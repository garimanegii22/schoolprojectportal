import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key_12345'
    
    # Force SQLite fallback unconditionally
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') if (os.environ.get('DATABASE_URL') and 'localhost' not in os.environ.get('DATABASE_URL')) else 'sqlite:///site.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_timeout': 20,
        'pool_pre_ping': True
    }