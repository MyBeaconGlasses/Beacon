import pyaudio
import wave

# Audio settings
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(rate=RATE,
                format=FORMAT,
                channels=CHANNELS,
                input=True,
		input_device_index=1,
                frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Record for 5 seconds
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# Stop recording
stream.stop_stream()
stream.close()
p.terminate()

print("Finished recording.")

# Save the recorded data as a WAV file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Audio recorded successfully and saved to {WAVE_OUTPUT_FILENAME}")
