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
            # 1. Find or create the Student entity
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

            # 2. Register student for the competition
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
        
        # Map integer position (1, 2, 3, 4) to model string values ('1st', '2nd', '3rd', '4th')
        pos_map = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th'}
        position_str = pos_map.get(pos_int, '1st')

        if not competition_id or not house_id:
            flash('All fields are required to declare a result.', 'danger')
            return redirect(url_for('admin_bp.declare_result'))

        try:
            existing_result = Result.query.filter_by(competition_id=competition_id, position=position_str).first()
            if existing_result:
                flash(f'Position #{pos_int} has already been awarded for this event!', 'danger')
                return redirect(url_for('admin_bp.declare_result'))

            competition = Competition.query.get(competition_id)
            max_pts = competition.max_points if competition else 40
            
            # 4:3:2:1 proportional scale weights
            scale_weights = {1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
            weight = scale_weights.get(pos_int, 0.1)
            points_awarded = int(max_pts * weight)

            new_result = Result(
                competition_id=competition_id,
                house_id=house_id,
                position=position_str,  # Saved as '1st', '2nd', etc.
                points_awarded=points_awarded
            )
            db.session.add(new_result)
            db.session.commit()

            house = House.query.get(house_id)
            house_name = house.name if house else "House"
            flash(f'Successfully awarded {points_awarded} points to {house_name} for Position #{pos_int}!', 'success')
            
            return render_template('admin/declare_result.html', 
                                   competitions=[c for c in Competition.query.all() if Result.query.filter_by(competition_id=c.id).count() < 4], 
                                   all_competitions=Competition.query.all(), 
                                   houses=House.query.all(), 
                                   taken_positions_map={c.id: [int(r.position[0]) for r in Result.query.filter_by(competition_id=c.id).all()] for c in Competition.query.all()},
                                   preselected_comp=competition_id)
        except Exception as e:
            db.session.rollback()
            flash(f'Error declaring result: {str(e)}', 'danger')

    all_competitions = Competition.query.all()
    competitions = [c for c in all_competitions if Result.query.filter_by(competition_id=c.id).count() < 4]
    taken_positions_map = {c.id: [int(r.position[0]) for r in Result.query.filter_by(competition_id=c.id).all()] for c in all_competitions}
    houses = House.query.all()
    
    return render_template('admin/declare_result.html', competitions=competitions, all_competitions=all_competitions, houses=houses, taken_positions_map=taken_positions_map, preselected_comp=None)