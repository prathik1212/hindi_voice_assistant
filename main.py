import sounddevice as sd
import queue
import json
import time
import os
import psutil
from vosk import Model, KaldiRecognizer


WAKE_WORD = "सुनो"
EXIT_WORD = "अलविदा"
PRIVACY_WORD = "प्राइवेसी मोड चालू"
REPORT_WORD = "रिपोर्ट बताओ"
CPU_WORD = "सीपीयू बताओ"
RAM_WORD = "रैम बताओ"

privacy_mode = False
assistant_active = False

model_path = "model"  # Make sure VOSK Hindi model is downloaded here
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def speak(text):
    print("Assistant:", text)
    os.system(f'espeak-ng -v hi -s 140 "{text}"')  


def get_response(text):
    global privacy_mode
    global assistant_active

    if WAKE_WORD in text:
        assistant_active = True
        return "जी, मैं सुन रहा हूँ"

    if EXIT_WORD in text:
        speak("अलविदा, धन्यवाद")
        exit()

    if not assistant_active:
        return None

    if PRIVACY_WORD in text:
        privacy_mode = True
        return "प्राइवेसी मोड चालू कर दिया गया है"

    if privacy_mode:
        return "प्राइवेसी मोड चालू है, मैं आपकी जानकारी साझा नहीं करूंगा"

    if CPU_WORD in text:
        cpu = psutil.cpu_percent()
        return f"सीपीयू उपयोग वर्तमान में {cpu} प्रतिशत है"

    if RAM_WORD in text:
        ram = psutil.virtual_memory().percent
        return f"रैम उपयोग वर्तमान में {ram} प्रतिशत है"

    if REPORT_WORD in text:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        latency = round(time.time() - start_time_global, 2)
        return (f"प्रदर्शन रिपोर्ट:\nसीपीयू उपयोग: {cpu}%\nरैम उपयोग: {ram}%\n"
                f"उत्तर देने में समय: {latency} सेकंड\nसिस्टम सामान्य रूप से काम कर रहा है")

    if "समय" in text:
        return f"अभी का समय है {time.strftime('%H:%M')}"
    if "तारीख" in text:
        return f"आज की तारीख है {time.strftime('%d %B %Y')}"
    if "आपका नाम" in text:
        return "मेरा नाम हिंदी वॉइस असिस्टेंट है"
    if "कैसे हो" in text:
        return "मैं ठीक हूँ, धन्यवाद"
    if "धन्यवाद" in text:
        return "आपका स्वागत है"
    if "नमस्ते" in text:
        return "नमस्ते"
    if "भारत" in text:
        return "भारत एक महान देश है"
    if "मौसम" in text:
        return "मौसम की जानकारी ऑफलाइन उपलब्ध नहीं है"
    if "कौन" in text:
        return "मैं आपका सहायक हूँ"
    if "क्या कर सकते हो" in text:
        return "मैं कई कार्य कर सकता हूँ, जैसे समय बताना, रिपोर्ट देना, और अन्य आदेश सुनना"
    if "दिन" in text:
        return f"आज {time.strftime('%A')} है"
    if "महीना" in text:
        return f"अभी {time.strftime('%B')} महीना है"
    if "सप्ताह" in text:
        return f"अभी {time.strftime('%U')}वां सप्ताह चल रहा है"
    if "उठो" in text:
        return "मैं तैयार हूँ, आदेश सुन रहा हूँ"
    if "खेल" in text:
        return "मैं खेल की जानकारी अभी नहीं दे सकता"
    if "समाचार" in text:
        return "मैं ऑफलाइन हूँ, समाचार जानकारी उपलब्ध नहीं है"
    if "गीत" in text:
        return "मुझे गाना गाने का प्रशिक्षण नहीं मिला है"
    if "हास्य" in text:
        return "एक मजाक सुनिए: क्यों मछली कंप्यूटर के पास नहीं जाती? क्योंकि वह इंटरनेट में डरती है!"
    if "मित्र" in text:
        return "मैं आपका डिजिटल मित्र हूँ"
    if "सहायता" in text:
        return "आप किस प्रकार की मदद चाहते हैं?"
    
    return "क्षमा करें, मैं यह आदेश नहीं समझ पाया"


print("हिंदी वॉइस असिस्टेंट शुरू हो गया है...")
print(f"Wake word: {WAKE_WORD}")
print(f"Exit word: {EXIT_WORD}")

with sd.RawInputStream(samplerate=16000,
                       blocksize=8000,
                       dtype='int16',
                       channels=1,
                       callback=callback):

    while True:
        print("\n🎙 बोलिए...")
        start_time_global = time.time()

        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
        else:
            continue

        if not text.strip():
            print("कुछ नहीं सुना गया, फिर से बोलिए")
            continue

        print("You:", text)
        start_time = time.time()
        response = get_response(text)
        speak(response)
        end_time = time.time()

      
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        latency = round(end_time - start_time, 2)
        print("\n====== प्रदर्शन रिपोर्ट ======")
        print(f"Latency: {latency} सेकंड")
        print(f"CPU: {cpu}%")
        print(f"RAM: {ram}%")
        print("================================\n")
