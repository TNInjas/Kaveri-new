from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os

db = SQLAlchemy()
sess = Session()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Hello python')

    raw_db_url = os.environ.get('DATABASE_URL')
    if not raw_db_url:
        raw_db_url = 'postgresql://postgres:Tanaysoni@db.elzegnmjiviemrpcwzgm.supabase.co:5432/postgres'
    db_url = raw_db_url
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif db_url.startswith('postgresql://') and 'postgresql+psycopg2://' not in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    if 'sslmode=' not in db_url:
        separator = '&' if '?' in db_url else '?'
        db_url = f"{db_url}{separator}sslmode=require"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True

    db.init_app(app)
    sess.init_app(app)

    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app


def register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.assignment import ass_bp
    from app.routes.dashboard import dash_bp
    from app.routes.content import content_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ass_bp, url_prefix='/assessment')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')
    app.register_blueprint(content_bp, url_prefix='/content')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('intro.html')
