from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secure_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_house_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'admin_bp.login'
    login_manager.login_message_category = 'info'

    from app_package.routes.public import public_bp
    from app_package.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from app_package.models import Admin, House
        
        # 1. Ensure default admin user is seeded with 'houseportaladmin'
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('houseportaladmin')
            db.session.add(admin)
        else:
            admin.set_password('houseportaladmin')
            
        # 2. Ensure default houses are seeded so dropdowns are never empty
        default_houses = [
            {"name": "Blue", "emoji": "🔵", "display_color": "blue", "border_class": "border-blue-500", "glow_class": "glow-blue"},
            {"name": "Red", "emoji": "🔴", "display_color": "red", "border_class": "border-red-500", "glow_class": "glow-red"},
            {"name": "Green", "emoji": "🟢", "display_color": "green", "border_class": "border-emerald-500", "glow_class": "glow-green"},
            {"name": "Yellow", "emoji": "🟡", "display_color": "yellow", "border_class": "border-amber-500", "glow_class": "glow-yellow"}
        ]
        for h_data in default_houses:
            house = House.query.filter_by(name=h_data["name"]).first()
            if not house:
                db.session.add(House(**h_data))
                
        db.session.commit()

    return app