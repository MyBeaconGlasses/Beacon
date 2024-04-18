import numpy as np
import shutil
import base64
import pyaudio
import collections
import websockets
import asyncio
import json
import cv2
import queue
import threading
import io
import wave
import traceback

# mpv
import shutil
import subprocess

from helper import (
    play_audio_stream,
    capture_image_to_base64_opencv,
    capture_image_to_base64,
    combine_bytes_to_base64,
    get_levels,
)

uri = "wss://api.mybeacon.tech/ws?client_id=1234"
buffer_size = 2048


async def main():
    audio_queue = queue.Queue()  # Using queue.Queue for thread-safe operations
    audio_thread = threading.Thread(target=play_audio_stream, args=(audio_queue,))
    audio_thread.start()

    while True:
        try:
            async with websockets.connect(uri, ping_timeout=None) as websocket:
                print("Connected to server")
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    rate=48000,
                    format=pyaudio.paInt32,
                    channels=1,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=buffer_size,
                )

                recording = False
                frames = []

                while True:
                    # Simulate button press (replace this with actual button check)
                    button_pressed = True  # Change this to actual button state

                    if button_pressed and not recording:
                        print("Recording started.")
                        recording = True

                    if recording:
                        data = stream.read(buffer_size)
                        frames.append(data)

                        # Simulate button release (replace this with actual button check)
                        button_released = False  # Change this to actual button state
                        if button_released:
                            print("Recording stopped.")
                            recording = False
                            break

                if frames:
                    # Stop and close the stream
                    stream.stop_stream()
                    stream.close()
                    audio.terminate()

                    # Combine frames into a single byte stream and convert to base64
                    audio_data = b"".join(frames)
                    audio_data_base64 = combine_bytes_to_base64(audio_data)

                    json_body = {
                        "audio": audio_data_base64,
                        "event": "audio_chat",
                    }
                    await websocket.send(json.dumps(json_body))
                    while True:
                        try:
                            response = await websocket.recv()
                            response_data = json.loads(response)
                            if response_data.get("transcript"):
                                print(response_data.get("transcript"), flush=True)
                            if response_data.get("audio"):
                                audio_chunk = response_data.get("audio")
                                if audio_chunk:
                                    audio_queue.put(audio_chunk)
                            if response_data.get("end"):
                                break
                            if response_data.get("error"):
                                print(response_data.get("error"))
                                break
                        except Exception as e:
                            print(e)
                            break
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}")
            print(traceback.format_exc())
            break
    print("Exiting...")
    return ""


import asyncio

asyncio.run(main())
