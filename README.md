# Astra Voice Assistant

Astra is a modern, AI-powered desktop voice assistant for Windows, inspired by futuristic assistants like Jarvis. It features a beautiful neon UI, voice-first control, and a wide range of smart features—all using free APIs and local functionality.

---

## Features
- **Voice-activated control** (no typing needed)
- **Weather information** (via OpenWeatherMap API)
- **News headlines** (via NewsAPI)
- **Reminders & Timers**
- **System control** (volume, lock, screenshot, etc.)
- **Play music/videos on YouTube**
- **Open any app or website**
- **Clipboard management** (copy, paste, read)
- **File search and open**
- **Fun:** jokes, riddles, facts, coin flip, dice roll
- **Custom greetings**
- **AI Q&A** (Google Gemini API)
- **Beautiful, resizable, Jarvis-inspired UI**

---

## Installation

### 1. Clone the repository or copy the files

### 2. Install Python 3.9+

### 3. Install required packages:
```sh
pip install -r requirements.txt
```
If you don't have a `requirements.txt`, install manually:
```sh
pip install pyttsx3 SpeechRecognition pywhatkit wikipedia googletrans==4.0.0-rc1 pyautogui gtts playsound pyjokes pytube google-generativeai requests pyperclip pillow
```

### 4. (Optional) Download [nircmd.exe](https://www.nirsoft.net/utils/nircmd.html) and place it in your PATH for system volume/lock commands.

---

## Free APIs Used & How to Get Keys

### **Weather (OpenWeatherMap)**
- Sign up at https://openweathermap.org/
- Get your free API key from your dashboard.
- Replace the `api_key` in the code:
  ```python
  api_key = 'YOUR_OPENWEATHERMAP_KEY'
  ```

### **News (NewsAPI)**
- Sign up at https://newsapi.org/
- Get your free API key from your dashboard.
- Replace the `apiKey` in the code:
  ```python
  url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_NEWSAPI_KEY'
  ```

### **AI Q&A (Google Gemini)**
- Get a free API key at https://aistudio.google.com/app/apikey
- Replace the Gemini API key in the code:
  ```python
  GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY'
  ```

---

## How to Run

```sh
python p4.py
```

- Click **Start Listening** to begin.
- Speak your command!
- Click **Stop Listening** to pause.

---

## Example Voice Commands
- "What's the weather in London?"
- "Remind me to call mom at 5 PM"
- "Set a timer for 2 minutes"
- "Tell me the latest news"
- "Mute volume"
- "Increase volume"
- "Lock computer"
- "Take a screenshot"
- "Play Shape of You on YouTube"
- "Open notepad"
- "Open github.com"
- "Find file report.pdf"
- "Open file notes.txt"
- "Copy this Hello World"
- "Paste"
- "Read my clipboard"
- "Tell me a riddle"
- "Flip a coin"
- "Roll a dice"
- "Who is the president of India?"

---

## Notes & Credits
- **Email and calendar integration** are placeholders—ask for setup help if you want to enable them.
- System control (volume, lock) uses [nircmd](https://www.nirsoft.net/utils/nircmd.html) (free, Windows only).
- UI uses [Pillow](https://python-pillow.org/) for avatar support.
- Inspired by Jarvis, but fully customizable.

---

**Enjoy your futuristic Astra Voice Assistant!** 
