from app import app, db

# Create the application context
with app.app_context():
    db.create_all()
    print("Database created successfully!")
