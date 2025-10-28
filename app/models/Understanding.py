from app import db
from datetime import datetime

class Understanding(db.Model):
    __tablename__ = 'understanding'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    strengths = db.Column(db.Text)
    improvement_areas = db.Column(db.Text)
    learning_pace = db.Column(db.String(50))
    motivation_factors = db.Column(db.Text)

    learning_style = db.Column(db.String(50))
    cognitive_level = db.Column(db.String(50))
    attention_span = db.Column(db.String(50))
    problem_solving_style = db.Column(db.String(50))
    recommended_learning_methods = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)