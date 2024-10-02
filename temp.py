import speech_recognition as sr
import spacy
from gtts import gTTS
from playsound import playsound

nlp = spacy.load("en_core_web_sm")

# Initialize custom vocabulary and user feedback history
custom_vocabulary = []
user_feedback = []

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak...")
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio)
            print("Transcription: " + text)
            return text
        except sr.UnknownValueError:
            print("Speech recognition could not understand the audio")
        except sr.RequestError as e:
            print("Error with the speech recognition service: {0}".format(e))
    
    return ""

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    playsound("output.mp3") 

def add_custom_vocabulary(new_phrase):
    """Add a new phrase to the custom vocabulary."""
    if new_phrase and new_phrase not in custom_vocabulary:
        custom_vocabulary.append(new_phrase)
        print("Updated Vocabulary:", custom_vocabulary)

def provide_feedback(transcribed_text, correct_text):
    """Provide feedback for misrecognized words."""
    if transcribed_text != correct_text:
        print(f"Feedback: Correcting '{transcribed_text}' to '{correct_text}'")
        add_custom_vocabulary(correct_text)
        user_feedback.append((transcribed_text, correct_text))

if __name__ == "__main__":
    transcribed_text = speech_to_text()
    
    if transcribed_text:
        print("Was the transcription correct? (yes/no)")
        feedback = input().strip().lower()

        if feedback == 'no':
            correct_text = input("Please enter the correct text: ")
            provide_feedback(transcribed_text, correct_text)
            text_to_speech(correct_text)
        else:
            text_to_speech(transcribed_text)

        print("Custom Vocabulary:", custom_vocabulary)