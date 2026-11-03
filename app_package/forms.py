from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CompetitionForm(FlaskForm):
    name = StringField('Competition Name', validators=[DataRequired(), Length(max=150)])
    category = SelectField('Category', choices=[('Sports', 'Sports'), ('Academics', 'Academics'), ('Arts', 'Arts'), ('Quiz', 'Quiz')], validators=[DataRequired()])
    event_date = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired()])
    max_points = IntegerField('Max Points', validators=[DataRequired()])
    submit = SubmitField('Add Competition')

class StudentForm(FlaskForm):
    full_name = StringField('Student Full Name', validators=[DataRequired(), Length(max=100)])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=50)])
    class_section = StringField('Class / Section', validators=[DataRequired(), Length(max=20)])
    house_id = SelectField('House', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register Student')

class ResultForm(FlaskForm):
    competition_id = SelectField('Competition', coerce=int, validators=[DataRequired()])
    position = SelectField('Position', choices=[('1st', '1st Place (Winner)'), ('2nd', '2nd Place'), ('3rd', '3rd Place'), ('4th', '4th Place')], validators=[DataRequired()])
    house_id = SelectField('House', coerce=int, validators=[DataRequired()])
    points_awarded = IntegerField('Points Awarded', validators=[DataRequired()])
    submit = SubmitField('Record & Save Result')

class ParticipantAssignmentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    competition_id = SelectField('Competition', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Participant')