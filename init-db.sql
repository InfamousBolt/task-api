-- Initialize database with default categories
-- This script runs automatically when the database container starts for the first time

-- Note: Tables are created by SQLAlchemy/Alembic, this just adds default data

-- Wait for tables to be created (handled by application startup)
-- Then insert default categories

DO $$
BEGIN
    -- Create default categories if the categories table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categories') THEN
        INSERT INTO categories (name, description, color, created_at)
        VALUES
            ('Work', 'Work-related tasks', '#3498db', NOW()),
            ('Personal', 'Personal tasks and errands', '#2ecc71', NOW()),
            ('Shopping', 'Shopping lists and purchases', '#e74c3c', NOW()),
            ('Health', 'Health and fitness goals', '#9b59b6', NOW()),
            ('Learning', 'Educational and learning tasks', '#f39c12', NOW())
        ON CONFLICT (name) DO NOTHING;
    END IF;
END $$;
