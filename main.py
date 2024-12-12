import os
import threading
import time
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from prompt_engeneering import jarvis_personality
import pyttsx3
import voice
from speech_to_text import get_vtt

class JarvisAssistant:
    def __init__(self, gui_callback, gui_instance):
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Create OpenAI client
        self.client = OpenAI(api_key=None)
        
        # Define the model and temperature
        self.MODEL = "gpt-4o-mini"
        self.TEMPERATURE = 0.5
        
        # Conversation history to remember chat
        self.conversation_history = [
            {"role": "system", "content": jarvis_personality}
        ]
        
        self.running = True
        self.mode = "voice"
        self.speaking = False  # Track whether the assistant is currently speaking
        self.gui_callback = gui_callback  # Callback to update GUI
        self.gui_instance = gui_instance  # Store the GUI instance

    def get_response(self, prompt):
        try:
            # Add the user input to the conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Fetch the response
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.conversation_history,
                temperature=self.TEMPERATURE
            )

            # Extract the assistant's reply
            assistant_message = response.choices[0].message.content

            # Add assistant's response to the history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"

    def get_response_voice(self):
        """Handles voice-based user interaction."""
        while self.running:
            self.gui_callback(True)  # Notify GUI that the assistant is ready to speak
            print("Speak now...")  # Indicate that the assistant is ready for voice input
            prompt = get_vtt()
            self.gui_callback(False)  # Notify GUI that the assistant is no longer ready to speak
            
            if not prompt.strip():
                print("Voice input not recognized. Please try again.")
                voice.speak("I couldn't understand that. Please try again.")
                continue

            if prompt.lower() == "exit":
                print("See you next time!")
                voice.speak("See you next time!")
                self.gui_instance.on_closing()  # Close the GUI window
                break
            else:
                self.speaking = True  # Set speaking to True when responding
                response = self.get_response(prompt)
                print(f"Assistant: {response}")
                time.sleep(0.5)  # Prevents speech truncation
                voice.speak(response)
                self.speaking = False  # Set speaking to False after responding

    def is_ready_to_speak(self):
        """Returns whether the assistant is ready to speak."""
        return not self.speaking  # Returns True if not currently speaking

    def main(self):
        """Main function to initialize and manage modes."""
        print("Jarvis initiated")
        voice.speak("Jarvis initiated")

        self.mode = "voice"

        # Persistent mode handling
        while self.running:
            if self.mode == "voice":
                self.get_response_voice()

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.main()
    
