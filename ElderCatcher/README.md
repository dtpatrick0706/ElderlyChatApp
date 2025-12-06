# Elderly Chat Application

A simple, accessible chat application built with Kivy and Google's Gemini AI, designed specifically for elderly users.

## Features

- Large, easy-to-read text
- Simple, intuitive interface
- Pre-configured AI assistant that understands it's talking to an elderly person
- Patient, warm, and helpful responses
- Clear, simple language

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure API Key

You have two options:

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# Windows CMD
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY=your-api-key-here
```

**Option B: Config File**
Create a file named `config.txt` in the same directory as `main.py` and paste your API key in it (just the key, nothing else).

### 4. Run the Application

```bash
python main.py
```

## Usage

1. Type your message in the text box at the bottom
2. Click "Send" or press Enter
3. The AI will respond in a friendly, patient manner
4. The conversation history is displayed in the chat area

## Notes

- The AI is pre-prompted to be patient, use simple language, and be understanding
- All text is displayed in large, readable fonts
- The interface is designed to be simple and non-intimidating

