import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import subprocess
import shutil

NEWS_API_KEY = "<Your NewsAPI Key>"  
OPENAI_KEY = "<Your OpenAI Key>"
SONG_FOLDER = r"D:\Zaheer\Songs"

listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
for v in voices:
    if 'zira' in v.name.lower():
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', 175)

def say(text):
    engine.say(text)
    engine.runAndWait()
    print(f"Friday: {text}")

def say_gTTS(text):
    try:
        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        os.remove("temp.mp3")
    except:
        pass

def ask_openai(prompt):
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def open_vscode():
    
    code_path = shutil.which("code")
    full_path = r"C:\Users\Prince Zaheer\AppData\Local\Programs\Microsoft VS Code\Code.exe"

    try:
        if code_path:
            subprocess.Popen([code_path])
            say("Launching Visual Studio Code. Happy Coding, Sir.")
        elif os.path.exists(full_path):
            subprocess.Popen([full_path])
            say("Launching Visual Studio Code. Happy Coding, Sir.")
        else:
            say("VS Code not detected. Opening web version instead, Sir.")
            webbrowser.open("https://code.visualstudio.com/")
    except Exception as e:
        say("VS Code command failed. Opening web version instead, Sir.")
        webbrowser.open("https://code.visualstudio.com/")

def play_local_songs():
    if not os.path.exists(SONG_FOLDER):
        say("Songs not found, Sir.")
        return
    files = [f for f in os.listdir(SONG_FOLDER) if f.lower().endswith(('.mp3', '.wav'))]
    if not files:
        say("No songs found in your folder, Sir.")
        return

    say("Playing Music, Sir.")
    pygame.mixer.init()
    
    for song in files:
        song_path = os.path.join(SONG_FOLDER, song)
        say(f"Now playing {song}, Sir.")
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Could not play {song}: {e}")
    pygame.mixer.quit()

def handleCommand(cmd_input):
    cmd_input_lower = cmd_input.lower()

    if "launch vs code" in cmd_input_lower:
        open_vscode()

    elif "open chat" in cmd_input_lower:
        say("Opening ChatGPT. Enjoy your Conversation, Sir.")
        webbrowser.open("https://chatgpt.com/")

    elif "open youtube" in cmd_input_lower:
        say("Opening YouTube. Enjoy your Videos, Sir.")
        webbrowser.open("https://www.youtube.com/")

    elif cmd_input_lower.startswith("play music"):
        play_local_songs()

    elif "news" in cmd_input_lower:
        say("Here are the Top Headlines, Sir.")
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}")
            articles = r.json().get('articles', [])
            for article in articles[:5]:
                say_gTTS(article['title'])
        except:
            say("Unable to fetch news at the moment, Sir.")

    else:
        say("Processing your Request, Sir.")
        answer = ask_openai(cmd_input)
        say_gTTS(answer)

if __name__ == "__main__":
    say("Friday is now Online, Sir.")
    listener.energy_threshold = 200
    listener.dynamic_energy_threshold = True
    listener.pause_threshold = 0.5

    while True:
        try:
            with sr.Microphone() as source:
                listener.adjust_for_ambient_noise(source, duration=1.5)
                audio = listener.listen(source, timeout=7, phrase_time_limit=8)
            wake = listener.recognize_google(audio)

            if "friday" in wake.lower():
                say("At your Service, Sir.")
                with sr.Microphone() as source:
                    listener.adjust_for_ambient_noise(source, duration=1.5)
                    audio = listener.listen(source, timeout=7, phrase_time_limit=8)
                    command = listener.recognize_google(audio)
                    handleCommand(command)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue
        