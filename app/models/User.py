from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(85), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    login_count = db.Column(db.Integer, default=0, nullable=False)
    last_login = db.Column(db.DateTime)
    last_assessment = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, lazy=True)
    understanding = db.relationship('Understanding', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def increment_login_count(self):
        if self.login_count is None:
            self.login_count = 0
        self.login_count += 1
        self.last_login = datetime.utcnow()
    
    def needs_reassessment(self):
        if self.login_count is None:
            return False
        return self.login_count > 0 and self.login_count % 10 == 0
    
    def __repr__(self):
        return f'<User {self.username}>'