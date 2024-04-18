'use client'
import React, {useState, useRef, useEffect} from 'react'
import Select from '@/components/Select'

const features = [
  'Same as the audio_demo, but with additional visual segmentation',
  'Select an image to segment',
  'Select a point on the image to segment',
  'Record audio and send it to the server',
]

const AudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false)
  const [overlayImage, setOverlayImage] = useState('')
  const [isLoading, setIsLoading] = useState(false) // New state for loading
  const [transcript, setTranscript] = useState('') // New state for transcript
  const [response, setResponse] = useState('') // New state for response
  const isPlaying = useRef(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const ws = useRef(null) // Initialize ws ref to null for WebSocket
  const audioContext = useRef()
  const audioQueueRef = useRef([])

  // Segmentation state and options
  const [selectedImage, setSelectedImage] = useState('/1.jpg') // Default image
  const images = Array.from({length: 10}, (_, i) => `/${i + 1}.jpg`) // Array of images
  const imageRef = useRef(null) // Ref for the main image
  const [segmentation, setSegmentation] = useState({
    display: 'Point Segmentation',
    value: 'Point Segmentation',
  })
  const imageSize = 'w-96 h-auto'
  const thumbnailSize = 'w-36 h-24'
  const [point, setPoint] = useState([0, 0])

  const convertDisplayedImageToBase64 = (callback) => {
    const imgElement = imageRef.current
    if (!imgElement) return

    // Create a canvas and draw the image onto it at displayed dimensions
    const canvas = document.createElement('canvas')
    canvas.width = imgElement.offsetWidth
    canvas.height = imgElement.offsetHeight

    const ctx = canvas.getContext('2d')
    ctx.drawImage(imgElement, 0, 0, canvas.width, canvas.height)

    // Convert canvas to Base64
    const base64Image = canvas.toDataURL('image/jpeg')
    callback(base64Image)
  }

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        // Set the uploaded image as the selected image
        setSelectedImage(e.target.result)
        setOverlayImage('') // Clear any existing overlay
      }
      reader.readAsDataURL(file) // Converts the image file to Base64
    }
  }

  useEffect(() => {
    audioContext.current = new (window.AudioContext ||
      window.webkitAudioContext)()
    ws.current = new WebSocket('wss://api.mybeacon.tech/ws?client_id=123')

    ws.current.onopen = () => console.log('WebSocket Connected')
    ws.current.onerror = (error) => console.log('WebSocket Error:', error)
    ws.current.onclose = () => console.log('WebSocket Disconnected')

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.end === true) {
        setIsLoading(false) // Disable loading state
      }
      if (data.transcript) {
        setTranscript(data.transcript)
      }
      if (data.text) {
        setResponse((prev) => prev + data.text)
      }
      if (data.audio) {
        const audioArrayBuffer = base64ToArrayBuffer(data.audio)
        enqueueAndPlayAudio(audioArrayBuffer)
      }
      if (data.mask) {
        const imgWithHeader = 'data:image/jpeg;base64,' + data.mask
        setOverlayImage(imgWithHeader)
      }
    }

    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64)
    const len = binaryString.length
    const bytes = new Uint8Array(len)
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    return bytes.buffer
  }

  const playNextAudio = () => {
    if (audioQueueRef.current.length > 0 && !isPlaying.current) {
      isPlaying.current = true
      const audioBlob = audioQueueRef.current.shift() // Get the next audio blob from the queue
      const reader = new FileReader()
      reader.onload = function () {
        const arrayBuffer = this.result
        audioContext.current.decodeAudioData(arrayBuffer, (buffer) => {
          const source = audioContext.current.createBufferSource()
          source.buffer = buffer
          source.connect(audioContext.current.destination)
          source.onended = () => {
            isPlaying.current = false // Reset the flag when audio ends
            playNextAudio() // Try to play the next audio
          }
          source.start(0)
        })
      }
      reader.readAsArrayBuffer(audioBlob)
    }
  }

  const enqueueAndPlayAudio = (audioArrayBuffer) => {
    const audioBlob = new Blob([audioArrayBuffer], {type: 'audio/mp3'})
    audioQueueRef.current.push(audioBlob) // Add new audio to the queue
    playNextAudio() // Attempt to play next audio
  }

  const handleMicClick = async () => {
    if (!isRecording && !isLoading) {
      if (
        segmentation.value === 'Point Segmentation' &&
        (point[0] === 0 || point[1] === 0)
      ) {
        alert('Please select a point on the image to segment.')
        return
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert(
          'Media Devices API or getUserMedia not supported in your browser.',
        )
        return
      }

      if (audioContext.current.state === 'suspended') {
        audioContext.current.resume()
      }

      try {
        setTranscript('') // Clear transcript when recording starts
        setResponse('') // Clear response when recording starts
        const stream = await navigator.mediaDevices.getUserMedia({audio: true})
        mediaRecorderRef.current = new MediaRecorder(stream)
        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data)
        }
        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: 'audio/mp3',
          })
          audioChunksRef.current = []
          const reader = new FileReader()
          reader.readAsDataURL(audioBlob)
          reader.onloadend = () => {
            convertDisplayedImageToBase64((base64Image) => {
              const base64AudioMessage = reader.result.split(',')[1]
              if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(
                  JSON.stringify({
                    audio: base64AudioMessage,
                    event: 'visual_chat',
                    mode:
                      segmentation === 'Point Segmentation' ? 'point' : 'text',
                    segment_data: point,
                    image: base64Image,
                  }),
                )
                setIsLoading(true) // Enable loading state
              }
            })
          }
        }
        mediaRecorderRef.current.start()
      } catch (err) {
        console.error('The following getUserMedia error occurred:', err)
      }
    } else {
      mediaRecorderRef.current.stop()
      setIsLoading(true) // Start loading when recording starts
    }
    setIsRecording((prev) => !prev)
  }

  const handleImageClick = (e) => {
    const x = e.nativeEvent.offsetX
    const y = e.nativeEvent.offsetY
    // Use ws.current to send a message to the server
    if (segmentation.value === 'Point Segmentation') {
      setPoint([x, y])
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-[#14102a] to-[#0e0e0e]">
      <div className="mb-8" flex flex-row items-center justify-center>
        <Select
          value={segmentation}
          setValue={(e) => {
            setSegmentation(e)
            setPoint([0, 0])
          }}
          options={['Point Segmentation', 'Text Segmentation']}
        />
        <div className="mb-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="file:mr-4 file:py-2 file:px-4
               file:rounded-full file:border-0
               file:text-sm file:font-semibold
               file:bg-violet-50 file:text-violet-700
               hover:file:bg-violet-100"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Features Column */}
        <div className="bg-gray-800 text-white p-4 rounded-lg">
          <div className="w-full max-w-4xl">
            {/* Focused Image */}
            <div className={`${imageSize} mx-auto mb-8 border-4 rounded-lg `}>
              <div className="relative">
                <img
                  ref={imageRef}
                  src={selectedImage}
                  onClick={handleImageClick}
                  alt="Selected"
                  className="object-cover rounded-md shadow-md w-96 h-auto"
                />
                {overlayImage && (
                  <img
                    src={overlayImage}
                    alt="Overlay"
                    className="absolute top-0 left-0 object-cover rounded-md shadow-lg w-full h-full opacity-50 pointer-events-none"
                  />
                )}
                {point[0] !== 0 && point[1] !== 0 && (
                  <div
                    style={{
                      position: 'absolute',
                      left: `${point[0]}px`,
                      top: `${point[1]}px`,
                      width: '10px',
                      height: '10px',
                      backgroundColor: 'red',
                      borderRadius: '50%',
                      transform: 'translate(-50%, -50%)', // Center the marker
                    }}
                  ></div>
                )}
              </div>
            </div>

            {/* Thumbnails Menu */}
            <div className="flex overflow-x-scroll overflow-y-hidden mx-4">
              {images.map((image, index) => (
                <div key={index} className={`flex-none mr-4 ${thumbnailSize}`}>
                  <button
                    onClick={() => {
                      setSelectedImage(image)
                      setPoint([0, 0])
                      setOverlayImage('')
                    }}
                  >
                    <img
                      src={image}
                      alt={`Thumbnail ${index + 1}`}
                      className={`object-cover rounded-md hover:opacity-75 ${thumbnailSize} ${
                        selectedImage === image
                          ? 'border-2 border-[#ac3fff]'
                          : ''
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Transcript and Response Column */}
        <div className="bg-gray-800 text-white p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-4">Features</h2>
          <ul>
            {features.map((feature, index) => (
              <li key={index} className="mb-2">
                {feature}
              </li>
            ))}
          </ul>
          <h2 className="text-lg font-semibold mb-4">Transcript & Response</h2>
          {transcript && <p className="mb-2">Transcript: {transcript}</p>}
          {response && <p>Response: {response}</p>}
        </div>
      </div>

      {/* Record Button */}
      <div className="mt-4 flex justify-center">
        <button
          onClick={handleMicClick}
          disabled={isLoading}
          className={`mt-4 p-4 rounded-full ${
            isRecording ? 'bg-red-500' : 'bg-green-500'
          } ${isLoading ? 'bg-gray-500' : ''} text-white`}
        >
          {isLoading
            ? 'Processing...'
            : isRecording
            ? 'Stop Recording'
            : 'Start Recording'}
        </button>
      </div>
    </div>
  )
}

export default AudioRecorder
