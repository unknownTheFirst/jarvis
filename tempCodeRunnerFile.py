import os
import threading
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from prompt_engeneering import jarvis_personality
import voice
from speech_to_text import get_vtt
import customtkinter as ctk

# Load environment variables
_ = load_dotenv(find_dotenv())

# Create OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define the model
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5

# Conversation history
conversation_history = [
    {"role": "system", "content": jarvis_personality}
]

# Initialize global mode
current_mode = "txt"  # Default to text mode


def get_response(prompt):
    """
    Fetch response from OpenAI API.
    """
    try:
        conversation_history.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history,
            temperature=TEMPERATURE
        )
        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message
    except Exception as e:
        return f"Error: {str(e)}"


class JarvisApp(ctk.CTk):
    """
    A customtkinter GUI for the Jarvis assistant.
    """

    def __init__(self):
        super().__init__()
        self.title("Jarvis Assistant")
        
        # Full-screen mode
        self.attributes('-fullscreen', True)

        # Configure appearance
        ctk.set_appearance_mode("dark")  # Modes: "dark", "light"
        ctk.set_default_color_theme("dark-blue")  # Themes: "blue", "dark-blue", "green"

        # Bind Escape key to exit full-screen mode
        self.bind("<Escape>", self.exit_fullscreen)

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Chat History (ScrolledText equivalent)
        self.chat_history = ctk.CTkTextbox(self.main_frame, wrap="word", height=400, state="disabled")
        self.chat_history.pack(fill="both", expand=True, pady=10, padx=10)

        # Entry Frame (for user input and buttons)
        self.entry_frame = ctk.CTkFrame(self.main_frame)
        self.entry_frame.pack(fill="x", pady=10, padx=10)

        # User Input Entry (Text Mode)
        self.user_input = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your message here...")
        self.user_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.user_input.bind("<Return>", self.submit_text_input)

        # Buttons
        self.submit_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.submit_text_input)
        self.submit_button.pack(side="left", padx=5, pady=5)

        self.listen_button = ctk.CTkButton(self.entry_frame, text="Listen", command=self.start_listening, state="disabled")
        self.listen_button.pack(side="left", padx=5, pady=5)

        self.switch_button = ctk.CTkButton(self.entry_frame, text="Switch to Voice", command=self.switch_mode)
        self.switch_button.pack(side="left", padx=5, pady=5)

        self.exit_button = ctk.CTkButton(self.entry_frame, text="Exit", command=self.exit_application)
        self.exit_button.pack(side="left", padx=5, pady=5)

    def log_message(self, role, message):
        """
        Logs messages to the chat history.
        """
        self.chat_history.configure(state="normal")
        if role == "user":
            self.chat_history.insert("end", f"You: {message}\n")
        elif role == "assistant":
            self.chat_history.insert("end", f"Jarvis: {message}\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def submit_text_input(self, event=None):
        """
        Handles text input submission.
        """
        prompt = self.user_input.get().strip()
        if not prompt:
            return
        if prompt.lower() == "exit":
            self.exit_application()
            return
        if prompt.lower() == "switch to voice":
            self.switch_mode()
            return

        self.log_message("user", prompt)
        self.user_input.delete(0, "end")

        # Fetch response in a separate thread
        threading.Thread(target=self.fetch_response, args=(prompt,)).start()

    def fetch_response(self, prompt):
        """
        Fetch assistant's response and log it.
        """
        response = get_response(prompt)
        self.log_message("assistant", response)

    def start_listening(self):
        """
        Handles voice input and fetches a response.
        """
        threading.Thread(target=self.process_voice_input).start()

    def process_voice_input(self):
        """
        Fetches and processes voice input.
        """
        prompt = get_vtt()
        if not prompt.strip():
            self.log_message("assistant", "I couldn't understand that. Please try again.")
            return

        if prompt.lower() == "exit":
            self.exit_application()
            return
        if prompt.lower() == "switch to text":
            self.switch_mode()
            return

        self.log_message("user", prompt)
        self.fetch_response(prompt)

    def switch_mode(self):
        """
        Switch between text and voice modes.
        """
        global current_mode
        if current_mode == "txt":
            current_mode = "voice"
            self.user_input.configure(state="disabled")
            self.listen_button.configure(state="normal")
            self.switch_button.configure(text="Switch to Text")
        else:
            current_mode = "txt"
            self.user_input.configure(state="normal")
            self.listen_button.configure(state="disabled")
            self.switch_button.configure(text="Switch to Voice")

    def exit_fullscreen(self, event=None):
        """
        Exit full-screen mode when the Escape key is pressed.
        """
        self.attributes('-fullscreen', False)

    def exit_application(self):
        """
        Exits the application.
        """
        self.destroy()


def main():
    """
    Initializes the customtkinter GUI.
    """
    app = JarvisApp()
    app.mainloop()


if __name__ == "__main__":
    main()
