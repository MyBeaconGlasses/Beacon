import shutil
import base64
import os
import websockets
from websockets.sync.client import connect
import json
import subprocess

elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice = {
    "voice_id": "EXAVITQu4vr4xnSDxMaL",
    "name": "Bella",
    "settings": {
        "stability": 0.72,
        "similarity_boost": 0.2,
        "style": 0.0,
        "use_speaker_boost": False,
        "speaking_rate": 2,
    },
}
model = {
    "model_id": "eleven_multilingual_v2",
}


def is_installed(lib_name):
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True


async def text_chunker(chunks):
    """Used during input streaming to chunk text blocks and set last char to space"""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer if buffer.endswith(" ") else buffer + " "
            buffer = text
        elif text.startswith(splitters):
            output = buffer + text[0]
            yield output if output.endswith(" ") else output + " "
            buffer = text[1:]
        else:
            buffer += text
    if buffer != "":
        yield buffer + " "


async def generate_stream_input(first_text_chunk, text_generator):
    """
    Generates audio from a stream of text input using the Eleven Labs API.
    """
    BOS = json.dumps(
        dict(
            text=" ",
            try_trigger_generation=True,
            voice_settings=voice["settings"],
            generation_config=dict(chunk_length_schedule=[50]),
        )
    )
    EOS = json.dumps({"text": ""})

    with connect(
        f"""wss://api.elevenlabs.io/v1/text-to-speech/{voice["voice_id"]}/stream-input?model_id={model["model_id"]}""",
        additional_headers={
            "xi-api-key": elevenlabs_api_key,
        },
    ) as websocket:
        websocket.send(BOS)

        # Send the first text chunk immediately
        first_data = dict(text=first_text_chunk, try_trigger_generation=True)
        websocket.send(json.dumps(first_data))

        # Stream text chunks and receive audio
        async for text_chunk in text_chunker(text_generator):
            data = dict(text=text_chunk, try_trigger_generation=True)
            websocket.send(json.dumps(data))
            try:
                data = json.loads(websocket.recv(1e-4))
                if data["audio"]:
                    yield base64.b64decode(data["audio"])  # type: ignore
            except TimeoutError:
                pass

        websocket.send(EOS)

        while True:
            try:
                data = json.loads(websocket.recv())
                if data["audio"]:
                    yield base64.b64decode(data["audio"])  # type: ignore
            except websockets.exceptions.ConnectionClosed:
                break


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
