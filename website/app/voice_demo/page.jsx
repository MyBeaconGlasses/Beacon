'use client'
import React, {useState, useRef, useEffect} from 'react'

const features = [
  'Google Finance: Get real-time stock prices and financial information for any company.',
  'Google Jobs: Find job postings and opportunities based on titles, companies, or locations.',
  'Google Scholar: Access academic papers, articles, and citations for scholarly research.',
  'Google Search: Perform searches to find information, news, images, and more on the web.',
  'Google Trends: Analyze the popularity of search queries in Google across various regions and languages.',
  'Weather Conditions: Get current weather conditions including temperature, humidity, and wind speed for any location.',
  'Yelp Places: Discover top-rated places like restaurants and services within a specified radius of a location.',
  'Yelp Business Details: Retrieve detailed information about businesses including ratings, reviews, and contact info.',
  'Yelp Reviews: Read customer reviews for businesses to make informed decisions.',
]

const AudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(false) // New state for loading
  const [transcript, setTranscript] = useState('') // New state for transcript
  const [response, setResponse] = useState('') // New state for response
  const isPlaying = useRef(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const ws = useRef(null) // Initialize ws ref to null for WebSocket
  const audioContext = useRef(null)

  const audioQueueRef = useRef([])

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
            const base64AudioMessage = reader.result.split(',')[1]
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
              ws.current.send(
                JSON.stringify({
                  audio: base64AudioMessage,
                  event: 'audio_chat',
                }),
              )
              setIsLoading(true) // Enable loading state
            }
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

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Features Column */}
        <div className="bg-gray-800 text-white p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-4">Features</h2>
          <ul>
            {features.map((feature, index) => (
              <li key={index} className="mb-2">
                {feature}
              </li>
            ))}
          </ul>
        </div>

        {/* Transcript and Response Column */}
        <div className="bg-gray-800 text-white p-4 rounded-lg">
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
