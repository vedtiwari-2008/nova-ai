from flask import Flask, request, jsonify
import os
import subprocess
import random
from random import choice
import time
import shutil
import webbrowser
import zipfile
from datetime import datetime, timedelta
import threading
import speech_recognition as sr
import pyttsx3
import keyboard
import pyautogui
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from cryptography.fernet import Fernet
import jsonlines
from datasets import load_dataset
from bs4 import BeautifulSoup

app = Flask(__name__)

# Disable PyAutoGUI fail-safe (use with caution)
pyautogui.FAILSAFE = False

# Define user profile
user_profile = {"name": "Sir", "favorites": [], "mood": "Happy"}

# Initialize the to-do list and reminders
todo_list = []
reminders = []

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to the user's voice and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0)
            audio = recognizer.listen(source, timeout=600)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("")
            return ""
        except sr.RequestError:
            speak("Sorry, there seems to be an issue with the speech recognition service.")
            return ""
        except Exception as e:
            speak("An error occurred. Please try again Sir.")
            print(f"Error: {e}")
            return ""

# Give some time for the page to load before scrolling
time.sleep(0)

# Scroll down faster (repeat for quick scrolling)
for _ in range(-300):  # Increase range for faster scrolling
    pyautogui.press('pagedown')

# Scroll up faster (repeat for quick scrolling)
for _ in range(+300):  # Increase range for faster scrolling
    pyautogui.press('pageup')

def web_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for paragraph in soup.find_all(['p', 'div'], class_='BNeawe iBp4i AP7Wnd')[:5]:
            content = paragraph.get_text()
            if content:
                results.append(content)
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        print("Error during web search:", e)
        return "Error during web search."

def search_google_maps(query):
    url = f"https://www.google.com/maps?q={query}"
    webbrowser.open(url)
    return f"Searching for {query} on Google Maps Sir."

def get_directions(start, end):
    url = f"https://www.google.com/maps/dir/{start}/{end}"
    webbrowser.open(url)
    return f"Getting directions from {start} to {end} on Google Maps Sir."

backup_folder = "C:/NovaBackup"
cloud_storage_folder = "C:/CloudStorage"

def organize_files():
    folders = {
        "Documents": ['.txt', '.pdf', '.docx', '.xlsx'],
        "Images": ['.jpg', '.png', '.jpeg', '.gif'],
        "Videos": ['.mp4', '.mkv', '.avi'],
        "Audios": ['.mp3', '.wav'],
        "Archives": ['.zip', '.rar'],
    }
    for folder_name, extensions in folders.items():
        folder_path = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for file in os.listdir():
            if os.path.isfile(file) and any(file.endswith(ext) for ext in extensions):
                shutil.move(file, os.path.join(folder_path, file))
                speak(f"Moved {file} to {folder_name} folder.")
    return "Files organized successfully."

def bulk_rename_files():
    speak("Please provide the pattern for renaming files (e.g., 'file_1', 'image_1').")
    pattern = listen().strip()
    if pattern:
        files = [f for f in os.listdir() if os.path.isfile(f)]
        for index, file in enumerate(files):
            extension = os.path.splitext(file)[1]
            new_name = f"{pattern}_{index + 1}{extension}"
            os.rename(file, new_name)
            speak(f"Renamed {file} to {new_name}.")
        return f"Renamed {len(files)} files."
    return "Invalid pattern provided."

def backup_files():
    speak("Backing up important files.")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    files_to_backup = ['important_file1.txt', 'important_file2.pdf']
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy(file, backup_folder)
            speak(f"Backup of {file} completed.")
        else:
            speak(f"{file} does not exist for backup.")
    return "Backup completed."

def restore_files():
    speak("Restoring files from backup.")
    for file in os.listdir(backup_folder):
        shutil.copy(os.path.join(backup_folder, file), os.getcwd())
        speak(f"Restored {file}.")
    return "Files restored."

def search_files():
    speak("Enter the directory to search in:")
    directory = listen().strip()
    speak("Enter the file type to search for (e.g., .txt, .jpg):")
    file_type = listen().strip()
    files = [f for f in os.listdir(directory) if f.endswith(file_type)]
    speak(f"Found the following files of type {file_type}: {', '.join(files)}")
    return f"Found: {', '.join(files)}"

def find_duplicate_files():
    files = [f for f in os.listdir() if os.path.isfile(f)]
    seen = {}
    duplicates = []
    for file in files:
        file_hash = hash(open(file, 'rb').read())
        if file_hash in seen:
            duplicates.append(file)
        else:
            seen[file_hash] = file
    if duplicates:
        speak(f"Found duplicate files: {', '.join(duplicates)}")
        speak("Would you like to delete them? (yes/no)")
        choice = listen().strip().lower()
        if choice == 'yes':
            for dup in duplicates:
                os.remove(dup)
                speak(f"Deleted duplicate file: {dup}")
            you'd like to delete them? (yes/no)")
        choice = listen().strip().lower()
        if choice == 'yes':
            for dup in duplicates:
                os.remove(dup)
                speak(f"Deleted duplicate file: {dup}")
            return f"Deleted duplicates: {', '.join(duplicates)}"
    return "No duplicates found."

