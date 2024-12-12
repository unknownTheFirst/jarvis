import customtkinter as ctk
import threading
from main import JarvisAssistant
import os

class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Jarvis Assistant")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a label with a cool font
        self.jarvis_label = ctk.CTkLabel(self, text="JARVIS", font=("Segoe UI", 24, "bold"))
        self.jarvis_label.pack(pady=20)

        # Create a button to start the conversation
        self.start_button = ctk.CTkButton(self, text="Start Conversation", command=self.start_conversation)
        self.start_button.pack(pady=20)

        # Create a label to indicate speaking status
        self.speak_label = ctk.CTkLabel(self, text="Can Speak: ", font=("Segoe UI", 14))
        self.speak_label.pack(pady=20)
        self.speak_status = ctk.CTkLabel(self, text="❌", font=("Segoe UI", 14))  # Start with a cross emoji
        self.speak_status.pack(pady=20)

        self.assistant = None  # To hold the assistant instance

    def start_conversation(self):
        # Create an instance of the JarvisAssistant class
        self.assistant = JarvisAssistant(self.update_speak_status, self)  # Pass self as the second argument
        threading.Thread(target=self.run_assistant).start()  # Start assistant in a separate thread
        self.start_button.configure(state="disabled")  # Disable the button after starting

    def run_assistant(self):
        self.assistant.main()  # Run the main function of the assistant

    def update_speak_status(self, can_speak):
        # Update the GUI elements in a thread-safe way
        if can_speak:
            self.speak_status.configure(text="✅")  # Indicate ready to speak with a tick emoji
        else:
            self.speak_status.configure(text="❌")  # Indicate not ready to speak with a cross emoji

    def on_closing(self):
        if self.assistant:
            self.assistant.running = False  # Signal the assistant to stop
        self.destroy()

if __name__ == "__main__":
    gui = JarvisGUI()
    gui.mainloop()