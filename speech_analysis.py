sentence = "The quick brown fox jumps over the lazy dog."

import pyaudio
import wave
from google.cloud import speech_v1p1beta1 as speech
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv


def record_audio(filename, stop_recording):
    chunk = 1024
    sample_format = pyaudio.paInt16 
    channels = 1
    fs = 44100 

    p = pyaudio.PyAudio()
    frames = []

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    while not stop_recording.is_set():
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print('Finished recording')

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

import requests
import base64

def transcribe_audio_with_api_key(file_path, api_key):
    # Read the audio file
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    # Encode the audio file in base64
    audio_content = base64.b64encode(content).decode("utf-8")

    # Define the request payload
    payload = {
        "config": {
            "encoding": "LINEAR16",
            "languageCode": "en-US",
            "enableWordConfidence": True
        },
        "audio": {
            "content": audio_content
        }
    }

    # Define the API endpoint
    url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"

    # Make the request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        results = response.json().get('results', [])
        transcription_data = []
        for result in results:
            alternative = result['alternatives'][0]
            # print(f"Transcript: {alternative['transcript']}")
            # print("Word-level confidence:")
            word_confidences = []
            for word_info in alternative.get('words', []):
                # print(f"Word: {word_info['word']}, Confidence: {word_info['confidence']}")
                word_confidences.append({
                    "word": word_info['word'].lower(),
                    "confidence": word_info['confidence']
                })
            transcription_data.append({
                "transcript": alternative['transcript'].lower(),
                "word_confidences": word_confidences
            })
        
        # Return the transcription data as JSON
        return transcription_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return {"error": response.status_code, "message": response.text}


def analyze_transcription_with_gpt(transcription_data, original_sentence, openai_api_key):
    # Set the OpenAI API key
    # client = OpenAI(api_key=openai_api_key)

    # # Prepare the prompt for GPT-4o-mini
    prompt = (
        f"Original sentence: \"{original_sentence}\"\n"
        f"Transcription data: {transcription_data}\n"
        "Please analyze the transcription and identify any differences from the original sentence. For the user, pretend that you're not analyzing a transcription, but rather their speech itself."
        "Provide a simple and friendly explanation of what the user can improve in their pronunciation. "
        "Focus on specific words or sounds that need attention and suggest easy ways to practice them. Give them specific phonetic symbols to practice"
        "Don't worry about gramatical differences and focus ONLY on the phonetics."
        "Keep it short and concise, under 100 words. Write in plain text, not markdown."
    )
    
    client = OpenAI(api_key=openai_api_key)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract and return the analysis
    analysis = completion.choices[0].message.content.strip()
    return analysis

def generate_practice_paragraphs(api_key, count=1):
    client = OpenAI(api_key=api_key)
    paragraphs = []
    
    prompt = """Generate a paragraph that:
    1. Can be read in about 10s seconds. Keep it decently short.
    2. Contains challenging sounds and combinations that people with speech impediments may struggle with
    3. Focuses on common speech challenges like sibilants, plosives, and consonant clusters
    Make it natural and meaningful, not just a tongue twister."""
    
    for _ in range(count):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a speech therapy assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        paragraphs.append(completion.choices[0].message.content.strip().lower())
    
    return paragraphs