def change_file_permissions():
    speak("Please specify the file and the permissions you want to set (read, write, execute).")
    file_name = listen().strip()
    speak("Please specify the permissions (read/write/execute or all).")
    permissions = listen().strip().lower()
    try:
        mode = 0
        if 'read' in permissions:
            mode |= 0o444
        if 'write' in permissions:
            mode |= 0o222
        if 'execute' in permissions:
            mode |= 0o111
        os.chmod(file_name, mode)
        speak(f"Permissions for {file_name} set to {permissions}.")
        return f"Permissions set for {file_name}."
    except Exception as e:
        speak(f"Error changing permissions: {e}")
        return f"Error: {e}"

def compress_file():
    speak("Please provide the file you want to compress.")
    file_name = listen().strip()
    if os.path.exists(file_name):
        zip_name = f"{file_name}.zip"
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            zipf.write(file_name, os.path.basename(file_name))
        speak(f"File {file_name} compressed into {zip_name}.")
        return f"Compressed {file_name} into {zip_name}."
    speak(f"The file {file_name} does not exist.")
    return f"File {file_name} does not exist."

def extract_file():
    speak("Please provide the ZIP file to extract.")
    zip_file = listen().strip()
    if zipfile.is_zipfile(zip_file):
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extractall()
        speak(f"Extracted {zip_file} successfully.")
        return f"Extracted {zip_file}."
    speak(f"{zip_file} is not a valid ZIP file.")
    return f"{zip_file} is not a valid ZIP file."

def encrypt_file():
    speak("Please provide the file you want to encrypt.")
    file_name = listen().strip()
    if os.path.exists(file_name):
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        with open(file_name, 'rb') as file:
            file_data = file.read()
        encrypted_data = cipher_suite.encrypt(file_data)
        encrypted_file = f"{file_name}.enc"
        with open(encrypted_file, 'wb') as enc_file:
            enc_file.write(encrypted_data)
        speak(f"File {file_name} encrypted into {encrypted_file}. Keep the key safe!")
        return f"Encrypted {file_name} into {encrypted_file}."
    speak(f"{file_name} does not exist.")
    return f"{file_name} does not exist."

def decrypt_file():
    speak("Please provide the encrypted file to decrypt.")
    encrypted_file = listen().strip()
    if os.path.exists(encrypted_file):
        speak("Please provide the decryption key.")
        key = listen().strip().encode()
        cipher_suite = Fernet(key)
        with open(encrypted_file, 'rb') as enc_file:
            encrypted_data = enc_file.read()
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        decrypted_file = encrypted_file.replace(".enc", "_decrypted")
        with open(decrypted_file, 'wb') as dec_file:
            dec_file.write(decrypted_data)
        speak(f"File {encrypted_file} decrypted into {decrypted_file}.")
        return f"Decrypted {encrypted_file} into {decrypted_file}."
    speak(f"{encrypted_file} does not exist.")
    return f"{encrypted_file} does not exist."

def schedule_cleanup():
    speak("How often would you like to clean up the temporary files? (e.g., 'every week', 'once a month')")
    schedule = listen().strip()
    speak(f"Scheduled cleanup every {schedule}.")
    return f"Scheduled cleanup every {schedule}."

def cloud_storage_upload():
    speak("Please provide the file to upload to the cloud.")
    file_name = listen().strip()
    if os.path.exists(file_name):
        shutil.copy(file_name, cloud_storage_folder)
        speak(f"File {file_name} uploaded to cloud storage.")
        return f"File {file_name} uploaded to cloud storage."
    speak(f"{file_name} does not exist.")
    return f"{file_name} does not exist."

def open_youtube():
    speak("What would you like to do Sir? Open YouTube or play music?")
    choice = listen().strip()
    if "music" in choice:
        webbrowser.open("https://www.youtube.com/results?search_query=random+music")
        speak("Playing random music on YouTube now.")
        return "Playing random music on YouTube."
    elif "open" in choice or "youtube" in choice:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube Sir.")
        return "Opening YouTube."
    speak("I'm sorry, I couldn't understand that. Please say 'play music' or 'open YouTube'.")
    return "Invalid choice."

def play_random_music():
    music_links = [
        "https://youtu.be/34Na4j8AVgA",
        "https://www.youtube.com/watch?v=sZrTJesvJeo",
        "https://www.youtube.com/watch?v=cNGjD0VG4R8",
        "https://www.youtube.com/watch?v=au1PyhcecWg",
        "https://www.youtube.com/watch?v=KuNQlwpeJHo",
    ]
    selected_music = random.choice(music_links)
    webbrowser.open(selected_music)
    speak("Playing random music on YouTube for you Sir.")
    return "Playing random music on YouTube."

def play_rock_music():
    music_links = [
        "https://www.youtube.com/watch?v=Ezsb5afVXQQ",
        "https://www.youtube.com/watch?v=unigt-F2JT0",
        "https://www.youtube.com/watch?v=sRlA7JWTj04",
        "https://www.youtube.com/watch?v=7UhWfDK1btc",
        "https://www.youtube.com/watch?v=WgxGftJ_OxE",
        "https://www.youtube.com/watch?v=2ydCvkxuNm4",
        "https://www.youtube.com/watch?v=f8arpOUQc-E",
    ]
    selected_music = random.choice(music_links)
    webbrowser.open(selected_music)
    speak("Playing rocking music on YouTube for you Sir.")
    return "Playing rock music on YouTube."

