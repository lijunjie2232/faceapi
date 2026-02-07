<template>
  <el-dialog v-model="dialogVisible" title="Face Detection" width="700px" :before-close="handleClose"
    class="face-detection-popout">
    <div class="camera-controls">
      <el-button type="primary" @click="toggleCamera" :loading="loadingModels" 
        :disabled="loadingModels || capturedImage || !modelsLoaded" class="camera-toggle-btn">
        <el-icon>
          <VideoCamera v-if="isCameraOpen" />
          <Camera v-else />
        </el-icon>
        <span>{{ isCameraOpen ? 'Stop Camera' : 'Start Camera' }}</span>
      </el-button>

      <el-button :type="flipEnabled ? 'success' : 'default'" @click="toggleFlip" 
        class="flip-btn">
        <el-icon>
          <Switch />
        </el-icon>
        <span>{{ flipEnabled ? 'Flip Enabled' : 'Flip Disabled' }}</span>
      </el-button>
      
      <!-- Auto Capture Switch -->
      <el-switch
        v-model="autoCaptureEnabled"
        class="auto-capture-switch"
        active-text="Auto Capture"
        inactive-text="Manual Capture"
        @change="handleAutoCaptureChange"
      />
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
        <el-button type="success" @click="confirmAndSendImage(props._handler)" class="confirm-btn">
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
import { FaceUtils } from '@/utils/face.js'
import { ElSwitch } from 'element-plus'

// Define props and emits
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  _handler: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'faceCaptured'])

// Refs
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const videoRef = ref(null)
const canvasRef = ref(null)
const isCameraOpen = ref(false)
const loadingModels = ref(true)
const modelsLoaded = ref(false) // Track whether models are loaded
const modelLoadProgress = ref(0)
const flipEnabled = ref(!!localStorage.getItem('CameraFlipEnabled')) // Load flip state from localStorage
const capturedImage = ref("") // Store the captured image
const autoCaptureEnabled = ref(!!localStorage.getItem('FaceAutoCaptureEnabled')) // Auto capture setting from localStorage
let stream = null
let faceUtils = null
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
  // Save flip state to localStorage
  if (flipEnabled.value) {
    localStorage.setItem('CameraFlipEnabled', 'true')
  } else {
    localStorage.removeItem('CameraFlipEnabled')
  }
}

// Handle auto capture setting change
const handleAutoCaptureChange = (value) => {
  if (value) {
    localStorage.setItem('FaceAutoCaptureEnabled', 'true')
  } else {
    localStorage.removeItem('FaceAutoCaptureEnabled')
  }
}

const loadModels = async () => {
  try {
    faceUtils = new FaceUtils()

    // Load face-api.js models
    const success = await faceUtils.loadFaceApi((progress) => {
      modelLoadProgress.value = progress
    })

    if (success) {
      setTimeout(() => {
        loadingModels.value = false
        modelsLoaded.value = true // Set modelsLoaded to true when loading is finished
      }, 500)
    }
  } catch (error) {
    // console.error("Error loading face-api.js:", error)
    loadingModels.value = false
    modelsLoaded.value = true // Still set to true so the button enables, even with error
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
    // console.error("Could not access the camera:", err)
    alert("Could not access the camera. Please check permissions.")
  }
}

let ctx = null

// Start face detection loop for real-time processing
const startFaceDetectionLoop = async () => {
  if (!isCameraOpen.value || !videoRef.value || !canvasRef.value || !faceUtils) return

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
    const detections = await faceUtils.detectFaces(video)

    // Check if we should auto-capture
    if (autoCaptureEnabled.value && detections && detections.length > 0) {
      // Delay capture slightly to ensure detection is stable
      setTimeout(() => {
        if (autoCaptureEnabled.value && detections && detections.length > 0) {
          captureImage()
        }
      }, 300)
    }

    // Draw detections on canvas
    if (ctx == null) {
      ctx = canvas.getContext('2d')
    }

    // Scale the detections to match the display size
    if (detections.length > 0) {
      // Calculate scale factors based on the actual video element's display size vs its intrinsic size
      const scaleX = canvas.width / video.videoWidth
      const scaleY = canvas.height / video.videoHeight

      // Use the utility function to draw detections
      faceUtils.drawDetections(canvas, detections, scaleX, scaleY, flipEnabled.value)
    }

    // Continue detecting faces if camera is still active
    if (isCameraOpen.value) {
      // Using setTimeout instead of requestAnimationFrame to control frequency
      // This prevents emitting events too frequently
      detectionInterval = setTimeout(startFaceDetectionLoop, 500) // ~2 FPS
    }
  } catch (error) {
    // console.error("Error during face detection:", error)
  }
}

// Function to capture image when button is clicked
const captureImage = () => {
  if (!videoRef.value || !faceUtils) return
  
  // Use the utility function to capture image from video
  const imageDataUrl = faceUtils.captureImageFromVideo(videoRef.value, flipEnabled.value)
  
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
const confirmAndSendImage = (_handler) => {
  if (capturedImage.value) {
    if (_handler && typeof _handler === 'function') {
      _handler(capturedImage.value)
    }
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

// Initialize when component mounts
onMounted(async () => {
  // Load auto capture setting from localStorage
  autoCaptureEnabled.value = !!localStorage.getItem('FaceAutoCaptureEnabled')
  await loadModels()
})

// Clean up camera stream when component unmounts
onUnmounted(() => {
  stopCamera()
})
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
  align-items: center;
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

.auto-capture-switch {
  margin-left: 10px;
}
</style>