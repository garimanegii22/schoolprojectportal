from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app_package import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class House(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    display_color = db.Column(db.String(50), nullable=False)
    border_class = db.Column(db.String(50), nullable=False)
    glow_class = db.Column(db.String(50), nullable=False)

    students = db.relationship('Student', backref='house', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='house', lazy=True, cascade='all, delete-orphan')

    @property
    def total_points(self):
        """Calculates total points dynamically from recorded results."""
        return sum(result.points_awarded for result in self.results)

    @property
    def total_wins(self):
        """Calculates total 1st place wins dynamically."""
        return sum(1 for result in self.results if result.position == '1st')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    class_section = db.Column(db.String(20), nullable=True, default='N/A')  # Optional to prevent registration blocks
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)

    registrations = db.relationship('ParticipantRegistration', backref='student', lazy=True, cascade='all, delete-orphan')

class Competition(db.Model):
    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Sports, Academics, Arts, Quiz
    event_date = db.Column(db.Date, nullable=False)
    max_points = db.Column(db.Integer, default=10, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    registrations = db.relationship('ParticipantRegistration', backref='competition', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='competition', lazy=True, cascade='all, delete-orphan')

class ParticipantRegistration(db.Model):
    __tablename__ = 'participant_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'competition_id', name='uq_student_competition'),
    )

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    position = db.Column(db.String(10), nullable=False)  # '1st', '2nd', '3rd', '4th'
    points_awarded = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('competition_id', 'position', name='uq_competition_position'),
    )