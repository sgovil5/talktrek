from flask import Flask, render_template, request, jsonify
import os
from speech_analysis import record_audio, transcribe_audio_with_api_key, analyze_transcription_with_gpt, generate_practice_paragraphs
from dotenv import load_dotenv
from threading import Thread, Event

app = Flask(__name__)

# Load environment variables
load_dotenv('keys.env')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Generate the practice paragraphs when the app starts
PRACTICE_SENTENCES = generate_practice_paragraphs(OPENAI_API_KEY)


recording_thread = None
stop_event = Event()

@app.route('/')
def index():
    return render_template('index.html', sentences=PRACTICE_SENTENCES)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording_thread, stop_event
    stop_event.clear()
    recording_thread = Thread(target=record_audio, args=("temp_recording.wav", stop_event))
    recording_thread.start()
    return jsonify({'success': True})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global stop_event, recording_thread

    try:
        # Signal the recording to stop
        stop_event.set()
        if recording_thread:
            recording_thread.join()
        
        # Get the selected sentence from the request
        sentence = request.form.get('sentence')
        
        # Transcribe the audio
        transcription_data = transcribe_audio_with_api_key("temp_recording.wav", GOOGLE_API_KEY)
        
        # Analyze the transcription
        analysis = analyze_transcription_with_gpt(transcription_data, sentence.lower(), OPENAI_API_KEY)
        
        # Clean up the temporary audio file
        if os.path.exists("temp_recording.wav"):
            os.remove("temp_recording.wav")
        
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

@app.route('/generate_practice_paragraphs', methods=['POST'])
def generate_practice_paragraphs_route():
    try:
        # Generate new practice paragraphs
        new_sentences = generate_practice_paragraphs(OPENAI_API_KEY)
        new_sentence = new_sentences[0] if new_sentences else ""

        return jsonify({
            'success': True,
            'newSentence': new_sentence
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 