def play_romantic_music():
    music_links = [
        "https://www.youtube.com/watch?v=g5WZLO8BAC8",
        "https://www.youtube.com/watch?v=3DtJ9egY9rs",
        "https://www.youtube.com/watch?v=kPhpHvnnn0Q",
        "https://www.youtube.com/watch?v=taRBVfDRukY",
        "https://www.youtube.com/watch?v=taRBVfDRukY",
        "https://www.youtube.com/watch?v=y9Kqb2z9Lzs",
        "https://www.youtube.com/watch?v=OgRoRBLZbUQ",
    ]
    selected_music = random.choice(music_links)
    webbrowser.open(selected_music)
    speak("Playing Romantic music on YouTube for you Sir.")
    return "Playing romantic music on YouTube."

class PersonalGrowthTracker:
    def __init__(self):
        self.goals = {
            'fitness': {'completed': 3, 'total': 5, 'level': 'Silver'},
            'language': {'completed': 50, 'total': 100, 'level': 'Bronze'},
            'reading': {'completed': 2, 'total': 5, 'level': 'Bronze'},
        }
        self.points = 0

    def update_points(self):
        self.points += 10
        return self.points

    def get_milestones(self):
        milestones = ""
        for goal, data in self.goals.items():
            milestones += f"{goal.capitalize()}: {data['completed']}/{data['total']} (Level: {data['level']})\n"
        return milestones

    def show_progress(self):
        milestones = self.get_milestones()
        points = self.update_points()
        return f"Your progress:\n{milestones}You’ve earned {points} points today. Keep going!"

def show_growth_progress():
    tracker = PersonalGrowthTracker()
    return tracker.show_progress()

class EmergencyHelper:
    def __init__(self):
        self.response_teams = {
            'medical': [
                {'name': 'Ashish Chacha', 'contact': '7756975987'},
                {'name': 'Dr. Sharma', 'contact': '8882123456'}
            ],
            'technical': [
                {'name': 'Tech Support', 'contact': '9812345678'}
            ],
            'family': [
                {'name': 'Papa', 'contact': '7756975987'},
                {'name': 'Mummy', 'contact': '8801012345'}
            ]
        }
        self.alert_message = "Urgent! Please Call me!"

    def add_contact(self, team, name, contact):
        if team in self.response_teams:
            if self._validate_contact(contact):
                self.response_teams[team].append({'name': name, 'contact': contact})
                return f"Added {name} to {team} team."
            return "Invalid contact number."
        return "Invalid team."

    def send_alert(self, team):
        if team not in self.response_teams:
            return "Invalid team."
        contacts = self.response_teams[team]
        if not contacts:
            return "No contacts found in this team."
        alerts = []
        for contact in contacts:
            alerts.append(f"Alert sent to {contact['name']} ({contact['contact']}): {self.alert_message}")
        return "\n".join(alerts)

    def _validate_contact(self, contact):
        if len(contact) == 10 and contact.isdigit():
            return True
        return False

def emergency_helper_alert(team):
    helper = EmergencyHelper()
    return helper.send_alert(team)

def open_file():
    speak("Please tell me the name of the file you want to open Sir(without extension).")
    filename = listen().strip()
    if filename:
        file_extensions = ['.txt', '.pdf', '.docx', '.xlsx', '.jpg', '.png', '.csv']
        for ext in file_extensions:
            file_path = filename + ext
            if os.path.exists(file_path):
                os.startfile(file_path)
                speak(f"Opening the file '{file_path}'.")
                return f"Opening {file_path}."
        speak(f"Sorry, I couldn't find a file named '{filename}' with any known extensions.")
        return f"File {filename} not found."
    speak("Please provide a valid filename Sir.")
    return "Invalid filename."

def open_email():
    try:
        speak("Opening your email Sir.")
        webbrowser.open("https://mail.google.com")
        return "Opening email."
    except Exception as e:
        speak(f"An error occurred while opening email: {e}")
        return f"Error: {e}"

def open_application():
    speak("Please tell me the name or path of the application you want to open Sir.")
    app_name = listen().strip()
    if app_name:
        try:
            subprocess.run(app_name, shell=True)
            speak(f"Opening {app_name}...")
            return f"Opening {app_name}."
        except Exception as e:
            speak(f"Sorry, I couldn't open {app_name}. Error: {e}")
            return f"Error: {e}"
    speak("Please provide a valid application name or path.")
    return "Invalid application name."

def create_file():
    speak("What should I name the file for you Sir?")
    filename = listen().strip()
    if filename:
        with open(f"{filename}.txt", "w") as f:
            f.write("")
        speak(f"File {filename}.txt has been created.")
        return f"File {filename}.txt created."
    speak("Filename cannot be empty.")
    return "Filename cannot be empty."

