from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)

    with app.app_context():
        try:
            # Import models to register them with SQLAlchemy
            from app import models

            # Create tables if they don't exist
            db.create_all()
            print("Database initialized successfully")
        except SQLAlchemyError as e:
            print(f"Database initialization error: {e}")
            raise


@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic commit/rollback"""
    try:
        yield db.session
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()
