"""
Jarvis AI Assistant - Consolidated Version
"""

import os
import sys
import webbrowser
import datetime
import urllib.parse
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the script's directory
script_dir = Path(__file__).parent
env_path = script_dir / ".env"
load_dotenv(dotenv_path=env_path)

# ============================================
# CONFIGURATION FLAGS
# ============================================
USE_SPEECH_RECOGNITION = False  # Set to False to disable voice input
USE_CHATBOT = True            # Set to False to disable AI chat responses

# ============================================
# GEMINI AI SETUP
# ============================================
gemini_api_key = os.getenv("gemini_api_key")

if not gemini_api_key:
    print("WARNING: gemini_api_key not found in .env file!")
    print(f"Looking for .env at: {env_path}")
    print("Please create a .env file with: gemini_api_key=YOUR_KEY_HERE")
    model = None
else:
    genai.configure(api_key=gemini_api_key)
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        print("Error loading Gemini model:", e)
        model = None

# Chat history for context
chat_history = ""

# ============================================
# HELPER FUNCTIONS
# ============================================

def chat(query: str) -> str:
    """Handles AI-powered conversation with context."""
    global chat_history
    chat_history += f"User: {query}\nJarvis: "

    if USE_CHATBOT and model:
        try:
            response = model.generate_content(query)
            reply = response.text.strip() if hasattr(response, "text") else "Error: No valid AI response."
        except Exception as e:
            reply = f"AI error: {str(e)}"
    else:
        reply = "Chatbot is disabled. Set USE_CHATBOT = True to enable."

    print("Jarvis:", reply)
    chat_history += f"{reply}\n"
    return reply


def ai(prompt: str) -> None:
    """Generates AI response and saves it to a file."""
    if not model:
        print("AI model not available.")
        return

    try:
        response = model.generate_content(prompt)
        text = f"Gemini response for Prompt: {prompt}\n{'=' * 50}\n\n{response.text}"
        os.makedirs("Gemini", exist_ok=True)
        filename = f"Gemini/{prompt.replace(' ', '_')[:50]}.txt"  # Limit filename length
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Response saved to {filename}")
    except Exception as e:
        print("Error fetching AI response:", e)


def recognize_speech() -> str:
    """Captures and recognizes speech from the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio).lower()
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
        except sr.WaitTimeoutError:
            print("No speech detected within timeout.")
    return ""


def search_youtube(query: str) -> None:
    """Searches YouTube for a video based on the query."""
    search_query = query.replace("play", "").replace("on youtube", "").strip()
    if search_query:
        encoded_query = urllib.parse.quote(search_query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        print(f"Searching YouTube for: {search_query}")
        webbrowser.open(youtube_url)
    else:
        print("No valid search query detected.")


def process_command(query: str) -> bool:
    """
    Processes user commands and returns True if the program should continue,
    False if it should exit.
    """
    global chat_history

    # Predefined websites
    sites = {
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.com",
        "google": "https://www.google.com",
        "gemini": "https://gemini.google.com/app?hl=en-IN",
        "chat gpt": "https://chatgpt.com/",
        "chatgpt": "https://chatgpt.com/"
    }

    # Open predefined websites
    for site, url in sites.items():
        if f"open {site}" in query and "play" not in query:
            print(f"Opening {site}...")
            webbrowser.open(url)
            return True

    # Play a video on YouTube
    if "play" in query and "youtube" in query:
        search_youtube(query)
        return True

    # Get the current time
    if "the time" in query:
        now = datetime.datetime.now()
        print(f"The time is {now.strftime('%H:%M')}")
        return True

    # Open system applications (macOS-specific, but kept for compatibility)
    if "open facetime" in query:
        os.system("open /System/Applications/FaceTime.app")
        return True
    if "open pass" in query:
        os.system("open /Applications/Passky.app")
        return True

    # AI-based file generation
    if "using artificial intelligence" in query:
        ai(prompt=query)
        return True

    # Exit command
    if "jarvis quit" in query or "exit" in query or "quit" in query:
        print("Goodbye!")
        return False

    # Reset chat history
    if "reset chat" in query:
        chat_history = ""
        print("Chat history reset.")
        return True

    # Default: use chatbot
    if USE_CHATBOT:
        chat(query)
    else:
        print("Command not recognized. Chatbot is disabled.")

    return True


# ============================================
# MAIN ENTRY POINT
# ============================================

def main():
    """Main function to run the Jarvis AI assistant."""
    print("=" * 50)
    print("       Welcome to Jarvis A.I")
    print("=" * 50)
    print(f"Speech Recognition: {'Enabled' if USE_SPEECH_RECOGNITION else 'Disabled'}")
    print(f"Chatbot: {'Enabled' if USE_CHATBOT else 'Disabled'}")
    print("=" * 50)

    while True:
        print("\nSay something or type your command:")

        query = ""
        if USE_SPEECH_RECOGNITION:
            query = recognize_speech()

        if not query:
            query = input("Enter your command: ").strip().lower()

        if not query:
            continue

        should_continue = process_command(query)
        if not should_continue:
            break


if __name__ == "__main__":
    main()