def delete_file():
    speak("Please tell me the name of the file you want to delete Sir(with extension).")
    filename = listen().strip()
    if filename:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                speak(f"File '{filename}' has been deleted.")
                return f"File {filename} deleted."
            speak(f"Couldn't find the file '{filename}'.")
            return f"File {filename} not found."
        except Exception as e:
            speak(f"An error occurred: {e}")
            return f"Error: {e}"
    return "Invalid filename."

def rename_file():
    speak("Please provide the current name of the file Sir(with extension).")
    current_name = listen().strip()
    if os.path.exists(current_name):
        speak("What would you like to rename the file to? Please include the extension.")
        new_name = listen().strip()
        try:
            os.rename(current_name, new_name)
            speak(f"File renamed from {current_name} to {new_name}.")
            return f"File renamed to {new_name}."
        except Exception as e:
            speak(f"Error renaming the file: {e}")
            return f"Error: {e}"
    speak(f"The file {current_name} does not exist.")
    return f"File {current_name} does not exist."

def search_files():
    speak("Please provide the directory path to search in sir.")
    directory = listen().strip()
    speak("What file name or type are you looking for Sir?")
    file_name = listen().strip()
    try:
        files = [f for f in os.listdir(directory) if file_name in f]
        if files:
            speak(f"Found the following files: {', '.join(files)}")
            return f"Found: {', '.join(files)}"
        speak(f"No files found matching '{file_name}' in {directory}.")
        return f"No files found matching '{file_name}'."
    except Exception as e:
        speak(f"Error: {e}")
        return f"Error: {e}"

def countdown_timer():
    speak("How many seconds would you like to set the timer for?")
    seconds = int(listen().strip())
    speak(f"Starting a timer for {seconds} seconds.")
    time.sleep(seconds)
    speak("Time's up!")
    return "Timer completed."

def calculator():
    speak("What operation would you like to perform Sir? (addition, subtraction, multiplication, division)")
    operation = listen().strip()
    speak("Please provide the first number.")
    num1 = float(listen().strip())
    speak("Please provide the second number.")
    num2 = float(listen().strip())
    if operation == "addition":
        result = num1 + num2
    elif operation == "subtraction":
        result = num1 - num2
    elif operation == "multiplication":
        result = num1 * num2
    elif operation == "division":
        if num2 != 0:
            result = num1 / num2
        else:
            speak("Cannot divide by zero.")
            return "Cannot divide by zero."
    else:
        speak("Invalid operation.")
        return "Invalid operation."
    speak(f"The result of the {operation} is: {result}")
    return f"Result: {result}"

def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    speak(f"Total space: {total // (2**30)} GB")
    speak(f"Used space: {used // (2**30)} GB")
    speak(f"Free space: {free // (2**30)} GB")
    return f"Total: {total // (2**30)} GB, Used: {used // (2**30)} GB, Free: {free // (2**30)} GB"

def handle_command(command):
    command = command.lower()
    if "good night" in command:
        speak("Good Night, Sir! Sleep well and take care.")
        return "Good Night, Sir!"
    elif "good morning" in command:
        speak("Good Morning, Sir! Have a great day ahead.")
        return "Good Morning, Sir!"
    elif "greet" in command:
        return greet_user()
    speak("Sorry, I don't understand that command Sir.")
    return "Command not understood."

def greet_user():
    hour = datetime.now().hour
    if hour < 12:
        speak("Good Morning, Sir!")
        return "Good Morning, Sir!"
    elif 12 <= hour < 18:
        speak("Good Afternoon, Sir!")
        return "Good Afternoon, Sir!"
    speak("Good Evening, Sir!")
    return "Good Evening, Sir!"

def set_name():
    speak("What can I call you Sir?")
    user_name = listen().strip()
    user_profile["name"] = user_name
    speak(f"Hello, {user_name}! Nice to meet you.")
    return f"Name set to {user_name}."

def ask_mood():
    speak("How are you feeling today sir?")
    mood = listen().lower()
    if "happy" in mood:
        user_profile["mood"] = "happy"
        speak("I'm glad you're feeling happy! Happy to see you Happy My creator great Sir! Let's start our work")
        return "Mood set to happy."
    elif "sad" in mood:
        user_profile["mood"] = "sad"
        speak("I'm sorry to hear that. Let me know how I can help. Ohh, Don't worry sir Everything is temporary")
        return "Mood set to sad."
    elif "stressed" in mood:
        user_profile["mood"] = "stressed"
        speak("Take a deep breath. You're doing great Sir!")
        return "Mood set to stressed."
    speak("Got it Sir! Let me know how I can help you today.")
    return "Mood not recognized."

def add_task(task):
    todo_list.append({"task": task, "completed": False})
    speak(f"Got it, I've added the task '{task}' to your to-do list.")
    return f"Task '{task}' added."

def remove_task(task):
    for t in todo_list:
        if t["task"].lower() == task.lower() and not t["completed"]:
            todo_list.remove(t)
            speak(f"Alright, I've removed the task '{task}' from your to-do list.")
            return f"Task '{task}' removed."
    speak(f"Sorry, I couldn't find the task '{task}' in your to-do list.")
    return f"Task '{task}' not found."

