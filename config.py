import os

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-temp-dev-key'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'temp-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bookbuyback.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings for Contact Seller feature
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # Email domain restriction
    ALLOWED_EMAIL_DOMAIN = 'gus.pittstate.edu', 'pittstate.edu'

    # Image storage
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}