from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Blueprints
    from .blueprints.main.routes import bp as main_bp
    from .blueprints.auth.routes import bp as auth_bp
    from .blueprints.questions.routes import bp as questions_bp
    from .blueprints.questions.routes import bp as exams_bp
    
    # Resgistering Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(exams_bp)
    
    return app 