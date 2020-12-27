import pyaudio
import wave

# Parametrii audio si pentru fisierul de output
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# Porneste streamul
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []  # Lista finala in care scrie toate chunk-urile inregistrate de la microfon

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)  # Nu inregistreaza direct in fisier, il considera un stream
    frames.append(data)

print("* done recording")

# Inchide toate stream-urile
stream.stop_stream()
stream.close()
p.terminate()

# Scrie tot ce o inregistrat intr-un fisier
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()