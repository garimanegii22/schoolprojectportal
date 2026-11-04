from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app_package.models import Admin, House, Competition, Student, ParticipantRegistration, Result
from app_package import db
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
        
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('admin_pass')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_bp.dashboard'))
        else:
            error_message = "Invalid username or password. Please check your spelling and try again."
            
    return render_template('admin/login.html', error_message=error_message)

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
    return render_template('admin/students.html', participants=participants)

@admin_bp.route('/register-student', methods=['GET', 'POST'])
@login_required
def register_student():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        roll_number = request.form.get('roll_number')
        house_id = request.form.get('house_id', type=int)
        competition_id = request.form.get('competition_id', type=int)

        if not student_name or not roll_number or not house_id or not competition_id:
            flash('All required fields must be filled for student registration.', 'danger')
            return redirect(url_for('admin_bp.register_student'))

        try:
            student = Student.query.filter_by(roll_number=roll_number.strip()).first()
            if not student:
                student = Student(
                    full_name=student_name.strip(),
                    roll_number=roll_number.strip(),
                    house_id=house_id,
                    class_section='N/A'
                )
                db.session.add(student)
                db.session.commit()

            existing_reg = ParticipantRegistration.query.filter_by(student_id=student.id, competition_id=competition_id).first()
            if existing_reg:
                flash(f'Student with Roll No {roll_number} is already registered for this event!', 'warning')
                return redirect(url_for('admin_bp.register_student'))

            new_reg = ParticipantRegistration(
                student_id=student.id,
                competition_id=competition_id
            )
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
        pos_int = request.form.get('position', type=int, default=1)
        
        pos_map = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th'}
        position_str = pos_map.get(pos_int, '1st')

        if not competition_id or not house_id:
            flash('All fields are required to declare a result.', 'danger')
            return redirect(url_for('admin_bp.declare_result'))

        try:
            # 1. Check if position is already taken
            existing_pos = Result.query.filter_by(competition_id=competition_id, position=position_str).first()
            if existing_pos:
                flash(f'Position #{pos_int} has already been awarded for this event!', 'danger')
                return redirect(url_for('admin_bp.declare_result'))

            # 2. Check if house already has ANY position in this competition
            existing_house = Result.query.filter_by(competition_id=competition_id, house_id=house_id).first()
            if existing_house:
                flash(f'This house has already been awarded Position #{existing_house.position} for this event! A house cannot receive multiple ranks in the same competition.', 'danger')
                return redirect(url_for('admin_bp.declare_result'))

            competition = Competition.query.get(competition_id)
            max_pts = competition.max_points if competition else 40
            
            scale_weights = {1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
            weight = scale_weights.get(pos_int, 0.1)
            points_awarded = int(max_pts * weight)

            new_result = Result(
                competition_id=competition_id,
                house_id=house_id,
                position=position_str,
                points_awarded=points_awarded
            )
            db.session.add(new_result)
            db.session.commit()

            house = House.query.get(house_id)
            house_name = house.name if house else "House"
            flash(f'Successfully awarded {points_awarded} points to {house_name} for Position #{pos_int}!', 'success')
            
            all_comps = Competition.query.all()
            return render_template('admin/declare_result.html', 
                                   competitions=[c for c in all_comps if Result.query.filter_by(competition_id=c.id).count() < 4], 
                                   all_competitions=all_comps, 
                                   houses=House.query.all(), 
                                   taken_positions_map={c.id: [int(r.position[0]) for r in Result.query.filter_by(competition_id=c.id).all()] for c in all_comps},
                                   taken_houses_map={c.id: [r.house_id for r in Result.query.filter_by(competition_id=c.id).all()] for c in all_comps},
                                   preselected_comp=competition_id)
        except Exception as e:
            db.session.rollback()
            flash(f'Error declaring result: {str(e)}', 'danger')

    all_competitions = Competition.query.all()
    competitions = [c for c in all_competitions if Result.query.filter_by(competition_id=c.id).count() < 4]
    taken_positions_map = {c.id: [int(r.position[0]) for r in Result.query.filter_by(competition_id=c.id).all()] for c in all_competitions}
    taken_houses_map = {c.id: [r.house_id for r in Result.query.filter_by(competition_id=c.id).all()] for c in all_competitions}
    houses = House.query.all()
    
    return render_template('admin/declare_result.html', competitions=competitions, all_competitions=all_competitions, houses=houses, taken_positions_map=taken_positions_map, taken_houses_map=taken_houses_map, preselected_comp=None)

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
            existing_event = Competition.query.filter_by(name=name.strip(), event_date=parsed_date).first()
            if existing_event:
                flash(f'An event named "{name}" scheduled on {date_str} already exists! Please choose a different date.', 'danger')
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