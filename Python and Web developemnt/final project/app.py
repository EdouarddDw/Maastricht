from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for session and flash messages
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")  # Default role is employee


# Helper function to create the admin user
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = generate_password_hash("1234", method='pbkdf2:sha256')
        admin = User(username="admin", password=hashed_password, role="admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")


# Run this function when the application starts
@app.before_request
def initialize():
    if not hasattr(app, 'is_initialized'):
        create_admin()
        app.is_initialized = True  # Set a flag to prevent running again


# Home/sign-in route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            flash('Sign-in successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to a dashboard or another page
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('signin.html')


# Dashboard route (after successful sign-in)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Placeholder for a dashboard page


# Sign-up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # New users automatically get the "employee" role
        new_user = User(username=username, password=hashed_password, role="employee")
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html')


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

#start of coding the dahsboard

# Key functionalities checklist:
#admin dashboard (with more accsees to edit everything) and employee pannel
#admin can add new employee
#admin can delete employee
#admin can edit employee
#admin can see all employees
#admin has the opportunity to create other admuins or to change the privilages of the employees
#employee can see other employees but can't edit them
#each employee is assigned to a project
#admin can see all projects and modify them and wich employee is assigned to them

# functionalities summary
#admin can see all employees
#admin can see all projects
#admin can add new employee
#admin can delete employee
#admin can edit employee
#admin can see all employees
#admin can see all projects
#admin can see number of hours worked by each employee
#admin can see number of hours worked by each project
#admin can see number of hours worked by each employee on each project

#design choices
#pie charts or something like that
#each employee has a profile page
#each project has a profile page
 
