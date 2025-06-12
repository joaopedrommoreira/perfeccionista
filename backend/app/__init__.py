# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .models import db

def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    load_dotenv()
    
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    db_path = os.path.join(os.path.dirname(basedir), 'database.db')
    
    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    UPLOAD_FOLDER = 'uploads/avatars'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # --- NOVA CONFIGURAÇÃO DE CORS AQUI ---
    CORS(app, 
         resources={r"/api/*": {
             "origins": "http://localhost:3000",
             "methods": ["GET", "POST"],
             "allow_headers": ["Authorization", "Content-Type"]
         }}, 
         supports_credentials=True
    )
    
    db.init_app(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.main_bp)
        db.create_all()

    return app