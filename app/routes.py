from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, Task, Category
from app.database import db
from app.auth import token_required, generate_token, validate_user_credentials, register_user

api_bp = Blueprint('api', __name__)


# ==================== Authentication Routes ====================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400

        user, error = register_user(data['username'], data['email'], data['password'])

        if error:
            return jsonify({'error': error}), 400

        token = generate_token(user.id)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()

        if not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Missing username or password'}), 400

        user = validate_user_credentials(data['username'], data['password'])

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        token = generate_token(user.id)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current authenticated user"""
    return jsonify(current_user.to_dict()), 200


# ==================== Category Routes ====================

@api_bp.route('/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    """Create a new category"""
    try:
        data = request.get_json()

        if 'name' not in data:
            return jsonify({'error': 'Category name is required'}), 400

        # Check if category already exists
        if Category.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Category already exists'}), 400

        category = Category(
            name=data['name'],
            description=data.get('description'),
            color=data.get('color', '#3498db')
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/categories/<int:category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    """Get a specific category"""
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        return jsonify(category.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    """Update a category"""
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        data = request.get_json()

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']

        db.session.commit()

        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    """Delete a category"""
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({'message': 'Category deleted successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Task Routes ====================

@api_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    """Get all tasks for current user with optional filters"""
    try:
        query = Task.query.filter_by(user_id=current_user.id)

        # Apply filters from query parameters
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)

        priority = request.args.get('priority')
        if priority:
            query = query.filter_by(priority=priority)

        category_id = request.args.get('category_id')
        if category_id:
            query = query.filter_by(category_id=int(category_id))

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Sort
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        if hasattr(Task, sort_by):
            column = getattr(Task, sort_by)
            query = query.order_by(column.desc() if order == 'desc' else column.asc())

        # Execute query with pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'tasks': [task.to_dict() for task in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    """Get a specific task"""
    try:
        task = db.session.get(Task, task_id)

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        return jsonify(task.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    """Create a new task"""
    try:
        data = request.get_json()

        if 'title' not in data:
            return jsonify({'error': 'Task title is required'}), 400

        # Validate category if provided
        category_id = data.get('category_id')
        if category_id and not db.session.get(Category, category_id):
            return jsonify({'error': 'Category not found'}), 404

        task = Task(
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            category_id=category_id,
            user_id=current_user.id
        )

        # Parse due_date if provided
        if 'due_date' in data:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    """Update a task"""
    try:
        task = db.session.get(Task, task_id)

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        data = request.get_json()

        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            # Mark as completed if status is 'completed'
            if data['status'] == 'completed' and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif data['status'] != 'completed':
                task.completed_at = None
        if 'priority' in data:
            task.priority = data['priority']
        if 'category_id' in data:
            task.category_id = data['category_id']
        if 'due_date' in data:
            try:
                task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
            except ValueError:
                return jsonify({'error': 'Invalid due_date format'}), 400

        db.session.commit()

        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    """Delete a task"""
    try:
        task = db.session.get(Task, task_id)

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': 'Task deleted successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Statistics Route ====================

@api_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get task statistics for current user"""
    try:
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').count()
        in_progress_tasks = Task.query.filter_by(user_id=current_user.id, status='in_progress').count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').count()

        return jsonify({
            'total_tasks': total_tasks,
            'pending': pending_tasks,
            'in_progress': in_progress_tasks,
            'completed': completed_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
