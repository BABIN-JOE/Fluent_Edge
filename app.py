import sounddevice as sd
import vosk
import queue
import json
import sys
import threading
import time
import os
import webbrowser
from flask import Flask, Response, render_template, jsonify, request
from flask_cors import CORS

# Import grammar and accuracy modules if available
try:
    from fluent_edge_core.grammar_checker import check_grammar
    from fluent_edge_core.accuracy_checker import calculate_accuracy
except ImportError:
    print("⚠️ WARNING: `fluent_edge_core` modules not found. Grammar & accuracy checking will be disabled.")
    check_grammar = lambda x: []
    calculate_accuracy = lambda x, y: 0.0

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load Vosk model
MODEL_PATH = "model/vosk-model-en-us-0.22-lgraph"
if not os.path.exists(MODEL_PATH):
    print(f"❌ ERROR: Vosk model not found in '{MODEL_PATH}'.")
    sys.exit(1)

model = vosk.Model(MODEL_PATH)

# Queue for audio data
q = queue.Queue()

# Store transcriptions and control flags
full_transcription = []
stop_recording_flag = threading.Event()
transcription_thread = None

# Callback function to capture audio data
def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio Input Error: {status}", file=sys.stderr)
    q.put(bytes(indata))

# Function to perform live transcription
def transcribe_audio():
    global full_transcription, stop_recording_flag

    full_transcription = []
    stop_recording_flag.clear()

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            print("🎤 Recording started... Speak now!")

            rec = vosk.KaldiRecognizer(model, 16000)

            while not stop_recording_flag.is_set():
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")

                        if text:
                            full_transcription.append(text)
                            print(f"📝 Live: {text}")

        print("\n🛑 Recording stopped!")
        process_final_transcription()

    except Exception as e:
        print(f"❌ ERROR: {e}")

# Function to process final transcription, grammar, and accuracy
def process_final_transcription():
    final_text = " ".join(full_transcription)
    print("\n📜 Full Transcription:")
    print(final_text)

    corrections = check_grammar(final_text)
    print("\n🔍 Grammar Corrections:")
    print(json.dumps(corrections, indent=2))

    accuracy = calculate_accuracy(final_text, corrections)
    print(f"\n🎯 Accuracy: {accuracy}%")

# Start Listening API
@app.route('/start', methods=['GET'])
def start_listening():
    global transcription_thread

    if transcription_thread and transcription_thread.is_alive():
        return jsonify({"status": "Already running"}), 400

    stop_recording_flag.clear()
    transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
    transcription_thread.start()
    return jsonify({"status": "Recording started"}), 200

# Stop Listening API
@app.route('/stop', methods=['GET'])
def stop_listening():
    stop_recording_flag.set()
    return jsonify({"status": "Stopping recording"}), 200

# Graceful shutdown
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/exit', methods=['GET'])
def exit_program():
    print("🛑 Shutting down the server...")
    os._exit(0)  # Forcefully terminate the program

@app.route('/goodbye')
def goodbye():
    return render_template("goodbye.html")

# Serve HTML page
@app.route('/')
def index():
    if not os.path.exists("templates/index.html"):
        return "❌ ERROR: 'index.html' not found. Make sure it exists in the 'templates/' folder.", 404
    return render_template("index.html")

# Streaming Transcription to Frontend
@app.route('/transcription')
def transcription_generator():
    def generate():
        previous_length = 0

        while not stop_recording_flag.is_set():
            if len(full_transcription) > previous_length:
                new_text = full_transcription[previous_length:]
                previous_length = len(full_transcription)
                print(f"Sending LIVE:: {new_text}")  # Debug log
                yield f"data: LIVE::{' '.join(new_text)}\n\n"
            time.sleep(0.5)

        # After stopping, send final transcription
        final_text = " ".join(full_transcription)
        print(f"Sending FULL_TRANSCRIPTION:: {final_text}")  # Debug log
        yield f"data: FULL_TRANSCRIPTION::{final_text}\n\n"

        # Send grammar errors as JSON
        corrections = check_grammar(final_text)
        print(f"Sending GRAMMAR_ERRORS:: {corrections}")  # Debug log
        yield f"data: GRAMMAR_ERRORS::{json.dumps(corrections)}\n\n"

        # Send accuracy
        accuracy = calculate_accuracy(final_text, corrections)
        print(f"Sending ACCURACY:: {accuracy}%")  # Debug log
        yield f"data: ACCURACY::{accuracy}%\n\n"

        # Exit the generator after sending final data
        return

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    print("🚀 Starting Flask server at http://127.0.0.1:5000/")
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=False, use_reloader=False, port=5000)
