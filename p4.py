import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit
import wikipedia
from googletrans import Translator
import os
import pyautogui
import datetime
from gtts import gTTS
from playsound import playsound
import pyjokes
import threading
from pytube import YouTube
import google.generativeai as genai
import subprocess
from PIL import Image, ImageTk
import requests
import random
import pyperclip

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyA2-8grvJ64c18CCgbMP824CPZmysKDJBs"
genai.configure(api_key=GEMINI_API_KEY)

# --- Voice Assistant Core ---
class VoiceAssistant:
    def __init__(self, output_callback):
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 170)
        self.output_callback = output_callback
        self.reminders = []

    def speak(self, text):
        self.output_callback(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language='en-in')
            self.output_callback(f"You said: {query}")
        except Exception:
            self.speak("Sorry, I did not catch that.")
            return ""
        return query.lower()

    def handle_command(self, query):
        if not query:
            return
        # Check reminders
        self.check_reminders()
        # Custom greeting
        if 'good morning' in query or 'good afternoon' in query or 'good evening' in query:
            self.custom_greeting()
            return
        # Weather
        if 'weather' in query:
            city = query.split('in')[-1].strip() if 'in' in query else 'your city'
            self.get_weather(city)
            return
        # Reminder
        if 'remind me to' in query:
            try:
                task = query.split('remind me to')[1].split('at')[0].strip()
                time_str = query.split('at')[-1].strip()
                self.set_reminder(task, time_str)
            except Exception:
                self.speak("Sorry, I couldn't set the reminder.")
            return
        # Timer
        if 'set a timer for' in query:
            try:
                minutes = int(query.split('set a timer for')[1].split('minute')[0].strip())
                self.set_timer(minutes)
            except Exception:
                self.speak("Sorry, I couldn't set the timer.")
            return
        # News
        if 'news' in query:
            self.get_news()
            return
        # System control
        for action in ['mute volume', 'increase volume', 'decrease volume', 'lock computer', 'take screenshot']:
            if action in query:
                self.system_control(action)
                return
        # Email
        if 'send an email' in query:
            self.send_email('recipient@example.com', 'subject', 'message')
            return
        # Calendar
        if 'calendar' in query:
            self.get_calendar()
            return
        # Fun
        for fun_type in ['riddle', 'fact', 'flip a coin', 'roll a dice']:
            if fun_type in query:
                if fun_type == 'flip a coin':
                    self.fun_feature('coin')
                elif fun_type == 'roll a dice':
                    self.fun_feature('dice')
                else:
                    self.fun_feature(fun_type)
                return
        # File search/open
        if 'find file' in query:
            filename = query.split('find file')[-1].strip()
            self.file_search(filename)
            return
        if 'open file' in query:
            filename = query.split('open file')[-1].strip()
            self.open_file(filename)
            return
        # Clipboard
        if 'copy this' in query:
            text = query.split('copy this')[-1].strip()
            self.clipboard_action('copy', text)
            return
        if 'paste' in query:
            self.clipboard_action('paste')
            return
        if 'read my clipboard' in query:
            self.clipboard_action('read')
            return
        # Expanded general Q&A: try to answer general questions locally, else fallback to Gemini
        general_qna = {
            'who are you': "I'm your voice assistant.",
            'what is your name': "I'm your voice assistant.",
            'how are you': "I'm always here to help you!",
            'hello': "Hello! How can I assist you today?",
            'hi': "Hi there! How can I help you?",
            'what can you do': "I can open apps, search the web, play songs, tell jokes, answer questions, and more!",
            'who made you': "I was created by my developer using Python and AI.",
            'what is your purpose': "My purpose is to assist you with tasks, answer questions, and make your life easier.",
            'what time is it': datetime.datetime.now().strftime("It's %I:%M %p."),
            'what day is it': datetime.datetime.now().strftime("Today is %A, %B %d, %Y."),
            'thank you': "You're welcome!",
            'thanks': "You're welcome!",
            'goodbye': "Goodbye! Have a great day!",
            'bye': "Goodbye! Have a great day!",
        }
        for key in general_qna:
            if key in query:
                self.speak(general_qna[key])
                return
        # If the query is a general question (who, what, when, where, why, how, etc.), use Gemini
        general_starts = ("who ", "what ", "when ", "where ", "why ", "how ", "explain ", "define ", "tell me about ", "describe ")
        if query.strip().endswith('?') or query.startswith(general_starts):
            prompt = query
            try:
                self.speak("Thinking...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                answer = response.text.strip()
                self.speak(answer)
            except Exception:
                self.speak("Sorry, I couldn't find an answer to that.")
            return
        # --- Dynamic open app/website logic ---
        if query.startswith('open '):
            rest = query[5:].strip()
            # YouTube special case: open and search
            if rest.startswith('youtube'):
                if 'search' in rest:
                    # e.g. 'open youtube and search weekend'
                    search_term = rest.split('search',1)[-1].strip()
                    if search_term:
                        self.speak(f"Searching YouTube for {search_term}")
                        pywhatkit.playonyt(search_term)
                        return
                self.speak("Opening YouTube.")
                webbrowser.open('https://www.youtube.com/')
                return
            # Open any website
            if rest.startswith('www.') or rest.endswith('.com') or rest.endswith('.org') or rest.endswith('.net'):
                url = rest if rest.startswith('http') else f"https://{rest}"
                self.speak(f"Opening {url}")
                webbrowser.open(url)
                return
            # Try to open as an app (by name)
            try:
                self.speak(f"Opening {rest}.")
                subprocess.Popen(rest)
                return
            except Exception:
                pass
            # Try to open as a Windows app via start
            try:
                subprocess.Popen(["start", "", rest], shell=True)
                return
            except Exception:
                pass
            self.speak(f"Sorry, I couldn't open {rest}.")
            return
        # --- End dynamic open logic ---
        # Play song (YouTube)
        if 'play' in query:
            song = query.replace('play', '').strip()
            if song:
                self.speak(f"Playing {song} on YouTube.")
                pywhatkit.playonyt(song)
                return
        # Voice commands
        if 'open' in query and 'chrome' in query:
            self.speak("Opening Chrome.")
            os.startfile(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        elif 'open' in query and 'code' in query:
            self.speak("Opening VS Code.")
            os.startfile(r"C:\Users\Arjun\AppData\Local\Programs\Microsoft VS Code\Code.exe")
        elif 'open' in query and 'facebook' in query:
            self.speak("Opening Facebook.")
            webbrowser.open('https://www.facebook.com/')
        elif 'open' in query and 'instagram' in query:
            self.speak("Opening Instagram.")
            webbrowser.open('https://www.instagram.com/')
        elif 'open' in query and 'maps' in query:
            self.speak("Opening Google Maps.")
            webbrowser.open('https://www.google.com/maps')
        elif 'joke' in query:
            joke = pyjokes.get_joke()
            self.speak(joke)
        elif 'wikipedia' in query:
            topic = query.replace('wikipedia', '').strip()
            self.speak(f"Searching Wikipedia for {topic}")
            try:
                result = wikipedia.summary(topic, sentences=2)
                self.speak(result)
            except Exception:
                self.speak("No results found on Wikipedia.")
        elif 'google' in query:
            topic = query.replace('google', '').strip()
            self.speak(f"Searching Google for {topic}")
            pywhatkit.search(topic)
        elif 'translate' in query:
            self.speak("What text do you want to translate?")
            text = self.listen()
            self.speak("To which language? (e.g., hi for Hindi, fr for French)")
            lang = self.listen()
            if text and lang:
                translator = Translator()
                try:
                    result = translator.translate(text, dest=lang)
                    self.speak(result.text)
                except Exception:
                    self.speak("Translation failed.")
        elif 'screenshot' in query:
            self.speak("What should I name the screenshot file?")
            name = self.listen().replace(' ', '_')
            if name:
                filename = os.path.join(os.path.expanduser('~'), f"{name}.png")
                try:
                    screenshot = pyautogui.screenshot()
                    screenshot.save(filename)
                    self.speak(f"Screenshot saved as {filename}")
                except Exception:
                    self.speak("Failed to take screenshot.")
        elif 'set alarm' in query or 'alarm' in query:
            self.speak("At what time? Please say in HH:MM format.")
            time_str = self.listen()
            if time_str:
                self.set_alarm(time_str)
        elif 'download' in query and 'youtube' in query:
            self.speak("Please say the YouTube video URL.")
            url = self.listen()
            self.speak("Where should I save the video? Please say the folder path.")
            folder = self.listen()
            try:
                yt = YouTube(url)
                stream = yt.streams.get_highest_resolution()
                stream.download(output_path=folder)
                self.speak("Video downloaded successfully.")
            except Exception as e:
                self.speak(f"Failed to download video: {e}")
        elif 'read pdf' in query or 'read book' in query:
            self.speak("Please say the full path to the PDF file.")
            file_path = self.listen()
            self.speak("Which page number should I read? (Say a number)")
            page_num_str = self.listen()
            try:
                page_num = int(page_num_str)
                import PyPDF2
                with open(file_path, 'rb') as book:
                    pdfreader = PyPDF2.PdfReader(book)
                    pages = len(pdfreader.pages)
                    self.speak(f"Number of pages: {pages}")
                    if page_num >= pages:
                        self.speak("Invalid page number.")
                        return
                    page = pdfreader.pages[page_num]
                    text = page.extract_text()
                    self.speak("In which language should I read? (Say 'en' for English, 'hi' for Hindi, etc.)")
                    lang = self.listen()
                    if lang != 'en':
                        translator = Translator()
                        try:
                            result = translator.translate(text, dest=lang)
                            self.speak(result.text)
                        except Exception:
                            self.speak("Translation failed.")
                    else:
                        self.speak(text)
            except Exception as e:
                self.speak(f"Failed to read PDF: {e}")
        elif 'gemini' in query or 'ask ai' in query or '?' in query:
            # For any other question, use Gemini
            prompt = query
            try:
                self.speak("Thinking...")
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                answer = response.text.strip()
                self.speak(answer)
            except Exception as e:
                self.speak(f"Gemini API error: {e}")
        elif 'exit' in query or 'quit' in query or 'stop' in query:
            self.speak("Goodbye!")
            os._exit(0)
        else:
            self.speak("Sorry, I don't understand that command.")

    def set_alarm(self, alarm_time):
        self.speak(f"Alarm set for {alarm_time}")
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == alarm_time:
                self.speak("Time to wake up!")
                playsound('alarm.mp3')
                break

    # --- Advanced Features ---
    def get_weather(self, city):
        try:
            api_key = 'b6907d289e10d714a6e88b30761fae22'  # OpenWeatherMap sample key (replace with your own for production)
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
            data = requests.get(url).json()
            if data.get('main'):
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                self.speak(f"The weather in {city} is {desc} with a temperature of {temp}°C.")
            else:
                self.speak(f"Sorry, I couldn't get the weather for {city}.")
        except Exception:
            self.speak("Sorry, I couldn't get the weather information.")

    def set_reminder(self, task, time_str):
        self.reminders.append((task, time_str))
        self.speak(f"Reminder set for {task} at {time_str}.")

    def check_reminders(self):
        now = datetime.datetime.now().strftime("%H:%M")
        for task, time_str in self.reminders[:]:
            if now == time_str:
                self.speak(f"Reminder: {task}")
                self.reminders.remove((task, time_str))

    def set_timer(self, minutes):
        self.speak(f"Timer set for {minutes} minutes.")
        threading.Thread(target=self._timer_thread, args=(minutes,), daemon=True).start()
    def _timer_thread(self, minutes):
        import time
        time.sleep(minutes * 60)
        self.speak("Timer is up!")

    def get_news(self):
        try:
            url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=5d1b3e6e2e2e4e7e8e8e8e8e8e8e8e8e'  # Replace with your NewsAPI key
            data = requests.get(url).json()
            if data.get('articles'):
                headlines = [a['title'] for a in data['articles'][:5]]
                for h in headlines:
                    self.speak(h)
            else:
                self.speak("Sorry, I couldn't fetch the news.")
        except Exception:
            self.speak("Sorry, I couldn't fetch the news.")

    def system_control(self, action):
        try:
            if action == 'mute volume':
                os.system('nircmd.exe mutesysvolume 1')
                self.speak("Volume muted.")
            elif action == 'increase volume':
                os.system('nircmd.exe changesysvolume 20000')
                self.speak("Volume increased.")
            elif action == 'decrease volume':
                os.system('nircmd.exe changesysvolume -20000')
                self.speak("Volume decreased.")
            elif action == 'lock computer':
                os.system('rundll32.exe user32.dll,LockWorkStation')
                self.speak("Computer locked.")
            elif action == 'take screenshot':
                screenshot = pyautogui.screenshot()
                filename = os.path.join(os.path.expanduser('~'), f"screenshot_{random.randint(1000,9999)}.png")
                screenshot.save(filename)
                self.speak(f"Screenshot saved as {filename}")
            else:
                self.speak("System action not recognized.")
        except Exception:
            self.speak("System control failed.")

    def send_email(self, to, subject, message):
        self.speak("Email sending is not configured. Please add your email credentials and code.")

    def get_calendar(self):
        self.speak("Calendar integration is not configured. Please add your Google Calendar API setup.")

    def fun_feature(self, fun_type):
        if fun_type == 'riddle':
            riddles = [
                "What has keys but can't open locks? A piano.",
                "What has a head and a tail but no body? A coin.",
                "What gets wetter as it dries? A towel."
            ]
            self.speak(random.choice(riddles))
        elif fun_type == 'fact':
            facts = [
                "Honey never spoils.",
                "Bananas are berries, but strawberries aren't.",
                "Octopuses have three hearts."
            ]
            self.speak(random.choice(facts))
        elif fun_type == 'coin':
            self.speak(f"It's {'heads' if random.choice([True, False]) else 'tails'}.")
        elif fun_type == 'dice':
            self.speak(f"You rolled a {random.randint(1,6)}.")

    def file_search(self, filename):
        for root, dirs, files in os.walk(os.path.expanduser('~')):
            if filename in files:
                filepath = os.path.join(root, filename)
                self.speak(f"Found {filename} at {filepath}")
                return filepath
        self.speak(f"File {filename} not found.")
        return None

    def open_file(self, filename):
        filepath = self.file_search(filename)
        if filepath:
            os.startfile(filepath)

    def clipboard_action(self, action, text=None):
        if action == 'copy' and text:
            pyperclip.copy(text)
            self.speak("Copied to clipboard.")
        elif action == 'paste':
            pasted = pyperclip.paste()
            self.speak(f"Clipboard: {pasted}")
        elif action == 'read':
            pasted = pyperclip.paste()
            self.speak(f"Clipboard: {pasted}")

    def custom_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            self.speak("Good morning!")
        elif hour < 18:
            self.speak("Good afternoon!")
        else:
            self.speak("Good evening!")

# --- GUI ---
class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Astra Voice Assistant")
        self.root.geometry("700x600")
        self.root.configure(bg="#181c25")
        self.root.resizable(True, True)
        self.assistant = VoiceAssistant(self.display_output)
        self.listening = False
        self._stop_listen_flag = False
        self.create_widgets()

    def create_widgets(self):
        # Use grid for full flexibility
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Avatar/icon
        avatar_frame = tk.Frame(self.root, bg="#181c25")
        avatar_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10))
        try:
            avatar_img = Image.open("assistant_avatar.png").resize((100, 100))
        except Exception:
            avatar_img = Image.new("RGBA", (100, 100), (24, 28, 37, 255))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(avatar_img)
            draw.ellipse((10, 10, 90, 90), fill="#00e6ff", outline="#00e6ff")
        self.avatar_photo = ImageTk.PhotoImage(avatar_img)
        avatar_label = tk.Label(avatar_frame, image=self.avatar_photo, bg="#181c25")
        avatar_label.pack()
        name_label = tk.Label(avatar_frame, text="ASTRA", font=("Orbitron", 28, "bold"), fg="#00e6ff", bg="#181c25")
        name_label.pack()

        # Animated listening indicator (circle)
        self.listen_canvas = tk.Canvas(self.root, width=60, height=60, bg="#181c25", highlightthickness=0)
        self.listen_canvas.grid(row=1, column=0, pady=(0, 10), sticky="n")
        self.listen_circle = self.listen_canvas.create_oval(10, 10, 50, 50, outline="#00e6ff", width=4)
        self._listening_anim = False

        # Custom style for neon blue scrollbar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar",
                        gripcount=0,
                        background="#00e6ff",
                        darkcolor="#00bfff",
                        lightcolor="#00e6ff",
                        troughcolor="#23283a",
                        bordercolor="#23283a",
                        arrowcolor="#00e6ff",
                        relief="flat")
        style.map("Vertical.TScrollbar",
                  background=[('active', '#1de9b6'), ('!active', '#00e6ff')],
                  arrowcolor=[('active', '#1de9b6'), ('!active', '#00e6ff')])

        # Output area
        output_frame = tk.Frame(self.root, bg="#23283a")
        output_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        self.output_area = tk.Text(output_frame, wrap=tk.WORD, font=("Consolas", 12), fg="#00e6ff", bg="#23283a", insertbackground="#00e6ff", borderwidth=0, highlightthickness=0)
        self.output_area.grid(row=0, column=0, sticky="nsew")
        self.output_area.config(state=tk.DISABLED)
        self.scrollbar = ttk.Scrollbar(output_frame, orient="vertical", style="Vertical.TScrollbar", command=self.output_area.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_area['yscrollcommand'] = self.scrollbar.set

        # Button frame
        btn_frame = tk.Frame(self.root, bg="#181c25")
        btn_frame.grid(row=3, column=0, sticky="ew", pady=10, padx=0)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        self.start_btn = tk.Button(
            btn_frame, text="Start Listening", command=self.start_listening,
            font=("Orbitron", 16, "bold"),
            bg="#0099ff", fg="#ffffff",
            activebackground="#00e6ff", activeforeground="#181c25",
            bd=4, relief=tk.RAISED, highlightthickness=2, cursor="hand2"
        )
        self.start_btn.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.stop_btn = tk.Button(
            btn_frame, text="Stop Listening", command=self.stop_listening,
            font=("Orbitron", 16, "bold"),
            bg="#ff1744", fg="#ffffff",
            activebackground="#ff5252", activeforeground="#181c25",
            bd=4, relief=tk.RAISED, highlightthickness=2, cursor="hand2", state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=20, pady=5, sticky="ew")

    def display_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"{text}\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.start_btn.config(state=tk.DISABLED, bg="#b3e5fc", fg="#181c25")
            self.stop_btn.config(state=tk.NORMAL, bg="#ff1744", fg="#ffffff")
            self._stop_listen_flag = False
            self._listening_anim = True
            self.animate_listen_circle()
            threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        self.listening = False
        self._stop_listen_flag = True
        self.start_btn.config(state=tk.NORMAL, bg="#0099ff", fg="#ffffff")
        self.stop_btn.config(state=tk.DISABLED, bg="#bdbdbd", fg="#ffffff")
        self._listening_anim = False
        self.listen_canvas.itemconfig(self.listen_circle, outline="#00e6ff")

    def animate_listen_circle(self):
        if not self._listening_anim:
            self.listen_canvas.itemconfig(self.listen_circle, outline="#00e6ff")
            return
        import random
        color = random.choice(["#00e6ff", "#00bfff", "#1de9b6", "#00bcd4"])
        self.listen_canvas.itemconfig(self.listen_circle, outline=color)
        self.root.after(400, self.animate_listen_circle)

    def listen_loop(self):
        while self.listening and not getattr(self, '_stop_listen_flag', False):
            query = self.assistant.listen()
            if not self.listening or getattr(self, '_stop_listen_flag', False):
                break
            if query:
                self.assistant.handle_command(query)
        self.start_btn.config(state=tk.NORMAL, bg="#0099ff", fg="#ffffff")
        self.stop_btn.config(state=tk.DISABLED, bg="#bdbdbd", fg="#ffffff")
        self._listening_anim = False
        self.listen_canvas.itemconfig(self.listen_circle, outline="#00e6ff")

# --- Main ---
def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()