def mark_task_completed(task):
    for t in todo_list:
        if t["task"].lower() == task.lower() and not t["completed"]:
            t["completed"] = True
            speak(f"Nice job Sir! You've completed the task '{task}'.")
            return f"Task '{task}' completed."
    speak(f"I couldn't find the task '{task}' or it's already completed.")
    return f"Task '{task}' not found or already completed."

def view_tasks():
    if todo_list:
        speak("Here are your tasks:")
        tasks = []
        for index, t in enumerate(todo_list, 1):
            status = "completed" if t["completed"] else "pending"
            speak(f"{index}. {t['task']} - {status}")
            tasks.append(f"{index}. {t['task']} - {status}")
        return "\n".join(tasks)
    speak("Your to-do list is empty. Let's add some tasks Sir!")
    return "To-do list is empty."

def tell_gk_fact():
    facts = [
        "The Great Wall of China is not visible from space without aid.",
        "Honey never spoils. Archaeologists have found pots of honey in ancient tombs.",
        "A leap year happens every 4 years, except for years divisible by 100 but not 400.",
        "The Eiffel Tower can grow more than 6 inches in summer due to thermal expansion.",
        "Octopuses have three hearts and blue blood.",
        "Hot water will turn into ice faster than cold water.",
        "The Mona Lisa has no eyebrows.",
        "The strongest muscle in the body is the tongue.",
        "Ants take rest for around 8 Minutes in 12-hour period.",
        "The most common name in the world is Mohammed.",
        "Minus 40 degrees Celsius is exactly the same as minus 40 degrees Fahrenheit.",
        "Women blink nearly twice as much as men!",
        "People say 'Bless you' when you sneeze because when you sneeze, your heart stops for a millisecond.",
        "It is physically impossible for pigs to look up into the sky"
    ]
    fact = random.choice(facts)
    speak(f"Here's a fun fact: {fact}")
    return fact

def ask_gk_question():
    questions = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who developed the theory of relativity?", "answer": "Albert Einstein"},
        {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare"},
        {"question": "What is the tallest mountain in the world?", "answer": "Mount Everest"}
    ]
    question = random.choice(questions)
    speak(question["question"])
    answer = listen().strip()
    if answer.lower() == question["answer"].lower():
        speak("Correct! Well done, Sir!")
        return "Correct!"
    speak(f"Oops, that's incorrect. The correct answer is {question['answer']}.")
    return f"Incorrect. Correct answer: {question['answer']}."

def motivation():
    quotes = [
        "Sir, greatness is your destiny. Keep pushing forward!",
        "Success is not final, failure is not fatal: It is the courage to continue that counts.",
        "Sir, your dreams are valid, and your efforts will make them a reality.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "Your focus and dedication will lead you to unmatched success, Sir!.",
        "Don’t watch the clock; do what it does. Keep going Sir!.",
        "Sir, you are brilliant, and no obstacle can stop your vision for greatness.",
        "Believe in yourself because the world already sees your potential Sir!.",
        "Your limitation—it’s only your imagination. Push past it!",
        "Sir, each day brings you closer to building a legacy that will inspire generations."
    ]
    selected_quote = choice(quotes)
    speak(selected_quote)
    return selected_quote

def set_reminder():
    speak("What reminder would you like to set Sir?")
    reminder = listen().strip()
    if reminder:
        reminders.append(reminder)
        speak(f"Reminder set: {reminder}.")
        return f"Reminder set: {reminder}."
    speak("Please provide a valid reminder Sir.")
    return "Invalid reminder."

def check_reminders():
    if reminders:
        speak("Here are your reminders:")
        for reminder in reminders:
            speak(reminder)
        return "\n".join(reminders)
    speak("You have no reminders set Sir.")
    return "No reminders set."

def open_instagram():
    speak("Opening Instagram Sir.")
    webbrowser.open("https://www.instagram.com")
    return "Opening Instagram."

def open_facebook():
    speak("Opening Facebook Sir.")
    webbrowser.open("https://www.facebook.com")
    return "Opening Facebook."

def search_youtube():
    speak("What would you like to search on YouTube, Sir?")
    search_query = listen().strip()
    if search_query:
        search_url = f"https://www.youtube.com/results?search_query={search_query}"
        speak(f"Searching for '{search_query}' on YouTube, Sir.")
        webbrowser.open(search_url)
        return f"Searching for '{search_query}' on YouTube."
    speak("Please provide a valid search query Sir.")
    return "Invalid search query."

