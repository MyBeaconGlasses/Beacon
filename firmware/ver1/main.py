from dotenv import load_dotenv
import numpy as np
import shutil
import base64
import pyaudio
import collections
from websockets import connect
import asyncio
import json
import cv2
import queue
import threading

# mpv
import shutil
import subprocess

load_dotenv()

uri = "ws://localhost:8000"

def is_installed(lib_name):
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True 

def play_audio_stream(audio_queue):
    """
    Function to be run in a separate thread for playing audio chunks.
    It takes a queue from which it will continuously read and play audio chunks.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,  # 16-bit PCM format
                    channels=1,  # mono audio
                    rate=44100,  # Adjusted to 44.1kHz sample rate for pcm_44100
                    output=True)

    try:
        while True:
            chunk = audio_queue.get()  # Block until an item is available
            if chunk is None:
                break  # None is the signal to stop
            data = base64.b64decode(chunk)
            stream.write(data)
    finally:
        # Ensure resources are released even if there's an error
        stream.stop_stream()
        stream.close()
        p.terminate()

def capture_image_to_base64():
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # 0 is the default camera

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    # Capture a single frame
    ret, frame = cap.read()

    # Release the camera
    cap.release()

    # Ensure the frame was captured successfully
    if not ret:
        print("Error: Failed to capture image.")
        return None

    # Encode the frame as a JPEG image in memory
    _, buffer = cv2.imencode('.jpg', frame)
    # Convert the image to a base64 string
    encoded_string = base64.b64encode(buffer).decode()

    return encoded_string


def get_levels(data, long_term_noise_level, current_noise_level):
    pegel = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
    long_term_noise_level = long_term_noise_level * 0.995 + pegel * (1.0 - 0.995)
    current_noise_level = current_noise_level * 0.920 + pegel * (1.0 - 0.920)
    return pegel, long_term_noise_level, current_noise_level

async def stream_output(audio_stream):
    if not is_installed("mpv"):
        message = (
            "mpv not found, necessary to stream audio. "
            "On mac you can install it with 'brew install mpv'. "
            "On linux and windows you can install it from https://mpv.io/"
        )
        raise ValueError(message)

    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    audio = b""

    async for chunk in audio_stream:
        if chunk is not None:
            mpv_process.stdin.write(chunk)  # type: ignore
            mpv_process.stdin.flush()  # type: ignore
            audio += chunk

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

    return audio

async def main():
    audio_queue = queue.Queue()  # Using queue.Queue for thread-safe operations
    audio_thread = threading.Thread(target=play_audio_stream, args=(audio_queue,))
    audio_thread.start()
    with connect(uri) as websocket:
        while True:
            image_base64 = None
            audio = pyaudio.PyAudio()
            stream = audio.open(
                rate=16000,
                format=pyaudio.paInt16,
                channels=1,
                input=True,
                frames_per_buffer=512,
            )
            audio_buffer = collections.deque(maxlen=int((16000 // 512) * 0.5))
            frames, long_term_noise_level, current_noise_level, voice_activity_detected = (
                [],
                0.0,
                0.0,
                False,
            )
            print("\n\nStart speaking. ", end="", flush=True)

            while True:
                image_base64 = capture_image_to_base64()
                data = stream.read(512)
                pegel, long_term_noise_level, current_noise_level = get_levels(
                    data, long_term_noise_level, current_noise_level
                )
                audio_buffer.append(data)

                if (
                    not voice_activity_detected
                    and current_noise_level > long_term_noise_level + 300
                ):
                    voice_activity_detected = True
                    
                    print("Listening.\n")
                    ambient_noise_level = long_term_noise_level
                    frames.extend(list(audio_buffer))

                if voice_activity_detected:
                    frames.append(data)
                    if current_noise_level < ambient_noise_level + 100:
                        break  # voice activity ends

            stream.stop_stream(), stream.close(), audio.terminate()
            audio_data = b"".join(frames)
            audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")
            
            jsonBody = {
                'audio': audio_data_base64,
                'event': 'video_chat',
                'mode': 'text',
                'image': image_base64
            }
            await websocket.send(json.dumps(jsonBody))
            while True:
                try:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    if response_data.get('transcript'):
                        print(response_data.get('transcript'))
                    if response_data.get('text'):
                        print(response_data.get('text'), end="")
                    if response_data.get('audio'):
                        audio_chunk = response_data.get('audio')
                        audio_queue.put(audio_chunk)
                    if response_data.get('end'):
                        audio_buffer.put(None)
                        break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(1)

import asyncio

asyncio.run(main())