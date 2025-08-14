import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import threading

DURATION = 5  # бичлэгийн хугацаа секундээр
FILENAME = "input.wav"

def record_audio():
    fs = 16000  # sample rate
    messagebox.showinfo("Бичлэг", "Бичлэг эхэллээ!")
    audio = sd.rec(int(DURATION * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(FILENAME, fs, audio)
    messagebox.showinfo("Бичлэг", "Бичлэг дууслаа!")

def transcribe(filename):
    with open(filename, 'rb') as f:
        audio = f.read()
    r = requests.post("https://api.chimege.com/v1.2/transcribe", data=audio, headers={
        'Content-Type': 'application/octet-stream',
        'Punctuate': 'true',
        'Token': '2e39f92b0c2faf8d4e1e2af0f9c929825cdb4f74dfae6c478c5e9a8825e102ef',
    })
    return r.content.decode("utf-8")

def start_record_and_transcribe():
    record_audio()
    result = transcribe(FILENAME)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

def threaded_action():
    threading.Thread(target=start_record_and_transcribe).start()

root = tk.Tk()
root.title("STT Demo")

record_btn = tk.Button(root, text="Мик асааж бичлэг хийх", command=threaded_action)
record_btn.pack(pady=10)

result_text = tk.Text(root, height=10, width=50)
result_text.pack(pady=10)

root.mainloop()
