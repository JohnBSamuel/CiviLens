import numpy as np
from PIL import Image
import tensorflow as tf

# Load pre-trained model
def load_model():
    try:
        model = tf.keras.models.load_model('violation_model.h5')
        print("Model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocess image for model input
def preprocess_image(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# Predict violation type
def predict_violation(image_path, model):
    try:
        if model is None:
            return False, "Model not loaded"

        img_array = preprocess_image(image_path)
        if img_array is None:
            return False, "Error preprocessing image"

        predictions = model.predict(img_array)
        violation_classes = ['Red Light Jumping', 'No Parking', 'No Helmet']
        predicted_class = violation_classes[np.argmax(predictions)]

        confidence = np.max(predictions)
        if confidence > 0.8:
            return True, predicted_class
        else:
            return False, "Low confidence in prediction"
    except Exception as e:
        print(f"Error in prediction: {e}")
        return False, str(e)
