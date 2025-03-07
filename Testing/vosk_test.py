from vosk import Model, KaldiRecognizer
import os

model_path = os.path.abspath("model")  # Use absolute path
if not os.path.exists(model_path):
    print("Model path does not exist:", model_path)
else:
    model = Model(model_path)
    print("Model loaded successfully!")
