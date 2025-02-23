from flask import Flask, render_template, request, jsonify
import os
from speech_analysis import record_audio, transcribe_audio_with_api_key, analyze_transcription_with_gpt
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv('keys.env')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Sample sentences for practice
PRACTICE_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "Peter Piper picked a peck of pickled peppers.",
    "How much wood would a woodchuck chuck?",
    "Red leather, yellow leather."
]

@app.route('/')
def index():
    return render_template('index.html', sentences=PRACTICE_SENTENCES)

@app.route('/analyze', methods=['POST'])
def analyze_speech():
    try:
        # Get the selected sentence from the request
        sentence = request.form.get('sentence')
        
        # Record audio (5 seconds duration)
        audio_file = "temp_recording.wav"
        record_audio(audio_file, duration=5)
        
        # Transcribe the audio
        transcription_data = transcribe_audio_with_api_key(audio_file, GOOGLE_API_KEY)
        
        # Analyze the transcription
        analysis = analyze_transcription_with_gpt(transcription_data, sentence, OPENAI_API_KEY)
        
        # Clean up the temporary audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        return jsonify({
            'success': True,
            'transcription': transcription_data[0]['transcript'] if transcription_data else "",
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 