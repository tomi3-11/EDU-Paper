from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120))
    role = db.Column(db.String(32), default="teacher") # teacher / school_admin / super_admin
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    school = db.relationship('School')
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)
    

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    class_level = db.Column(db.String(64))
    term = db.Column(db.String)
    dusration_mins = db.Column(db.Integer)
    # created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_exam_owner'), nullable=False)  # new
    
    owner = db.relationship('User', backref='exams')  # optional, makes it easier
    
    items = db.relationship('ExamItem', backref='exam', cascade='all, delete-orphan', order_by="ExamItem.order")
    
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(32), nullable=False) # MCQs, True or False, SA, Essay, Tick or cross
    text = db.Column(db.Text, nullable=False)
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    options = db.relationship('AnswerOption', backref='question', cascade='all, delete-orphan')
    
    
class AnswerOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    label = db.Column(db.String(4)) # A, B, C, D ...
    
    
class ExamItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    order = db.Column(db.Integer, default=1)
    
    question = db.relationship('Question')