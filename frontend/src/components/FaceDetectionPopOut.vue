<template>
  <el-dialog v-model="dialogVisible" title="Face Detection" width="700px" :before-close="handleClose"
    class="face-detection-popout">
    <div class="camera-controls">
      <el-button type="primary" @click="toggleCamera" :loading="loadingModels" :disabled="loadingModels"
        class="camera-toggle-btn">
        <el-icon>
          <VideoCamera v-if="isCameraOpen" />
          <Camera v-else />
        </el-icon>
        <span>{{ isCameraOpen ? 'Stop Camera' : 'Start Camera' }}</span>
      </el-button>

      <el-button :type="flipEnabled ? 'success' : 'default'" @click="toggleFlip" class="flip-btn">
        <el-icon>
          <Switch />
        </el-icon>
        <span>{{ flipEnabled ? 'Flip Enabled' : 'Flip Disabled' }}</span>
      </el-button>
    </div>

    <!-- Show captured image preview when available -->
    <div v-if="capturedImage" class="image-preview-container">
      <h3>Confirm Image</h3>
      <img :src="capturedImage" alt="Captured face image" class="captured-image-preview" />
      <p>Please confirm to upload this image</p>
    </div>

    <div v-show="isCameraOpen && !capturedImage" class="camera-container">
      <div class="video-wrapper">
        <video ref="videoRef" class="camera-video" :style="videoStyle" autoplay playsinline></video>
        <canvas ref="canvasRef" class="detection-canvas" :style="canvasStyle"></canvas>
      </div>

      <div v-if="loadingModels" class="loading-overlay">
        <el-progress type="circle" :percentage="modelLoadProgress" :width="150" :stroke-width="10" />
        <p>Loading face detection models...</p>
      </div>
    </div>

    <div v-if="!isCameraOpen && !loadingModels && !capturedImage" class="placeholder-container">
      <el-empty description="Camera is not active" :image-size="150">
        <p>Click "Start Camera" to begin face detection</p>
      </el-empty>
    </div>

    <!-- Different button actions depending on state -->
    <div class="button-actions">
      <el-button @click="handleClose">{{ capturedImage ? 'Cancel' : 'Close' }}</el-button>
      
      <div class="confirmation-buttons" v-if="capturedImage">
        <el-button @click="retakeImage">Retake</el-button>
        <el-button type="success" @click="confirmAndSendImage" class="confirm-btn">
          <el-icon>
            <Check />
          </el-icon>
          <span>Confirm & Upload</span>
        </el-button>
      </div>
      
      <el-button v-else type="success" @click="captureImage" :disabled="!isCameraOpen || loadingModels" class="capture-btn">
        <el-icon>
          <Camera />
        </el-icon>
        <span>Capture Image</span>
      </el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElDialog, ElButton, ElIcon, ElProgress, ElEmpty, ElMessage } from 'element-plus'
import { VideoCamera, Camera, Switch, Check } from '@element-plus/icons-vue'
import axios from 'axios'

// Define props and emits
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  token: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'faceCaptured'])

// Get environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const MODELS_PATH = import.meta.env.VITE_FACE_API_MODELS_PATH || '/models'

// Refs
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const videoRef = ref(null)
const canvasRef = ref(null)
const isCameraOpen = ref(false)
const loadingModels = ref(true)
const modelLoadProgress = ref(0)
const flipEnabled = ref(false)
const capturedImage = ref(null) // Store the captured image
let stream = null
let faceapi = null
let detectionInterval = null

// Computed styles for video and canvas
const videoStyle = computed(() => ({
  transform: flipEnabled.value ? 'scaleX(-1)' : 'none'
}))

const canvasStyle = computed(() => ({
  transform: flipEnabled.value ? 'scaleX(-1)' : 'none'
}))

// Toggle flip function
const toggleFlip = () => {
  flipEnabled.value = !flipEnabled.value
}

// Initialize face-api.js
onMounted(() => {
  loadModels()
})

const loadModels = async () => {
  try {
    // Dynamically import face-api.js
    const faceApiModule = await import('face-api.js')
    faceapi = faceApiModule

    // Load face-api.js models
    await loadFaceDetectionModels()
  } catch (error) {
    console.error("Error loading face-api.js:", error)
    loadingModels.value = false
  }
}

// Load face-api.js models
const loadFaceDetectionModels = async () => {
  try {
    // Update progress as each model loads
    modelLoadProgress.value = 25
    await faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_PATH)

    modelLoadProgress.value = 100
    setTimeout(() => {
      loadingModels.value = false
    }, 500)
  } catch (err) {
    console.error("Error loading models from local path:", err)

    // Try loading from CDN as fallback
    try {
      await faceapi.nets.tinyFaceDetector.loadFromUri('https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights')

      modelLoadProgress.value = 100
      setTimeout(() => {
        loadingModels.value = false
      }, 500)
    } catch (fallbackErr) {
      console.error("Error loading models from CDN:", fallbackErr)
      loadingModels.value = false
    }
  }
}

