import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import threading
import os

custom_vocabulary = []
user_feedback = []

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        update_status("Listening...", listening_icon)
        audio = recognizer.listen(source)
        
        try:
            update_status("Transcribing...", transcribing_icon)
            text = recognizer.recognize_google(audio)
            update_status("Transcription Complete", ready_icon)
            transcription_text.delete('1.0', ctk.END)
            transcription_text.insert(ctk.END, text)
            threading.Thread(target=text_to_speech, args=(text,)).start()
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Speech recognition could not understand the audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from the speech recognition service; {e}")
        finally:
            update_status("Ready", ready_icon)

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")

def play_audio():
    if os.path.exists("output.mp3"):
        playsound("output.mp3")
    else:
        messagebox.showwarning("No Audio", "No audio file found. Please generate audio first.")

def submit_feedback():
    transcribed_text = transcription_text.get('1.0', ctk.END).strip()
    correct_text = correct_text_entry.get('1.0', ctk.END).strip()
    if correct_text:
        with open('user_feedback.txt', 'a') as file:
            file.write(f"Transcribed Text: {transcribed_text}\n")
            file.write(f"Corrected Text: {correct_text}\n")
            file.write('-' * 50 + '\n')
        messagebox.showinfo("Feedback Saved", "Thank you for your feedback!")
        transcription_text.delete('1.0', ctk.END)
        correct_text_entry.delete('1.0', ctk.END)
        feedback_entry_frame.grid_remove()
        feedback_var.set('yes')
        start_speech_recognition()
    else:
        messagebox.showwarning("No Input", "Please enter the correct output.")

def start_speech_recognition():
    threading.Thread(target=speech_to_text).start()

def on_feedback_change(value):
    feedback_var.set(value)
    if value == 'no':
        feedback_entry_frame.grid()
    else:
        feedback_entry_frame.grid_remove()
        transcription_text.delete('1.0', ctk.END)
        messagebox.showinfo("Thank You", "Please provide another translation.")
        start_speech_recognition()

def update_status(message, icon):
    status_label.configure(text=message, image=icon)
    root.update()

def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

def show_splash_screen():
    import tkinter as tk
    from tkinter import ttk 

    root.withdraw()

    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry('800x600')
    center_window(splash)

    # Create a frame
    splash_frame = tk.Frame(splash, bg="#242424")
    splash_frame.pack(fill="both", expand=True)

    text = "Team \nBrainstorm \nBrigade"
    # label = tk.Label(splash_frame, text="", font=("Segoe UI", 50, "bold"), fg="white", bg="#2e2e2e")\
    label = tk.Label(splash, text="", font=("ROG Fonts", 40, "bold"), fg="#1F6AA5", bg='#242424')
    label.place(relx=0.5, rely=0.3, anchor='center')

    # Load the animated GIF
    gif_frames = []

    try:
        gif_image = Image.open('loading.gif')
        for frame in range(gif_image.n_frames):
            gif_image.seek(frame)
            frame_image = ImageTk.PhotoImage(gif_image.copy().resize((64, 64)))
            gif_frames.append(frame_image)
    except Exception as e:
        print(f"Error loading GIF: {e}")
        gif_frames = None

    gif_label = tk.Label(splash_frame, bg="#242424")
    gif_label.place(relx=0.5, rely=0.6, anchor='center')

    def animate(frame_index=0):
        if gif_frames:
            frame = gif_frames[frame_index]
            gif_label.configure(image=frame)
            gif_label.image = frame  # Possibly for preventing garbage collection -> just safety
            frame_index = (frame_index + 1) % len(gif_frames)
            splash.after(100, animate, frame_index)
        else:
            progress_bar = ttk.Progressbar(splash_frame, orient='horizontal', mode='indeterminate', length=400)
            progress_bar.place(relx=0.5, rely=0.6, anchor='center')
            progress_bar.start()

    def animate_text(index=0):
        if index <= len(text):
            label.config(text=text[:index])
            splash.after(200, animate_text, index + 1)
        else:
            animate()

    animate_text()

    def close_splash():
        splash.destroy()
        root.deiconify()

    splash.after(9000, close_splash)

    splash.mainloop()

