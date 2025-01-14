from app import db, create_admin

# Create the application context
from app import app

with app.app_context():
    # Create all tables
    db.create_all()
    # Create the admin user
    create_admin()
    print("Database and admin user created successfully!")
