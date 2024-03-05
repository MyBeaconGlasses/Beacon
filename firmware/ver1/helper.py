import numpy as np
import shutil
import base64
import pyaudio
import cv2
import io
import wave
import miniaudio
from picamera2 import Picamera2

# mpv
import shutil

def is_installed(lib_name):
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True 

def play_audio_stream(audio_queue):
    """
    Function to be run in a separate thread for playing audio chunks.
    It takes a queue from which it will continuously read and play MP3 audio chunks,
    decodes them, and plays the decoded PCM audio.
    """
    p = pyaudio.PyAudio()

    # We might not know the exact format of the decoded audio in advance,
    # but we're assuming 44100 Hz, 16-bit, mono for this example.
    # Adjust these parameters based on the actual format of your MP3 audio.
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

    def decode_and_play_mp3_data(mp3_data):
        # Decode MP3 data to PCM
        decoded_audio = miniaudio.decode(mp3_data, nchannels=1, sample_rate=44100, output_format=miniaudio.SampleFormat.SIGNED16)
        pcm_data = decoded_audio.samples.tobytes()
        stream.write(pcm_data)

    try:
        while True:
            mp3_chunk_base64 = audio_queue.get()  # Block until an item is available
            # Decode Base64 to get the MP3 binary data
            mp3_data = base64.b64decode(mp3_chunk_base64)
            # Decode MP3 and play
            try:
                decode_and_play_mp3_data(mp3_data)
            except Exception as e:
                print(f"Error while playing audio: {e}")
    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        
def capture_image_to_base64_opencv():
    # Initialize the default camera
    cap = cv2.VideoCapture(0)  # 0 is the default camera

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    # Capture an image from the camera
    ret, frame = cap.read()
    if not ret:
        raise IOError("Cannot capture image from camera")
    
    # Optionally, convert the image from BGR to RGB format
    # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert the captured frame (image) to a JPEG in memory
    success, encoded_image = cv2.imencode('.jpg', frame)  # You can use frame_rgb if you converted it
    if not success:
        raise ValueError("Could not encode image to JPEG")
    
    # Convert the JPEG buffer to a Base64 string
    base64_image_str = base64.b64encode(encoded_image).decode('utf-8')
    
    # Release the camera
    cap.release()
    
    return base64_image_str

def capture_image_to_base64():
    # Initialize Picamera2
    picamera2 = Picamera2()

    # Configure the camera
    config = picamera2.create_preview_configuration()
    picamera2.configure(config)

    # Start the camera and let it adjust to conditions
    picamera2.start()

    # Capture an image to a NumPy array
    image = picamera2.capture_array()

    # Convert the image from BGR to RGB format
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # This is the key step

    # Convert the NumPy array to a JPEG in memory
    success, encoded_image = cv2.imencode('.jpg', image_rgb)  # Use the RGB image here
    if not success:
        raise ValueError("Could not encode image")

    # Convert the JPEG buffer to a Base64 string
    base64_image_str = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

    # Stop the camera
    picamera2.stop()

    return base64_image_str


def get_levels(data, long_term_noise_level, current_noise_level):
    pegel = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
    long_term_noise_level = long_term_noise_level * 0.995 + pegel * (1.0 - 0.995)
    current_noise_level = current_noise_level * 0.920 + pegel * (1.0 - 0.920)
    # print("long term: " + str(long_term_noise_level))
    # print("current: " + str(current_noise_level))
    return pegel, long_term_noise_level, current_noise_level


def combine_bytes_to_base64(audio, audio_data):
    # Create a bytes buffer to hold the WAV file data
    wav_buffer = io.BytesIO()

    # Initialize a wave file writer
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))  # Sample width in bytes
        wav_file.setframerate(44100)  # Sample rate
        wav_file.writeframes(audio_data)  # Write the raw audio data

    # Get the WAV file data from the buffer
    wav_data = wav_buffer.getvalue()
    
    with open("audio.wav", "wb") as f:
        f.write(wav_data)

    # Encode the WAV file data to Base64
    audio_data_base64 = base64.b64encode(wav_data).decode("utf-8")
    return audio_data_base64