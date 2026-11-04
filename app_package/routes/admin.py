from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app_package.models import Admin, House, Competition, ParticipantRegistration, Result
from app_package import db
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, seamlessly bypass login page when clicking Admin Portal
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('admin_pass')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_bp.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('public_bp.index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    houses = House.query.all()
    competitions = Competition.query.order_by(Competition.id.desc()).all()
    return render_template('admin/dashboard.html', houses=houses, competitions=competitions)

@admin_bp.route('/students')
@login_required
def students():
    participants = ParticipantRegistration.query.all()
    houses = {h.id: h.name for h in House.query.all()}
    competitions = {c.id: c.name for c in Competition.query.all()}
    return render_template('admin/students.html', participants=participants, houses=houses, competitions=competitions)

@admin_bp.route('/register-student', methods=['GET', 'POST'])
@login_required
def register_student():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        roll_number = request.form.get('roll_number', 'N/A')
        house_id = request.form.get('house_id', type=int)
        competition_id = request.form.get('competition_id', type=int)

        if not student_name or not house_id or not competition_id:
            flash('All required fields must be filled for student registration.', 'danger')
            return redirect(url_for('admin_bp.register_student'))

        try:
            new_reg = ParticipantRegistration()
            if hasattr(new_reg, 'student_name'):
                new_reg.student_name = student_name.strip()
            elif hasattr(new_reg, 'name'):
                new_reg.name = student_name.strip()
            
            if hasattr(new_reg, 'roll_number'):
                new_reg.roll_number = roll_number.strip()
            elif hasattr(new_reg, 'student_id'):
                new_reg.student_id = roll_number.strip()
            
            if hasattr(new_reg, 'house_id'):
                new_reg.house_id = house_id
            if hasattr(new_reg, 'competition_id'):
                new_reg.competition_id = competition_id

            db.session.add(new_reg)
            db.session.commit()
            
            flash(f'Registration completed! Student "{student_name}" (Roll No: {roll_number}) successfully registered.', 'success')
            return redirect(url_for('admin_bp.register_student'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering student: {str(e)}', 'danger')

    houses = House.query.all()
    competitions = Competition.query.all()
    return render_template('admin/register_student.html', houses=houses, competitions=competitions)

@admin_bp.route('/declare-result', methods=['GET', 'POST'])
@login_required
def declare_result():
    if request.method == 'POST':
        competition_id = request.form.get('competition_id', type=int)
        house_id = request.form.get('house_id', type=int)
        position = request.form.get('position', type=int, default=1)

        if not competition_id or not house_id:
            flash('All fields are required to declare a result.', 'danger')
            return redirect(url_for('admin_bp.declare_result'))

        try:
            existing_result = Result.query.filter_by(competition_id=competition_id, position=position).first()
            if existing_result:
                flash(f'Position #{position} has already been awarded for this event! Please select an available position.', 'danger')
                return redirect(url_for('admin_bp.declare_result'))

            competition = Competition.query.get(competition_id)
            max_pts = competition.max_points if competition else 40
            
            # 4:3:2:1 proportional scale
            scale_weights = {1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
            weight = scale_weights.get(position, 0.1)
            points_awarded = int(max_pts * weight)

            new_result = Result(
                competition_id=competition_id,
                house_id=house_id,
                position=position,
                points_awarded=points_awarded
            )
            db.session.add(new_result)
            db.session.commit()

            house = House.query.get(house_id)
            house_name = house.name if house else "House"
            flash(f'Successfully awarded {points_awarded} points to {house_name} for Position #{position}!', 'success')
            return redirect(url_for('admin_bp.declare_result'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error declaring result: {str(e)}', 'danger')

    all_competitions = Competition.query.all()
    # Filter out competitions where all 4 positions are already taken
    competitions = []
    for comp in all_competitions:
        taken_count = Result.query.filter_by(competition_id=comp.id).count()
        if taken_count < 4:
            competitions.append(comp)

    # Pass taken positions mapping for dynamic client-side skipping
    taken_positions_map = {}
    for comp in all_competitions:
        taken_positions_map[comp.id] = [r.position for r in Result.query.filter_by(competition_id=comp.id).all()]

    houses = House.query.all()
    return render_template('admin/declare_result.html', competitions=competitions, all_competitions=all_competitions, houses=houses, taken_positions_map=taken_positions_map)

@admin_bp.route('/add-event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        date_str = request.form.get('date')
        max_points = request.form.get('max_points', type=int)
        
        if not name or not category or not date_str or not max_points:
            flash('All fields including date are required.', 'danger')
            return redirect(url_for('admin_bp.add_event'))
            
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if an event with exact same name and exact same date already exists
            existing_event = Competition.query.filter_by(name=name.strip(), event_date=parsed_date).first()
            if existing_event:
                flash(f'An event named "{name}" scheduled on {date_str} already exists! Please choose a different date if this is a separate occurrence.', 'danger')
                return redirect(url_for('admin_bp.add_event'))

            new_competition = Competition(
                name=name.strip(),
                category=category.strip(),
                event_date=parsed_date,
                max_points=max_points
            )
            db.session.add(new_competition)
            db.session.commit()
            flash(f'Competition "{name}" added successfully!', 'success')
            return redirect(url_for('admin_bp.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding event: {str(e)}', 'danger')
            
    return render_template('admin/add_event.html')