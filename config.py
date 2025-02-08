class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///civilians.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'
    SECRET_KEY = 'your-secret-key'
