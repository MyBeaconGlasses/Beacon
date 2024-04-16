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

from helper import play_audio_stream, capture_image_to_base64_opencv, capture_image_to_base64, combine_bytes_to_base64, get_levels

uri = "wss://api.mybeacon.tech/ws?client_id=1234"

async def main():
    audio_queue = queue.Queue()  # Using queue.Queue for thread-safe operations
    audio_thread = threading.Thread(target=play_audio_stream, args=(audio_queue,))
    audio_thread.start()
    while True:
        try:
            async with websockets.connect(uri, ping_timeout=None) as websocket:
                print("Connected to server")
                while True:
                    image_base64 = None
                    audio = pyaudio.PyAudio()
                    stream = audio.open(
                        rate=48000,
                        format=pyaudio.paInt32,
                        channels=1,
                        input=True,
			input_device_index=0,
                        frames_per_buffer=1024,
                    )
                    audio_buffer = collections.deque(maxlen=int((48000 // 1024) * 0.5))
                    frames, long_term_noise_level, current_noise_level, voice_activity_detected = (
                        [],
                        0.0,
                        0.0,
                        False,
                    )
                    print("\n\nStart speaking. ", end="", flush=True)
                    while True:
                        data = stream.read(1024)
                        pegel, long_term_noise_level, current_noise_level = get_levels(
                            data, long_term_noise_level, current_noise_level
                        )

                        # print(f"\rNoise level: {current_noise_level}")
                        # print(f"\rLong term noise level: {long_term_noise_level}")
                        

                        # if voice_activity_detected:
                        #     frames.append(data)
                        #     if current_noise_level < long_term_noise_level + 200:
                        #         print("long term: " + str(long_term_noise_level))
                        #         print("current: " + str(current_noise_level))
                        #         print("Stopped speaking.\n")
                        #         image_base64 = capture_image_to_base64()
                        #         break  # voice activity ends

                        # if (
                        #     not voice_activity_detected
                        #     and current_noise_level > long_term_noise_level + 500
                        # ):
                        #     print("Listening.\n")                            
                        #     voice_activity_detected = True
                        #     frames.extend(list(audio_buffer))
                            
                        audio_buffer.append(data)
                        if (
                            not voice_activity_detected
                            and current_noise_level > long_term_noise_level + 300
                        ):
                            print("Listening.\n")
                            # Save image to file
                            
                            voice_activity_detected = True
                            ambient_noise_level = long_term_noise_level
                            frames.extend(list(audio_buffer))
                            
                        if voice_activity_detected:
                            frames.append(data)
                            if current_noise_level < ambient_noise_level + 100:
                                print("Stopped speaking.\n")
                                image_base64 = capture_image_to_base64()
                                # capture_image_to_base64()
                                with open("image.jpg", "wb") as f:
                                    f.write(base64.b64decode(image_base64))
                                break  # voice activity ends  
                        
                    stream.stop_stream(), stream.close(), audio.terminate()
                    audio_data = b"".join(frames)
                    audio_data_base64 = combine_bytes_to_base64(audio, audio_data)
                    # print(audio_data_base64)
                                      
                    jsonBody = {
                        'audio': audio_data_base64,
                        'event': 'visual_chat',
                        'mode': 'text',
                        'image': image_base64,
                        'segment_data': ""
                    }
                    await websocket.send(json.dumps(jsonBody))
                    while True:
                        try:
                            response = await websocket.recv()
                            response_data = json.loads(response)
                            if response_data.get('transcript'):
                                print(response_data.get('transcript'), flush=True)
                            if response_data.get('text'):
                                print(response_data.get('text'), end="", flush=True)
                            if response_data.get('audio'):
                                audio_chunk = response_data.get('audio')
                                if audio_chunk != None or audio_chunk != "":
                                    # Convert from base64 to audio_data
                                    audio_queue.put(audio_chunk)
                            if response_data.get('end'):
                                break
                            if response_data.get('error'):
                                print(response_data.get('error'))
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
