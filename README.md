# Speech Practice Buddy

A kid-friendly web application to help children practice their pronunciation and improve their speech. The application records the user's voice, transcribes it, and provides friendly feedback on how to improve pronunciation.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `keys.env` file in the root directory with your API keys:
```
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:
```bash
python app.py
```

5. Open your web browser and navigate to `http://localhost:5000`

## How to Use

1. Select a practice sentence from the dropdown menu
2. Click the "Start Recording" button
3. Read the sentence aloud (you have 5 seconds to read)
4. Wait for the analysis
5. Review your transcription and the friendly feedback
6. Practice the suggested improvements and try again!

## Requirements

- Python 3.7 or higher
- A microphone
- Google Cloud Speech-to-Text API key
- OpenAI API key

## Note

This is a basic implementation intended for local use. The application records audio for 5 seconds when you click the "Start Recording" button. Make sure your microphone is working and properly configured on your system. 