// Toggle camera on/off
const toggleCamera = async () => {
  if (isCameraOpen.value) {
    stopCamera()
  } else {
    await startCamera()
  }
}

// Start camera
const startCamera = async () => {
  if (loadingModels.value) return

  try {
    // Request access to the camera
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      isCameraOpen.value = true

      // Start face detection loop after a delay to allow video to load
      setTimeout(startFaceDetectionLoop, 500)
    }
  } catch (err) {
    console.error("Could not access the camera:", err)
    alert("Could not access the camera. Please check permissions.")
  }
}

let ctx = null

// Start face detection loop for real-time processing
const startFaceDetectionLoop = async () => {
  if (!isCameraOpen.value || !videoRef.value || !canvasRef.value || !faceapi) return

  try {
    // Get the display dimensions of the video element
    const video = videoRef.value
    const canvas = canvasRef.value

    // Wait for the video to be loaded and dimensions to be available
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      // Retry after a short delay if video dimensions aren't ready yet
      setTimeout(startFaceDetectionLoop, 100)
      return
    }

    // Get the computed styles of the video element to determine actual display size
    const computedStyle = window.getComputedStyle(video)
    const videoDisplayWidth = parseFloat(computedStyle.getPropertyValue('width'))
    const videoDisplayHeight = parseFloat(computedStyle.getPropertyValue('height'))

    // Set canvas dimensions to match the actual video display size
    canvas.width = videoDisplayWidth
    canvas.height = videoDisplayHeight

    // Set the canvas position to match the video element's offset
    canvas.style.position = 'absolute'
    canvas.style.top = video.offsetTop + 'px'
    canvas.style.left = video.offsetLeft + 'px'
    canvas.style.width = videoDisplayWidth + 'px'
    canvas.style.height = videoDisplayHeight + 'px'

    // Apply flip transformation to canvas if enabled
    canvas.style.transform = flipEnabled.value ? 'scaleX(-1)' : 'none'

    // Perform face detection on the actual video
    const detections = await faceapi.detectAllFaces(
      video,
      new faceapi.TinyFaceDetectorOptions()
    )

    // Draw detections on canvas
    if (ctx == null) {
      ctx = canvas.getContext('2d')
    }

    // Clear the canvas before drawing
    // ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Scale the detections to match the display size
    if (detections.length > 0) {
      // Calculate scale factors based on the actual video element's display size vs its intrinsic size
      const scaleX = canvas.width / video.videoWidth
      const scaleY = canvas.height / video.videoHeight

      // Draw detections by manually drawing ellipses with gradient
      detections.forEach(detection => {
        const box = detection.box

        // Scale the box coordinates according to the display scale
        let x = box.x * scaleX
        let y = box.y * scaleY
        const width = box.width * scaleX
        const height = box.height * scaleY

        // Adjust x coordinate if flipped
        // if (flipEnabled.value) {
        //   x = canvas.width - x - width
        // }

        // Draw rectangle with gradient
        drawEllipseWithGradient(ctx, x + width/2, y + height/2, width/2, height/2)
      })
    }

    // Continue detecting faces if camera is still active
    if (isCameraOpen.value) {
      // Using setTimeout instead of requestAnimationFrame to control frequency
      // This prevents emitting events too frequently
      detectionInterval = setTimeout(startFaceDetectionLoop, 500) // ~2 FPS
    }
  } catch (error) {
    console.error("Error during face detection:", error)
    // Retry after a short delay
    // if (isCameraOpen.value) {
    //   detectionInterval = setTimeout(startFaceDetectionLoop, 1000)
    // }
  }
}

