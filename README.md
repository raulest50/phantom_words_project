# Phantom Words Dashboard

An interactive dashboard created with Dash to demonstrate the Phantom Words effect.

## What are Phantom Words?

Phantom words are an auditory illusion where your brain perceives words that aren't actually present in the audio. This happens when the same sound is played in both ears but with a slight delay between them. The brain tries to make sense of these overlapping sounds, creating the perception of words or phrases that don't exist in the original audio.

## Features

- Single-page dashboard with a light blue header
- Responsive design using Dash Bootstrap Components
- Audio file upload with validation (file type and size)
- Delay control to adjust the time difference between left and right audio channels
- Loop control to set how many times the audio repeats
- Client-side audio processing using Web Audio API

## Installation

This project uses Poetry for dependency management. Make sure you have Poetry installed on your system.

```bash
# Install Poetry (if not already installed)
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Install dependencies
poetry install
```

## Running the Dashboard

There are two ways to run the dashboard:

### Method 1: Using Poetry Run

```bash
# Run the dashboard directly using Poetry
poetry run dashboard
```

### Method 2: Using Python

```bash
# Activate the virtual environment
poetry shell

# Run the application
python run.py
```

The dashboard will be available at http://localhost:8050 in your web browser.

## How to Use

1. **Upload an Audio File**: Click on the upload area to select an audio file (MP3, WAV, OGG, or M4A) that is less than 5MB in size.
2. **Adjust the Delay**: Use the slider to set the delay (in milliseconds) between the left and right audio channels. A typical value is around 200ms.
3. **Set Loop Count**: Specify how many times you want the audio to repeat using the number input.
4. **Play the Audio**: Click the "Play Audio" button to start playback. The audio will play normally in the right channel and with the specified delay in the left channel.
5. **Listen for Phantom Words**: As you listen, your brain will try to make sense of the overlapping sounds, potentially creating the perception of words or phrases that aren't actually in the audio.

## Project Structure

```
phantomwords/
├── src/
│   ├── assets/
│   │   └── audio_processor.js  # Client-side JavaScript for audio processing
│   ├── __init__.py             # Package initialization
│   ├── app.py                  # Main Dash application
│   └── creacion_audios.py      # Audio creation utilities
├── poetry.lock                 # Poetry lock file
├── pyproject.toml              # Project configuration
├── README.md                   # This file
└── run.py                      # Entry point script
```

## Technical Details

The application uses the Web Audio API through Dash's client-side callbacks to process the audio. The processing includes:

1. Creating separate audio sources for left and right channels
2. Applying a delay to one channel
3. Merging the channels back together
4. Playing the processed audio through the user's speakers

This approach ensures that the audio processing happens in the browser, reducing server load and providing a smoother user experience.

The client-side JavaScript code has been moved to an external file (`src/assets/audio_processor.js`) for better maintainability and separation of concerns. This follows best practices by keeping the Python code and JavaScript code separate, making the codebase easier to maintain and understand.