def show_functions():
    functions_list = [
        "1:Open a file",
        "2:Open Notepad",
        "3:Open calculator",
        "4:Open chrome",
        "5:Open word",
        "6:Open excel",
        "7:Open photoshop",
        "8:Open file explorer",
        "9:Open Instagram",
        "10:Open facebook",
        "11:Open Email",
        "12:search youtube for(anything you want to search)",
        "13:play music on youtube",
        "14:set name",
        "15:set reminder",
        "16:check reminders",
        "17:add task",
        "18:view tasks",
        "19:ask mood",
        "20:create file",
        "21:organize files",
        "22:bulk rename",
        "23:backup files",
        "24:restore files",
        "25:search files",
        "26:find duplicates",
        "27:change permissions",
        "28:compress file",
        "29:extract file",
        "30:encrypt file",
        "31:decrypt file",
        "32:schedule cleanup",
        "33:upload to cloud",
        "34:delete file",
        "35:rename file",
        "36:calculator",
        "37:check disk space",
        "38:Provide general knowledge",
        "39:tell me a fact",
        "40:Greet based on the time of day",
        "41:search for 'the place you want to go on'",
        "42:Directions to 'place you want to go on' from 'The place you are on'",
        "43:open amazon",
        "44:open flipkart",
        "45:open myntra",
        "46:open shopify",
        "47:open snapdeal",
        "48:search google for(anything you want to search)",
        "49:scroll down",
        "50:scroll up",
        "51:start Dictating(but first open notepad or word and then say start writing say 'stop' to stop writing",
        "52:open chatGPT",
        "53:shut down",
        "54:restart",
        "55:virtual pet"
    ]
    speak("Here are the functions I can perform, Sir:")
    for function in functions_list:
        speak(function)
    return "\n".join(functions_list)

def search_google(query):
    formatted_query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={formatted_query}"
    subprocess.run(["start", url], shell=True)
    return f"Searching Google for {query}."

def search_youtube(query):
    formatted_query = query.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={formatted_query}"
    subprocess.run(["start", url], shell=True)
    return f"Searching YouTube for {query}."

def open_chatgpt():
    speak("Opening ChatGPT...")
    subprocess.run(["start", "https://chat.openai.com/"], shell=True)
    return "Opening ChatGPT."

def shut_down():
    speak("Shutting down the computer...")
    subprocess.run(["shutdown", "/s", "/f", "/t", "1"], shell=True)
    return "Shutting down computer."

def restart():
    speak("Restarting the computer...")
    subprocess.run(["shutdown", "/r", "/f", "/t", "1"], shell=True)
    return "Restarting computer."

class MindfulnessCoach:
    def __init__(self):
        self.breathing_steps = [
            "Sir we are doing this for nearly one minute so please focus! Breathe in slowly for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly for 4 seconds.",
            "Breathe in slowly for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly for 4 seconds.",
            "Breathe in slowly for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly for 4 seconds.",
            "Breathe in slowly for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly for 4 seconds.",
            "Breathe in slowly for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly for 4 seconds.",
        ]
        self.meditation_guides = [
            "Sit comfortably, close your eyes, and focus on your breathing.",
            "Focus on each inhale and exhale, letting go of distractions.",
            "If your mind wanders, gently bring your attention back to your breath."
        ]
        self.relaxation_prompts = [
            "Take a moment to focus on how your body feels. Are you tense anywhere?",
            "Imagine yourself in a peaceful place. Visualize the sights, sounds, and smells around you.",
            "Close your eyes and breathe deeply. Focus only on the sensation of your breath entering and leaving your body."
        ]

    def guide_breathing(self):
        speak("Starting breathing exercise. Follow my instructions Sir.")
        for step in self.breathing_steps:
            speak(step)
            time.sleep(4)
        speak("Breathing exercise complete. Take a moment to relax Sir!")
        return "Breathing exercise completed."

    def guide_meditation(self):
        speak("Starting meditation. Relax and focus.")
        for guide in self.meditation_guides:
            speak(guide)
            time.sleep(5)
        speak("Meditation session complete. Take your time to relax.")
        return "Meditation session completed."

    def give_relaxation_prompt(self):
        prompt = random.choice(self.relaxation_prompts)
        speak(prompt)
        return prompt

    def check_mood(self, mood):
        if mood.lower() in ["stressed", "anxious", "overwhelmed"]:
            return self.guide_breathing()
        elif mood.lower() in ["tired", "bored"]:
            return self.give_meditation()
        return self.give_relaxation_prompt()

class VirtualPet:
    def __init__(self, name):
        self.name = name
        self.happiness = 50
        self.hunger = 50
        self.health = 100
        self.age = 0
        self.mood = "Neutral"

    def feed(self):
        self.hunger = 100
        self.happiness += 10
        self.mood = "Happy"
        speak(f"{self.name} has been fed. Happiness increased!")
        return f"{self.name} has been fed. Happiness increased!"

    def play(self):
        self.happiness += 20
        self.health += 5
        self.mood = "Playful"
        speak(f"You played with {self.name}. Happiness and health increased!")
        return f"You played with {self.name}. Happiness and health increased!"

    def check_status(self):
        if self.happiness < 30:
            self.mood = "Sad"
        elif self.happiness >= 30 and self.happiness < 60:
            self.mood = "Neutral"
        else:
            self.mood = "Happy"
        if self.hunger < 30:
            self.mood = "Hungry"
        speak(f"{self.name}'s Mood: {self.mood}\nHealth: {self.health} | Happiness: {self.happiness} | Hunger: {self.hunger}")
        return f"{self.name}'s Mood: {self.mood}\nHealth: {self.health} | Happiness: {self.happiness} | Hunger: {self.hunger}"

    def age_up(self):
        self.age += 1
        self.happiness -= 5
        self.hunger -= 10
        self.health -= 5
        speak(f"{self.name} grew older! Age: {self.age}")
        return f"{self.name} grew older! Age: {self.age}"

