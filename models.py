from datetime import datetime  # Import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    credits = db.Column(db.Integer, default=0)

    # Relationship with Complaints
    complaints = db.relationship('Complaint', backref='user', lazy=True)

# Define the Complaint model
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    violation_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Use datetime.utcnow() for the default value

    # Optional: You can define other methods or properties here if needed for your app
