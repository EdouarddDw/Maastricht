from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)

# Basic Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_super_secret_key'

db = SQLAlchemy(app)

# ------------------------------------------------------------------------
# Association Table for Many-to-Many: A user can have multiple projects
# and a project can have multiple users
# ------------------------------------------------------------------------
employee_projects = db.Table(
    'employee_projects',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)

# ------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")
    
    # Personal info
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)

    # Hours worked (optional, if you also track in TimeLog)
    hours_worked = db.Column(db.Float, default=0.0)

    # Many-to-Many relationship with Projects
    projects = db.relationship(
        'Project',
        secondary=employee_projects,
        back_populates='users'
    )


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    total_hours = db.Column(db.Float, default=0.0)

    # Many-to-Many relationship back to Users
    users = db.relationship(
        'User',
        secondary=employee_projects,
        back_populates='projects'
    )


class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today)
    hours = db.Column(db.Float, default=0.0)

    # NEW: which project these hours are for
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project = db.relationship('Project')

    user = db.relationship('User', backref='time_logs')



# ------------------------------------------------------------------------
# Create a default admin user if none exists
# ------------------------------------------------------------------------
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = generate_password_hash("1234", method='pbkdf2:sha256')
        admin = User(username="admin", password=hashed_password, role="admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin / 1234")


# ------------------------------------------------------------------------
# Decorators
# ------------------------------------------------------------------------
def login_required(f):
    """Checks if user is logged in at all."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Checks if user is admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------------------------------------------------------
# Before first request, create tables and an admin user
# ------------------------------------------------------------------------
app_initialized = False

@app.before_request
def setup():
    global app_initialized
    if not app_initialized:
        db.create_all()
        create_admin()
        app_initialized = True

# ------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------

@app.route('/')
def home():
    """Public homepage: info, login, signup links."""
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route (both admin and employee)."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Logged in successfully!", "success")
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('manager_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup for new employees. (Admin can also create employees in manager area.)"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Choose another!", "danger")
            return redirect(url_for('signup'))

        # If it doesn't exist, proceed to create
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed, role='employee')
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been created. Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    """Simple logout route."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


# -----------------------
# EMPLOYEE AREA
# -----------------------
@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    # If user is admin, redirect to manager
    if session.get('role') == 'admin':
        return redirect(url_for('manager_dashboard'))
    
    user = User.query.get(session['user_id'])
    
    # Grab all logs for this user
    logs = TimeLog.query.filter_by(user_id=user.id).order_by(TimeLog.log_date.desc()).all()

    # Sum up hours across ALL logs
    total_logged_hours = sum(log.hours for log in logs)

    # ---------------- NEW: Summaries by Project ----------------
    # For each project that the user is assigned to, let's sum their hours.
    project_hours = {}
    for p in user.projects:
        logs_for_p = TimeLog.query.filter_by(user_id=user.id, project_id=p.id).all()
        total_p_hours = sum(log.hours for log in logs_for_p)
        project_hours[p] = total_p_hours

    # Pass 'project_hours' to the template so we can display hours for each project.
    return render_template(
        'employee_dashboard.html',
        user=user,
        logs=logs,
        total_logged_hours=total_logged_hours,
        project_hours=project_hours
    )


@app.route('/employee/log-hours', methods=['POST'])
@login_required
def employee_log_hours():
    """Process a new time log from an employee."""
    if session.get('role') == 'admin':
        return redirect(url_for('manager_dashboard'))
    
    user_id = session['user_id']
    hours = request.form.get('hours', 0)
    date_str = request.form.get('date')  # e.g. "2025-01-14"
    project_id = request.form.get('project_id')  # NEW: which project?

    # Basic date parsing
    if date_str:
        try:
            y, m, d = map(int, date_str.split('-'))
            log_date = date(y, m, d)
        except:
            log_date = date.today()
    else:
        log_date = date.today()

    # Convert hours to float
    hours_val = float(hours) if hours else 0.0

    # Create the new TimeLog with both user_id and project_id
    new_log = TimeLog(
        user_id=user_id, 
        project_id=project_id,  # store the chosen project
        log_date=log_date, 
        hours=hours_val
    )
    db.session.add(new_log)
    db.session.commit()

    flash("Hours logged successfully.", "success")
    return redirect(url_for('employee_dashboard'))



