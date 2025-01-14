from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for session and flash messages
db = SQLAlchemy(app)

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    total_hours = db.Column(db.Float, default=0.0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")  # Default role is employee
    hours_worked = db.Column(db.Float, default=0.0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project = db.relationship('Project', backref='employees')


# Helper function to create the admin user
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = generate_password_hash("1234", method='pbkdf2:sha256')
        admin = User(username="admin", password=hashed_password, role="admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Run this function when the application starts
@app.before_request
def initialize():
    if not hasattr(app, 'is_initialized'):
        create_admin()
        app.is_initialized = True  # Prevents multiple runs

# Home/sign-in route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Store user info in session for role checking
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Sign-in successful!', 'success')

            # If the user is admin, redirect to admin dashboard
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                # Otherwise, direct them to the employee dashboard
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('signin.html')

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    employees = User.query.filter_by(role="employee").all()
    projects = Project.query.all()
    return render_template('admin_dashboard.html',
                           employees=employees,
                           projects=projects)

# Dashboard route (for employees)
@app.route('/dashboard')
def dashboard():
    # Guard check: if no user is logged in, redirect or show an error
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    current_user = User.query.get(user_id)

    # Render the dashboard for this user
    return render_template('dashboard.html', current_user=current_user)

# View all projects (generic route - not admin-restricted)
@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

# Add new employee (Admin only)
@app.route('/add-employee', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_employee = User(username=username, password=hashed_password, role="employee")
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_employee.html')

# Edit employee (Admin only)
@app.route('/edit-employee/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_employee(user_id):
    employee = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        employee.username = new_username
        if new_password.strip():
            # Only update if a new password was provided
            employee.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees'))
    
    return render_template('edit_employee.html', employee=employee)

# Sign-up route (for non-admins to create accounts)
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

# Manage employees (Admin only)
@app.route('/employees')
@admin_required
def employees():
    employee_list = User.query.filter_by(role="employee").all()
    return render_template('employees.html', employees=employee_list)

# Manage projects (Admin only)
@app.route('/admin-projects')
@admin_required
def admin_projects():
    projects = Project.query.all()
    return render_template('admin_projects.html', projects=projects)

# Edit a project (Admin only)
@app.route('/edit-project/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        project.total_hours = float(request.form['total_hours']) if request.form['total_hours'] else project.total_hours
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('edit_project.html', project=project)

# Add a new project (Admin only)
@app.route('/add-project', methods=['GET', 'POST'])
@admin_required
def add_project():
    if request.method == 'POST':
        project_name = request.form['name']
        project_description = request.form['description']
        total_hours = request.form.get('total_hours', 0)

        # Create a new Project object
        new_project = Project(
            name=project_name,
            description=project_description,
            total_hours=float(total_hours) if total_hours else 0.0
        )
        db.session.add(new_project)
        db.session.commit()

        flash('New project added successfully!', 'success')
        return redirect(url_for('admin_projects'))

    return render_template('add_project.html')

# Delete a project (Admin only)
@app.route('/delete-project/<int:project_id>', methods=['POST'])
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))




@app.route('/delete-employee/<int:user_id>', methods=['POST'])
@admin_required
def delete_employee(user_id):
    # (Optional) prevent deleting your own admin account, etc.
    # if session.get('user_id') == user_id:
    #     flash('You cannot delete your own account.', 'danger')
    #     return redirect(url_for('employees'))

    employee = User.query.get_or_404(user_id)
    db.session.delete(employee)
    db.session.commit()

    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('employees'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
