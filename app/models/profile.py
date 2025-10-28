from app import db
from datetime import datetime

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    Q1_answer = db.Column(db.String(250), nullable=False, unique=False)
    Q2_answer = db.Column(db.String(250), nullable=False, unique=False)
    Q3_answer = db.Column(db.String(250), nullable=False, unique=False)
    Q4_answer = db.Column(db.String(250), nullable=False, unique=False)
    Q5_answer = db.Column(db.String(250), nullable=False, unique=False)
    Q6_answer = db.Column(db.String(250), nullable=False, unique=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Profile for User {self.user_id}>'