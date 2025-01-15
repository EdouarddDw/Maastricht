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

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    # total_hours is optional if you plan to sum from TimeLog or hours_worked in user
    total_hours = db.Column(db.Float, default=0.0)


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

    # If each user only has one project:
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project = db.relationship('Project', backref='employees')

    # We can keep hours_worked or rely on TimeLog
    hours_worked = db.Column(db.Float, default=0.0)


class TimeLog(db.Model):
    """
    Logs daily or weekly hours for an employee.
    Summations of these logs can be used to see total hours per user or per project.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today)  # default to "today"
    hours = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref='time_logs')


# Create a default admin user if none exists
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = generate_password_hash("1234", method='pbkdf2:sha256')
        admin = User(username="admin", password=hashed_password, role="admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin / 1234")


# Decorators
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

# Use a global flag so setup runs only once
app_initialized = False

@app.before_request
def setup():
    global app_initialized
    if not app_initialized:
        db.create_all()
        create_admin()
        app_initialized = True


# Routes

@app.route('/')
def home():
    """
    Public homepage. You can show info about who developed it, the year, etc.
    Provide links to Login/Signup.
    """
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
    """Signup for new employees. (Admins can create employees in manager area, too.)"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password, method='pbkdf2:sha256')

        # Create user with default role=employee
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
    # If user is admin, redirect
    if session.get('role') == 'admin':
        return redirect(url_for('manager_dashboard'))
    
    user = User.query.get(session['user_id'])
    
    # Grab logs for that user
    logs = TimeLog.query.filter_by(user_id=user.id).order_by(TimeLog.log_date.desc()).all()
    total_logged_hours = sum(log.hours for log in logs)

    # Pass them to the template
    return render_template(
        'employee_dashboard.html',
        user=user,
        logs=logs,
        total_logged_hours=total_logged_hours
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

    # Basic date parsing
    if date_str:
        try:
            y, m, d = map(int, date_str.split('-'))
            log_date = date(y, m, d)
        except:
            log_date = date.today()
    else:
        log_date = date.today()

    new_log = TimeLog(user_id=user_id, log_date=log_date, hours=float(hours))
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
    """
    The manager's one-stop dashboard.
    """
    projects = Project.query.all()
    employees = User.query.filter(User.role != 'admin').all()

    # Hours by project:
    project_summaries = []
    for p in projects:
        logs_for_p = db.session.query(TimeLog).join(User).filter(User.project_id==p.id).all()
        total_p_hours = sum(log.hours for log in logs_for_p)
        project_summaries.append((p, total_p_hours))

    # Hours by employee:
    employee_summaries = []
    for emp in employees:
        logs_for_emp = TimeLog.query.filter_by(user_id=emp.id).all()
        total_e_hours = sum(l.hours for l in logs_for_emp)
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
        
        project_id = request.form.get('project_id', '')
        if project_id == 'None':
            emp.project_id = None
        elif project_id.isdigit():
            emp.project_id = int(project_id)

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


if __name__ == '__main__':
    app.run(debug=True)