// Function to handle face captured from pop-out window
const handleFaceCaptured = async (imageData, token) => {
  try {
    // Upload the captured image to update the user's head pic
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/user/me`,
      {
        head_pic: imageData // Assuming the backend accepts base64 image data
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    // Check if response has the expected structure with 'code' field
    if (response.data.code === 200 || response.data.success) {
      ElMessage.success(response.data.message || 'Face image updated successfully');
      emit('faceCaptured', imageData); // Emit event with captured image data
    } else {
      ElMessage.error(response.data.message || 'Failed to update face image');
    }
  } catch (error) {
    console.error('Error updating face image:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error(error.message || 'An error occurred while updating face image');
    }
  }
};

// Function to capture image when button is clicked
const captureImage = () => {
  if (!videoRef.value) return
  
  // Create a temporary canvas to capture the video frame
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = videoRef.value.videoWidth
  tempCanvas.height = videoRef.value.videoHeight
  const ctx = tempCanvas.getContext('2d')

  // Apply flip if enabled before drawing the video frame
  if (flipEnabled.value) {
    ctx.translate(tempCanvas.width, 0)
    ctx.scale(-1, 1)
  }

  // Draw current video frame to canvas
  ctx.drawImage(videoRef.value, 0, 0, tempCanvas.width, tempCanvas.height)

  // Convert to image data URL
  const imageDataUrl = tempCanvas.toDataURL('image/jpeg')
  
  // Store the captured image for confirmation
  capturedImage.value = imageDataUrl
  
  // Stop the camera but keep the dialog open
  stopCamera()
}

// Function to retake image - reset captured image and restart camera
const retakeImage = () => {
  capturedImage.value = null
  startCamera()  // Restart the camera
}

// Function to confirm and send the image
const confirmAndSendImage = () => {
  if (capturedImage.value && props.token) {
    handleFaceCaptured(capturedImage.value, props.token)
    handleClose() // Close the dialog after sending
  }
}

// Stop camera
const stopCamera = () => {
  if (detectionInterval) {
    clearTimeout(detectionInterval) // Use clearTimeout instead of cancelAnimationFrame
    detectionInterval = null
  }

  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  isCameraOpen.value = false
}

// Handle dialog close
const handleClose = () => {
  stopCamera()
  capturedImage.value = null // Reset captured image
  dialogVisible.value = false
}

// Clean up camera stream when component unmounts
onUnmounted(() => {
  stopCamera()
})

// Function to draw ellipse with green border
function drawEllipseWithGradient(ctx, centerX, centerY, radiusX, radiusY) {
  // Draw a green ellipse border for face detection
  ctx.save();

  // Draw the green border for the ellipse
  ctx.strokeStyle = '#00ff00'; // Bright green color
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, Math.PI * 2);
  ctx.stroke();

  // Add L-shaped corners for better visibility
  ctx.beginPath();

  // Top-left corner
  ctx.moveTo(centerX - radiusX, centerY - radiusY + 10);
  ctx.lineTo(centerX - radiusX, centerY - radiusY);
  ctx.lineTo(centerX - radiusX + 10, centerY - radiusY);

  // Top-right corner
  ctx.moveTo(centerX + radiusX - 10, centerY - radiusY);
  ctx.lineTo(centerX + radiusX, centerY - radiusY);
  ctx.lineTo(centerX + radiusX, centerY - radiusY + 10);

  // Bottom-left corner
  ctx.moveTo(centerX - radiusX, centerY + radiusY - 10);
  ctx.lineTo(centerX - radiusX, centerY + radiusY);
  ctx.lineTo(centerX - radiusX + 10, centerY + radiusY);

  // Bottom-right corner
  ctx.moveTo(centerX + radiusX - 10, centerY + radiusY);
  ctx.lineTo(centerX + radiusX, centerY + radiusY);
  ctx.lineTo(centerX + radiusX, centerY + radiusY - 10);

  ctx.stroke();

  // Draw a small circle at the center of the ellipse
  ctx.beginPath();
  ctx.fillStyle = '#00ff00'; // Same bright green color
  ctx.arc(centerX, centerY, 4, 0, Math.PI * 2); // Small circle with radius 4
  ctx.fill();

  ctx.restore();
}
</script>

<style scoped>
.face-detection-popout {
  padding: 20px;
}

.camera-controls {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.image-preview-container {
  text-align: center;
  margin: 20px 0;
}

.captured-image-preview {
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin: 10px auto;
  display: block;
}

.camera-container {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  min-height: 300px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.camera-video {
  width: 100%;
  display: block;
  border-radius: 12px;
  object-fit: cover;
  /* Ensures the video maintains aspect ratio */
  transition: transform 0.2s ease;
  /* Smooth transition for flip effect */
}

.detection-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  transition: transform 0.2s ease;
  /* Smooth transition for flip effect */
}

.button-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.confirmation-buttons {
  display: flex;
  gap: 10px;
}

.capture-btn {
  background-color: #67c23a;
  /* Green color */
  border-color: #67c23a;
  /* Green border */
  color: white;
  /* White text */
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
}

.capture-btn:hover,
.capture-btn:focus {
  background-color: #5daf34;
  /* Darker green on hover */
  border-color: #5daf34;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.confirm-btn {
  background-color: #67c23a;
  /* Green color */
  border-color: #67c23a;
  /* Green border */
  color: white;
  /* White text */
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
}

.confirm-btn:hover,
.confirm-btn:focus {
  background-color: #5daf34;
  /* Darker green on hover */
  border-color: #5daf34;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  z-index: 10;
}

.loading-overlay p {
  margin-top: 15px;
  font-size: 16px;
}

.placeholder-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  margin-top: 20px;
}

.flip-btn {
  margin-left: 10px;
}
</style>