import pyaudio

FORMAT = pyaudio.paInt32  # This is the closest format available in PyAudio for S32_LE
CHANNELS = 2
RATE = 48000
CHUNK = 1024

audio = pyaudio.PyAudio()

# List all the available audio devices
info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