pet_name = "NOVA Pet"
pet = VirtualPet(pet_name)

def start_dictation():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    speak("I am ready to dictate Sir. Please speak into the microphone.")
    dictating = True
    while dictating:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            if "stop" in command.lower():
                speak("Stopping dictation.")
                dictating = False
            else:
                pyautogui.typewrite(command)
        except sr.UnknownValueError:
            print("Sorry, I could not understand that.")
        except sr.RequestError:
            print("Issue with speech recognition service.")
    return "Dictation stopped."

def increase_volume(times=11):
    for _ in range(times):
        pyautogui.press("volumeup")
        time.sleep(0.1)
    speak("Volume increased, Sir.")
    return "Volume increased."

def decrease_volume(times=7):
    for _ in range(times):
        pyautogui.press("volumedown")
        time.sleep(0.1)
    speak("Volume decreased, Sir.")
    return "Volume decreased."

def mute_volume():
    pyautogui.press("volumemute")
    speak("Volume muted, Sir.")
    return "Volume muted."

def close_application(app_name):
    os.system(f"taskkill /f /im {app_name}.exe")
    speak(f"{app_name.capitalize()} has been closed, Sir.")
    return f"{app_name.capitalize()} closed."

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '').lower()
    response = ""

    if "show your functions" in command or "what can you do" in command:
        response = show_functions()
    elif "open" in command or "kardo" in command or "kar do" in command or "kholdo" in command or "khol do" in command or "shuru" in command or "chalu" in command or "karo" in command or "kholo" in command or "chalu karo" in command or "shuru karo" in command or "start" in command or "open karo" in command:
        if "file" in command:
            response = open_file()
        elif "notepad" in command:
            subprocess.run(["start", "notepad"], shell=True)
            response = "Opening Notepad Sir..."
        elif "calculator" in command:
            subprocess.run(["start", "calc"], shell=True)
            response = "Opening Calculator Sir..."
        elif "chat gpt" in command:
            response = open_chatgpt()
        elif "chrome" in command:
            subprocess.run(["start", "chrome"], shell=True)
            response = "Opening Chrome Sir..."
        elif "word" in command:
            subprocess.run(["start", "winword"], shell=True)
            response = "Opening Word Sir..."
        elif "excel" in command:
            subprocess.run(["start", "excel"], shell=True)
            response = "Opening Excel Sir..."
        elif "photoshop" in command:
            subprocess.run(["start", "photoshop"], shell=True)
            response = "Opening Photoshop Sir..."
        elif "file explorer" in command:
            subprocess.run(["start", "explorer"], shell=True)
            response = "Opening File Explorer Sir..."
        elif "instagram" in command:
            response = open_instagram()
        elif "facebook" in command:
            response = open_facebook()
        elif "youtube" in command:
            response = open_youtube()
        elif "email" in command or "check email" in command:
            response = open_email()
        elif "amazon" in command:
            webbrowser.open("https://www.amazon.com")
            response = "Opening Amazon Sir."
        elif "flipkart" in command:
            webbrowser.open("https://www.flipkart.com")
            response = "Opening Flipkart Sir."
        elif "shopify" in command:
            webbrowser.open("https://www.shopify.com")
            response = "Opening Shopify Sir."
        elif "snapdeal" in command:
            webbrowser.open("https://www.snapdeal.com")
            response = "Opening Snapdeal Sir."
        elif "myntra" in command:
            webbrowser.open("https://www.myntra.com")
            response = "Opening Myntra Sir."
    elif "close notepad" in command or "notepad band kar do" in command or "notepad band karo" in command:
        response = close_application("notepad")
    elif "close calculator" in command or "calculator band kar do" in command or "calculator band karo" in command:
        response = close_application("calc")
    elif "close chrome" in command or "chrome band kar do" in command or "calculator band karo" in command:
        response = close_application("chrome")
    elif "close word" in command or "word band kar do" in command or "word band karo" in command:
        response = close_application("winword")
    elif "close excel" in command or "excel band kar do" in command or "excel band karo" in command:
        response = close_application("excel")
    elif "close photoshop" in command or "photoshop band kar do" in command or "photoshop band karo" in command:
        response = close_application("photoshop")
    elif "close file explorer" in command or "file explorer band kar do" in command or "file explorer band karo" in command:
        response = close_application("explorer")
    elif "search for" in command:
        location = command.replace("search for", "").strip()
        response = search_google_maps(location)
    elif "way to" in command or "directions to" in command:
        locations = command.replace("directions to", "").strip().split(" from ")
        if len(locations) == 2:
            start_location, end_location = locations
            response = get_directions(start_location, end_location)
        else:
            response = "Please provide start and end locations."
    elif "google for" in command or "google karo" in command:
        search_query = command.replace("google for", "").strip()
        if search_query:
            response = search_google(search_query)
        else:
            response = "Please specify what to search for."
    elif "search youtube for" in command or "youtube karo" in command:
        search_query = command.replace("search youtube for", "").strip()
        if search_query:
            response = search_youtube(search_query)
        else:
            response = "Please specify what to search for on YouTube."
    elif "play music" in command or "gana bajao" in command or "gana chalao" in command or "gana shuru karo" in command or "gana lagao" in command:
        response = play_random_music()
    elif "play rock music" in command or "tadakta fadakta gana bajao" in command or "tadakta fadakta gana lagao" in command or "tadakta fadakta gana shuru karo" in command or "tadakta fadakta gana chalu karo" in command or "tufani gana bajao" in command or "joshila gana bajao" in command or "joshila gana lagao" in command or "joshila gana" in command or "joshila music" in command or "joshila song" in command:
        response = play_rock_music()
    elif "play romantic music" in command or "love music" in command or "romantic music" in command or "romantic" in command:
        response = play_romantic_music()
    elif "start dictating" in command or "likhna chalu karo" in command or "likho" in command or "likhna shuru karo" in command or "likhna start karo" in command:
        response = start_dictation()
    elif "feed the pet" in command or "pet ko khana khilao" in command:
        response = pet.feed()
    elif "play with the pet" in command or "pet ke sath khelo" in command:
        response = pet.play()
    elif "check pets status" in command:
        response = pet.check_status()
    elif "age up the pet" in command:
        response = pet.age_up()
    elif "breathing exercise" in command or "rest karna hai" in command or "shant karo mujhe" in command:
        response = MindfulnessCoach().guide_breathing()
    elif "meditate" in command or "meditation" in command or "josh" in command:
        response = MindfulnessCoach().guide_meditation()
    elif "relax" in command or "focus" in command:
        response = MindfulnessCoach().give_relaxation_prompt()
    elif "motivate" in command or "motivation" in command:
        response = motivation()
    elif "check my mood" in command or "mood check karo" in command:
        response = ask_mood()
    elif "set name" in command or "mera naam batao" in command:
        response = set_name()
    elif "scroll down" in command or "niche karo" in command or "nichekaro" in command:
        pyautogui.press('pagedown')
        response = "Scrolled down."
    elif "scroll up" in command or "upar karo" in command or "uparkaro" in command:
        pyautogui.press('pageup')
        response = "Scrolled up."
    elif "shut down" in command or "shutdown" in command:
        response = shut_down()
    elif "restart" in command:
        response = restart()
    elif "set reminder" in command or "reminder lagao" in command:
        response = set_reminder()
    elif "reminders" in command or "see reminders" in command:
        response = check_reminders()
    elif "add task" in command or "task add karo" in command:
        task = command.replace("add task", "").strip()
        if task:
            response = add_task(task)
        else:
            response = "Please specify a task."
    elif "view tasks" in command or "tasks dekho" in command or "check tasks" in command:
        response = view_tasks()
    elif "create file" in command or "file banao" in command or "file create karo" in command or "file bana do" in command or "file create" in command or "make a file" in command or "make file" in command:
        response = create_file()
    elif "organize files" in command or "file organize" in command:
        response = organize_files()
    elif "bulk rename" in command:
        response = bulk_rename_files()
    elif "backup files" in command:
        response = backup_files()
    elif "restore files" in command:
        response = restore_files()
    elif "search files" in command:
        response = search_files()
    elif "find duplicates" in command:
        response = find_duplicate_files()
    elif "change permissions" in command:
        response = change_file_permissions()
    elif "compress file" in command:
        response = compress_file()
    elif "extract file" in command:
        response = extract_file()
    elif "encrypt file" in command:
        response = encrypt_file()
    elif "decrypt file" in command:
        response = decrypt_file()
    elif "schedule cleanup" in command:
        response = schedule_cleanup()
    elif "upload to cloud" in command:
        response = cloud_storage_upload()
    elif "delete file" in command:
        response = delete_file()
    elif "rename file" in command or "file rename" in command or "file ko naam do" in command:
        response = rename_file()
    elif "calculate" in command or "calculation" in command:
        response = calculator()
    elif "check disk space" in command or "disk mein kitni jagah bachi hai" in command or "kitni space bachi hai" in command or "kitni space khali hai" in command or "space kitni hai" in command or "space batao" in command or "check space" in command or "space check" in command:
        response = check_disk_space()
    elif "web search" in command or "find" in command or "search this" in command:
        query = command.replace("web search", "").strip()
        if query:
            response = web_search(query)
        else:
            response = "Please specify what to search."
    elif "alert" in command:
        team = command.split()[-1]
        response = emergency_helper_alert(team)
    elif "tell me a fact" in command or "fact" in command or "interseting batao" in command or "interesting sa batao" in command:
        response = tell_gk_fact()
    elif "ask me a question" in command or "sawal" in command or "question" in command or "sawaal" in command:
        response = ask_gk_question()
    elif "greet" in command:
        response = greet_user()
    elif "good night" in command:
        response = "Good Night, Sir! Sleep well without any tension, because I am here to take your tension."
    elif "good morning" in command:
        response = "Good Morning, Sir! I am with you all the Time."
    elif "good evening" in command:
        response = "Good Evening, Sir! I hope your day went well."
    else:
        response = "Sorry, Sir please say it clearly."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)