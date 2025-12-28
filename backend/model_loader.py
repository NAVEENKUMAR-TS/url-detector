import tensorflow as tf
import pickle
import numpy as np
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "url_deep_model.keras")
TOKENIZER_PATH = os.path.join(os.path.dirname(__file__), "models", "tokenizer.pickle")
MAX_LEN = 150
LABELS_MAP = {0: "Malicious", 1: "Safe"}

model = None
tokenizer = None

def load_ai_model():
    global model, tokenizer
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            print("Keras model loaded successfully.")
        else:
            print(f"Error: Model not found at {MODEL_PATH}")

        if os.path.exists(TOKENIZER_PATH):
            with open(TOKENIZER_PATH, "rb") as handle:
                tokenizer = pickle.load(handle)
            print("Tokenizer loaded successfully.")
        else:
            print(f"Error: Tokenizer not found at {TOKENIZER_PATH}")
            
    except Exception as e:
        print(f"Failed to load model/tokenizer: {e}")

def predict_url_safety(url: str):
    """
    Returns: (label, class_id, confidence)
    """
    if model is None or tokenizer is None:
        return "Unknown", -1, 0.0

    try:
        seq = tokenizer.texts_to_sequences([url])
        padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')
        pred = model.predict(padded)[0]
        cls = int(np.argmax(pred))
        conf = float(np.max(pred))
        return LABELS_MAP.get(cls, "Unknown"), cls, conf
    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Error", -1, 0.0

# Initialize on module load (or call explicitly in main startup)
load_ai_model()
