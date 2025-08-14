import requests
import tkinter as tk
from tkinter import messagebox
import re
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import os
import platform

# --- TTS хэсэг ---
def sanitize_filename(text):
    # Файлын нэрэнд тохирохгүй тэмдэгтүүдийг арилгана
    filename = re.sub(r'[^\w\s-]', '', text)
    filename = filename.strip().replace(' ', '_')
    return filename or "output"

def synthesize(text, filename):
    url = "https://api.chimege.com/v1.2/synthesize"
    headers = {
        'Content-Type': 'plain/text',
        'Token': 'ce748d6923ceba4367468b4254626d49cb27ce46a0a6c66bed2e291df7b57633',
    }

    r = requests.post(
        url, data=text.encode('utf-8'), headers=headers)

    with open(filename, 'wb') as out:
        out.write(r.content)

def play_wav(filename):
    # WAV файлыг тоглуулах (Windows)
    if platform.system() == "Windows":
        import winsound
        winsound.PlaySound(filename, winsound.SND_FILENAME)
    else:
        # Linux/Mac-д өөр тоглуулагч ашиглаж болно
        os.system(f"aplay {filename}")

def on_synthesize():
    text = entry.get()
    if not text.strip():
        messagebox.showwarning("Анхаар", "Текст оруулна уу!")
        return
    filename = sanitize_filename(text) + ".wav"
    try:
        synthesize(text, filename)
        messagebox.showinfo("Амжилттай", f"{filename} файл үүслээ.")
        play_wav(filename)
    except Exception as e:
        messagebox.showerror("Алдаа", str(e))

# --- STT хэсэг ---
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
    # STT үр дүнг зөвхөн TTS талбарт бичнэ
    entry.delete(0, tk.END)
    entry.insert(0, result.strip())
    # Автоматаар синтез хийгээд тоглуулна
    text = result.strip()
    if text:
        filename = sanitize_filename(text) + ".wav"
        try:
            synthesize(text, filename)
            play_wav(filename)
        except Exception as e:
            messagebox.showerror("TTS Алдаа", str(e))

def threaded_action():
    threading.Thread(target=start_record_and_transcribe).start()

# --- UI хэсэг ---
root = tk.Tk()
root.title("Чимэгэ TTS & STT Demo")

# TTS хэсэг
tk.Label(root, text="Текстийг дуу болгох (TTS):").pack(padx=10, pady=(10, 0))
entry = tk.Entry(root, width=40)
entry.pack(padx=10, pady=5)
tk.Button(root, text="Синтез хийх", command=on_synthesize).pack(padx=10, pady=5)

# STT хэсэг
tk.Label(root, text="Дуу хоолойг текст болгох (STT):").pack(padx=10, pady=(15, 0))
record_btn = tk.Button(root, text="Мик асааж бичлэг хийх", command=threaded_action)
record_btn.pack(pady=5)

root.mainloop()
