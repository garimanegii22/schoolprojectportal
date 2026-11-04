import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_school_key_2026'
    
    # Use cloud PostgreSQL if provided; otherwise fallback to local SQLite
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Performance tweaking
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }