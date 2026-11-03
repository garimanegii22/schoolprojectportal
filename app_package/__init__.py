import os
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin_bp.login'
login_manager.login_message_category = 'info'

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    # Import and register Blueprints
    from app_package.routes.public import public_bp
    from app_package.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # CLI Command to create initial admin user easily
    @app.cli.command("create-admin")
    def create_admin_command():
        """Creates an initial administrator account via terminal command."""
        from app_package.models import Admin
        import getpass
        
        username = input("Enter admin username: ").strip()
        if Admin.query.filter_by(username=username).first():
            print(f"Error: Admin '{username}' already exists!")
            return
            
        password = getpass.getpass("Enter admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Error: Passwords do not match!")
            return
            
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Success: Administrator '{username}' created successfully!")

    with app.app_context():
        db.create_all()
	db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        db.create_all()
        from app_package.models import Admin
        from werkzeug.security import generate_password_hash
        
        # Automatically create a default admin if none exists
        if not Admin.query.first():
            hashed_password = generate_password_hash('admin123')
            # Adjust 'username' or 'password' field names if your Admin model uses different names
            admin_user = Admin(username='admin', password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
        # Seed default houses if none exist
        from app_package.models import House
        if House.query.count() == 0:
            default_houses = [
                {"name": "Blue", "emoji": "🔵", "display_color": "text-blue-400", "border_class": "border-blue-500/30", "glow_class": "glow-blue"},
                {"name": "Red", "emoji": "🔴", "display_color": "text-red-400", "border_class": "border-red-500/30", "glow_class": "glow-red"},
                {"name": "Green", "emoji": "🟢", "display_color": "text-emerald-400", "border_class": "border-emerald-500/30", "glow_class": "glow-green"},
                {"name": "Yellow", "emoji": "🟡", "display_color": "text-amber-400", "border_class": "border-amber-500/30", "glow_class": "glow-yellow"}
            ]
            for h in default_houses:
                house = House(name=h["name"], emoji=h["emoji"], display_color=h["display_color"], border_class=h["border_class"], glow_class=h["glow_class"])
                db.session.add(house)
            db.session.commit()
            print("Default school houses seeded successfully.")

    return app