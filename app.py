from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Complaint
from utils import load_model, allowed_file, preprocess_image, predict_violation
import os
import uuid

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config.Config')

# Initialize the database
db.init_app(app)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the AI model
model = load_model()

# Serve the front-end HTML file
@app.route('/')
def index():
    return send_from_directory('.', 'index2.html')

# Health check route to ensure server is running
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'running', 'message': 'Server is active'}), 200

# User registration endpoint
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        aadhaar_number = data.get('aadhaar_number')
        pin_code = data.get('pin_code')

        # Validate Aadhaar and Pin Code
        if not aadhaar_number or not pin_code:
            return jsonify({'error': 'Aadhaar number and pin code are required'}), 400
        if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
            return jsonify({'error': 'Invalid Aadhaar number'}), 400
        if len(pin_code) != 6 or not pin_code.isdigit():
            return jsonify({'error': 'Invalid pin code'}), 400

        # Check if user already exists
        if User.query.filter_by(aadhaar_number=aadhaar_number).first():
            return jsonify({'error': 'Aadhaar number already registered'}), 400

        # Register new user
        user = User(aadhaar_number=aadhaar_number, pin_code=pin_code)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# File upload and violation reporting endpoint
@app.route('/report', methods=['POST'])
def report_violation():
    try:
        user_id = request.form.get('user_id')
        location = request.form.get('location')
        file = request.files.get('file')

        # Validate input
        if not user_id or not location or not file:
            return jsonify({'error': 'All fields are required'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(file_path)

        # Predict violation type
        validated, prediction = predict_violation(file_path, model)

        if validated:
            # Create a new complaint
            complaint = Complaint(
                user_id=user_id,
                file_path=file_path,
                violation_type=prediction,
                location=location
            )
            user.credits += 10  # Reward user with credits
            db.session.add(complaint)
            db.session.commit()

            return jsonify({
                'message': 'Complaint submitted successfully',
                'complaint_id': complaint.id,
                'predicted_violation': prediction,
                'credits': user.credits
            }), 201
        else:
            return jsonify({'error': f'Violation could not be validated: {prediction}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Reward credits endpoint
@app.route('/rewards/<int:user_id>', methods=['GET'])
def get_rewards(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user_id': user.id, 'credits': user.credits})
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Ensure database tables are created before running
with app.app_context():
    db.create_all()

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