def main_app():
    global root, status_label, transcription_text, feedback_var, vocab_listbox
    global feedback_entry_frame, correct_text_entry
    global listening_icon, transcribing_icon, ready_icon

    root.title("Speech Recognition App")
    root.geometry("800x600")
    root.resizable(True, True)

    # Load icons
    listening_icon = ctk.CTkImage(Image.open('listening.png'), size=(24, 24))
    transcribing_icon = ctk.CTkImage(Image.open('transcribing.png'), size=(24, 24))
    ready_icon = ctk.CTkImage(Image.open('ready.png'), size=(24, 24))

    # Configure grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=0)
    root.grid_rowconfigure(4, weight=1)
    root.grid_rowconfigure(5, weight=0)
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)

    # Transcription Label and Text
    transcription_label = ctk.CTkLabel(root, text="Transcription:", font=ctk.CTkFont(size=16, weight="bold"))
    transcription_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='ne')
    transcription_text = ctk.CTkTextbox(root)
    transcription_text.grid(row=0, column=1, padx=10, pady=(10, 5), sticky='nsew')

    # Feedback Frame (Yes/No Buttons)
    feedback_frame = ctk.CTkFrame(root)
    feedback_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

    feedback_label = ctk.CTkLabel(feedback_frame, text="Was the transcription correct?", font=ctk.CTkFont(size=16, weight="bold"))
    feedback_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    feedback_var = ctk.StringVar(value='yes')

    yes_button = ctk.CTkButton(feedback_frame, text="Yes", command=lambda: on_feedback_change('yes'), width=100)
    yes_button.grid(row=0, column=1, padx=5, pady=5)
    no_button = ctk.CTkButton(feedback_frame, text="No", command=lambda: on_feedback_change('no'), width=100)
    no_button.grid(row=0, column=2, padx=5, pady=5)

    # Feedback Entry Frame (initially hidden)
    feedback_entry_frame = ctk.CTkFrame(root)
    feedback_entry_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
    feedback_entry_frame.grid_remove()  

    feedback_entry_frame.columnconfigure(1, weight=1)

    # Correct Text Label and Entry
    correct_text_label = ctk.CTkLabel(feedback_entry_frame, text="Correct Output:", font=ctk.CTkFont(size=16, weight="bold"))
    correct_text_label.grid(row=0, column=0, padx=5, pady=5, sticky='ne')
    correct_text_entry = ctk.CTkTextbox(feedback_entry_frame)
    correct_text_entry.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

    # Submit Feedback Button
    submit_feedback_button = ctk.CTkButton(feedback_entry_frame, text="✔ Submit Feedback", command=submit_feedback, width=150)
    submit_feedback_button.grid(row=1, column=1, padx=5, pady=5, sticky='e')

    # Buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    listen_button = ctk.CTkButton(button_frame, text="🎤 Listen", command=start_speech_recognition, width=150)
    listen_button.grid(row=0, column=0, padx=5)

    play_audio_button = ctk.CTkButton(button_frame, text="▶ Play Audio", command=play_audio, width=150)
    play_audio_button.grid(row=0, column=1, padx=5)

    # Custom Vocabulary Label and Listbox
    vocab_label = ctk.CTkLabel(root, text="Custom Vocabulary:", font=ctk.CTkFont(size=16, weight="bold"))
    vocab_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky='ne')
    vocab_listbox = ctk.CTkTextbox(root)
    vocab_listbox.grid(row=4, column=1, padx=10, pady=(10, 5), sticky='nsew')

    # Status Label
    status_label = ctk.CTkLabel(root, text="Ready", image=ready_icon, compound='left', font=ctk.CTkFont(size=18, weight="bold"))
    status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='we')

    center_window(root)

if __name__ == "__main__":
    root = ctk.CTk()
    main_app()
    show_splash_screen()
    try:
        root.mainloop()
    except Exception as e:
        pass
