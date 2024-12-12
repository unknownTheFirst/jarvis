import speech_recognition as sr

recognizer = sr.Recognizer()

def get_vtt():
    """
    Captures voice input and transcribes it using Google Speech Recognition.
    Returns the transcribed text or an empty string if transcription fails.
    """
    with sr.Microphone() as source:
        print("Speak now...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""  # Return empty string if audio is not understood
        except sr.RequestError as e:
            print(f"Request failed: {e}")
            return ""  # Return empty string if there is a request error
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""  # Catch other exceptions
