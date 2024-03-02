'use client'
import {useState, useRef, useEffect} from 'react'
import Select from '@/components/Select'

const Gallery = () => {
  const [selectedImage, setSelectedImage] = useState('/1.jpg') // Default image
  const [overlayImage, setOverlayImage] = useState('')
  const images = Array.from({length: 10}, (_, i) => `/${i + 1}.jpg`) // Array of images
  const imageRef = useRef(null) // Ref for the main image
  const [segmentationText, setSegmentationText] = useState('')
  const ws = useRef(null) // Initialize ws ref to null
  const [segmentation, setSegmentation] = useState({
    display: 'Point Segmentation',
    value: 'Point Segmentation',
  })

  const imageSize = 'w-96 h-auto'
  const thumbnailSize = 'w-36 h-24'

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

  const handleImageClick = (e) => {
    const x = e.nativeEvent.offsetX
    const y = e.nativeEvent.offsetY
    // Use ws.current to send a message to the server
    if (
      ws.current &&
      ws.current.readyState === WebSocket.OPEN &&
      segmentation.value === 'Point Segmentation'
    ) {
      // Ensure the WebSocket connection is open
      // Convert the displayed image to Base64, then send it along with the coordinates
      convertDisplayedImageToBase64((base64Image) => {
        // Prepare the message object
        const message = {
          event: 'segment_point',
          point: [x, y],
          image: base64Image,
          text: segmentationText, // Include only if relevant
        }
        // Send the message to the WebSocket server
        ws.current.send(JSON.stringify(message))
      })
    }
  }

  const handleTextEntry = (e) => {
    if (e.key === 'Enter') {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        convertDisplayedImageToBase64((base64Image) => {
          const message = {
            event: 'segment_text',
            image: base64Image,
            text: segmentationText,
          }
          ws.current.send(JSON.stringify(message))
        })
      }
    }
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
    // Establish the WebSocket connection in the useEffect hook
    ws.current = new WebSocket('wss://api.mybeacon.tech/ws?client_id=123')

    ws.current.onopen = () => console.log('WebSocket Connected')
    ws.current.onerror = (error) => console.log('WebSocket Error:', error)
    ws.current.onclose = () => console.log('WebSocket Disconnected')

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.mask) {
        const imgWithHeader = 'data:image/jpeg;base64,' + data.mask
        setOverlayImage(imgWithHeader)
      }
    }

    // Cleanup function to close WebSocket connection when the component unmounts
    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-[#14102a] to-[#0e0e0e]">
      <div className="mb-8" flex flex-row items-center justify-center>
        <Select
          value={segmentation}
          setValue={setSegmentation}
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
            {/* Overlay Image - Rendered only if overlayImage is not empty */}
            {overlayImage && (
              <img
                src={overlayImage}
                alt="Overlay"
                className="absolute top-0 left-0 object-cover rounded-md shadow-lg w-full h-full opacity-50 pointer-events-none"
              />
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
                  setOverlayImage('')
                }}
              >
                <img
                  src={image}
                  alt={`Thumbnail ${index + 1}`}
                  className={`object-cover rounded-md hover:opacity-75 ${thumbnailSize} ${
                    selectedImage === image ? 'border-2 border-[#ac3fff]' : ''
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {segmentation.value == 'Text Segmentation' && (
        <div className="mt-4">
          <input
            type="text"
            value={segmentationText}
            onChange={(e) => setSegmentationText(e.target.value)}
            placeholder="Enter text for segmentation"
            className="px-4 py-2 border rounded-md shadow-sm w-full focus:ring-[#ac3fff] focus:border-[#ac3fff] focus:outline-none"
            onKeyDown={handleTextEntry}
          />
        </div>
      )}
    </div>
  )
}

export default Gallery
