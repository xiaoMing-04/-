from firebase_admin import credentials, initialize_app
import firebase_admin
import os
def firebase_config():
    if not firebase_admin._apps:
        try:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cred_path = os.path.join(BASE_DIR, 'firebase_config.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firestore initialized successfully.")
        except Exception as e:
            print(f"Error initializing Firestore: {e}")