@app.route('/employee/edit-profile', methods=['GET', 'POST'])
@login_required
def employee_edit_profile():
    """Allows employee to update personal info (phone, address, etc.)."""
    if session.get('role') == 'admin':
        return redirect(url_for('manager_dashboard'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.phone = request.form['phone']
        user.address = request.form['address']
        birthdate_str = request.form['birthdate']  # e.g. "1990-05-20"
        if birthdate_str:
            y, m, d = map(int, birthdate_str.split('-'))
            user.birthdate = date(y, m, d)
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('employee_dashboard'))

    return render_template('employee_edit_profile.html', user=user)


# -----------------------
# MANAGER AREA
# -----------------------
@app.route('/manager/dashboard')
@admin_required
def manager_dashboard():
    """The manager's one-stop dashboard."""
    projects = Project.query.all()
    employees = User.query.filter(User.role != 'admin').all()

    # Hours by project: 
    # Instead of .any(), rely on TimeLog.project_id == p.id
    project_summaries = []
    for p in projects:
        # Only logs referencing this project_id
        logs_for_p = TimeLog.query.filter_by(project_id=p.id).all()
        total_p_hours = sum(log.hours for log in logs_for_p)
        project_summaries.append((p, total_p_hours))

    # Hours by employee:
    employee_summaries = []
    for emp in employees:
        logs_for_emp = TimeLog.query.filter_by(user_id=emp.id).all()
        total_e_hours = sum(log.hours for log in logs_for_emp)
        employee_summaries.append((emp, total_e_hours))

    return render_template('manager_dashboard.html',
                           projects=projects,
                           employees=employees,
                           project_summaries=project_summaries,
                           employee_summaries=employee_summaries)


@app.route('/manager/add-employee', methods=['GET','POST'])
@admin_required
def manager_add_employee():
    """Allows manager to create a new employee account quickly."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'employee')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Choose another!", "danger")
            return redirect(url_for('manager_add_employee'))
        
        # If it doesn't exist, proceed to create
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Employee created!", "success")
        return redirect(url_for('manager_dashboard'))
    
    return render_template('manager_add_employee.html')



@app.route('/manager/edit-employee/<int:user_id>', methods=['GET','POST'])
@admin_required
def manager_edit_employee(user_id):
    """Manager can edit an existing employee."""
    emp = User.query.get_or_404(user_id)
    projects = Project.query.all()

    if request.method == 'POST':
        emp.username = request.form['username']
        new_password = request.form['password']
        if new_password.strip():
            emp.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        emp.role = request.form.get('role', 'employee')

        # You could also let the manager assign multiple projects.
        # For a single project, you might do something different, but with many-to-many,
        # you'd typically have a multi-select or checkboxes.
        # Below is just a single project dropdown example:
        project_id = request.form.get('project_id')
        if project_id:
            # Clear existing
            emp.projects = []
            # Assign new one
            project = Project.query.get(project_id)
            if project:
                emp.projects.append(project)

        db.session.commit()
        flash("Employee updated!", "success")
        return redirect(url_for('manager_dashboard'))

    return render_template('manager_edit_employee.html', emp=emp, projects=projects)


@app.route('/manager/delete-employee/<int:user_id>', methods=['POST'])
@admin_required
def manager_delete_employee(user_id):
    if session['user_id'] == user_id:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for('manager_dashboard'))
    
    emp = User.query.get_or_404(user_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted.", "success")
    return redirect(url_for('manager_dashboard'))


@app.route('/manager/add-project', methods=['GET', 'POST'])
@admin_required
def manager_add_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_project = Project(name=name, description=description)
        db.session.add(new_project)
        db.session.commit()
        flash("Project created!", "success")
        return redirect(url_for('manager_dashboard'))
    return render_template('manager_add_project.html')


@app.route('/manager/edit-project/<int:project_id>', methods=['GET','POST'])
@admin_required
def manager_edit_project(project_id):
    proj = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        proj.name = request.form['name']
        proj.description = request.form['description']
        db.session.commit()
        flash("Project updated!", "success")
        return redirect(url_for('manager_dashboard'))
    return render_template('manager_edit_project.html', proj=proj)


@app.route('/manager/delete-project/<int:project_id>', methods=['POST'])
@admin_required
def manager_delete_project(project_id):
    proj = Project.query.get_or_404(project_id)
    db.session.delete(proj)
    db.session.commit()
    flash("Project deleted!", "success")
    return redirect(url_for('manager_dashboard'))


# Example of a route to assign multiple projects (optional)
@app.route('/manager/assign-projects/<int:user_id>', methods=['POST'])
@admin_required
def manager_assign_projects(user_id):
    """
    If you have a multi-select form for projects, you can assign many at once.
    Example usage in the template:
      <select name="project_ids" multiple>
          ...
      </select>
    """
    emp = User.query.get_or_404(user_id)
    selected_ids = request.form.getlist('project_ids')  # e.g. ['1', '3', '5']
    project_ids = [int(pid) for pid in selected_ids]

    # Clear the existing assignments
    emp.projects = []

    # Add each project
    for pid in project_ids:
        project = Project.query.get(pid)
        if project:
            emp.projects.append(project)

    db.session.commit()
    flash("Projects assigned!", "success")
    return redirect(url_for('manager_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
