from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app_package import db
from app_package.models import Admin, House, Student, Competition, ParticipantRegistration, Result
from app_package.forms import LoginForm, CompetitionForm, StudentForm, ResultForm, ParticipantAssignmentForm

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash('Successfully logged in as administrator.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_bp.index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    student_count = Student.query.count()
    comp_count = Competition.query.filter_by(is_archived=False).all()
    results_count = Result.query.count()
    houses = House.query.all()
    sorted_houses = sorted(houses, key=lambda h: (h.total_points, h.total_wins), reverse=True)
    
    return render_template('admin/dashboard.html', 
                           student_count=student_count, 
                           comp_count=len(comp_count), 
                           results_count=results_count, 
                           houses=sorted_houses)

@admin_bp.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    form = StudentForm()
    form.house_id.choices = [(h.id, f"{h.emoji} {h.name} House") for h in House.query.all()]
    
    if form.validate_on_submit():
        existing_student = Student.query.filter_by(roll_number=form.roll_number.data).first()
        if existing_student:
            flash(f'Roll Number {form.roll_number.data} is already registered to {existing_student.full_name}.', 'danger')
        else:
            student = Student(
                full_name=form.full_name.data,
                roll_number=form.roll_number.data,
                class_section=form.class_section.data,
                house_id=form.house_id.data
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student {student.full_name} registered successfully!', 'success')
            return redirect(url_for('admin_bp.students'))
            
    all_students = Student.query.all()
    return render_template('admin/students.html', form=form, students=all_students)

@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student record for {name} deleted.', 'info')
    return redirect(url_for('admin_bp.students'))

@admin_bp.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    form = CompetitionForm()
    if form.validate_on_submit():
        existing = Competition.query.filter_by(name=form.name.data).first()
        if existing:
            flash(f'Competition "{form.name.data}" already exists.', 'danger')
        else:
            comp = Competition(
                name=form.name.data,
                category=form.category.data,
                event_date=form.event_date.data,
                max_points=form.max_points.data
            )
            db.session.add(comp)
            db.session.commit()
            flash(f'Competition "{comp.name}" created successfully!', 'success')
            return redirect(url_for('admin_bp.events'))
            
    all_events = Competition.query.order_by(Competition.event_date.desc()).all()
    return render_template('admin/events.html', form=form, events=all_events)

@admin_bp.route('/events/archive/<int:event_id>', methods=['POST'])
@login_required
def archive_event(event_id):
    event = Competition.query.get_or_404(event_id)
    event.is_archived = not event.is_archived
    db.session.commit()
    status = "archived" if event.is_archived else "restored"
    flash(f'Competition "{event.name}" has been {status}.', 'info')
    return redirect(url_for('admin_bp.events'))

@admin_bp.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    result_form = ResultForm()
    assign_form = ParticipantAssignmentForm()
    
    # Populate dropdown selections dynamically
    competitions = Competition.query.filter_by(is_archived=False).all()
    houses = House.query.all()
    students = Student.query.all()
    
    result_form.competition_id.choices = [(c.id, f"{c.name} ({c.category})") for c in competitions]
    result_form.house_id.choices = [(h.id, f"{h.emoji} {h.name} House") for h in houses]
    
    assign_form.student_id.choices = [(s.id, f"{s.full_name} ({s.roll_number}) - {s.house.name} House") for s in students]
    assign_form.competition_id.choices = [(c.id, c.name) for c in competitions]
    
    if result_form.validate_on_submit() and 'submit_result' in request.form:
        # Prevent duplicate position entries for the same competition
        existing_result = Result.query.filter_by(
            competition_id=result_form.competition_id.data,
            position=result_form.position.data
        ).first()
        
        if existing_result:
            flash(f'A result for position {result_form.position.data} in this competition already exists.', 'danger')
        else:
            res = Result(
                competition_id=result_form.competition_id.data,
                house_id=result_form.house_id.data,
                position=result_form.position.data,
                points_awarded=result_form.points_awarded.data
            )
            db.session.add(res)
            db.session.commit()
            flash('Podium result recorded and saved to MySQL!', 'success')
            return redirect(url_for('admin_bp.results'))

    all_results = Result.query.order_by(Result.id.desc()).all()
    registrations = ParticipantRegistration.query.order_by(ParticipantRegistration.id.desc()).all()
    
    return render_template('admin/results.html', 
                           result_form=result_form, 
                           assign_form=assign_form, 
                           results=all_results, 
                           registrations=registrations)

@admin_bp.route('/results/assign', methods=['POST'])
@login_required
def assign_participant():
    assign_form = ParticipantAssignmentForm()
    students = Student.query.all()
    competitions = Competition.query.filter_by(is_archived=False).all()
    assign_form.student_id.choices = [(s.id, s.full_name) for s in students]
    assign_form.competition_id.choices = [(c.id, c.name) for c in competitions]
    
    if assign_form.validate_on_submit():
        existing_reg = ParticipantRegistration.query.filter_by(
            student_id=assign_form.student_id.data,
            competition_id=assign_form.competition_id.data
        ).first()
        
        if existing_reg:
            flash('Student is already registered for this competition.', 'warning')
        else:
            reg = ParticipantRegistration(
                student_id=assign_form.student_id.data,
                competition_id=assign_form.competition_id.data
            )
            db.session.add(reg)
            db.session.commit()
            flash('Student assigned to competition successfully.', 'success')
            
    return redirect(url_for('admin_bp.results'))

@admin_bp.route('/results/delete/<int:result_id>', methods=['POST'])
@login_required
def delete_result(result_id):
    res = Result.query.get_or_404(result_id)
    db.session.delete(res)
    db.session.commit()
    flash('Result deleted successfully. House standings updated.', 'info')
    return redirect(url_for('admin_bp.results'))