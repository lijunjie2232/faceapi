<template>
  <el-dialog v-model="dialogVisible" title="Face Recognition" width="700px" :before-close="handleClose"
    class="face-detection-popout">
    <div class="camera-controls">
      <el-button :type="flipEnabled ? 'success' : 'default'" @click="toggleFlip" :disabled="!isCameraOpen"
        class="flip-btn">
        <el-icon>
          <Switch />
        </el-icon>
        <span>{{ flipEnabled ? 'Flip Enabled' : 'Flip Disabled' }}</span>
      </el-button>
    </div>

    <div v-show="isCameraOpen" class="camera-container">
      <div class="video-wrapper">
        <video ref="videoRef" class="camera-video" :style="videoStyle" autoplay playsinline></video>
        <canvas ref="canvasRef" class="detection-canvas" :style="canvasStyle"></canvas>
      </div>

      <div v-if="loadingModels" class="loading-overlay">
        <el-progress type="circle" :percentage="modelLoadProgress" :width="150" :stroke-width="10" />
        <p>Loading face detection models...</p>
      </div>
    </div>

    <div v-if="!isCameraOpen && !loadingModels" class="placeholder-container">
      <el-empty description="Camera is not active" :image-size="150">
        <p>Camera starting automatically...</p>
      </el-empty>
    </div>

    <!-- Status message when verifying faces -->
    <div v-if="verifyingFace" class="verifying-message">
      <el-alert title="Verifying face, please wait..." type="info" :closable="false" show-icon>
      </el-alert>
    </div>

    <!-- Action buttons -->
    <div class="button-actions">
      <el-button @click="handleClose">Close</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElDialog, ElButton, ElIcon, ElProgress, ElEmpty, ElMessage, ElAlert } from 'element-plus'
import { FaceUtils } from '@/utils/face.js'

// Define props and emits
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'faceVerified'])

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
const flipEnabled = ref(!!localStorage.getItem('CameraFlipEnabled')) // Load flip state from localStorage
let faceUtils = null
let detectionInterval = null
const verifyingFace = ref(false) // Flag to prevent multiple verification requests

// Watch for dialog visibility to auto-start camera
watch(dialogVisible, async (newVal) => {
  if (newVal && !isCameraOpen.value && !loadingModels.value) {
    // Wait a bit to ensure UI is rendered before starting camera
    setTimeout(async () => {
      await startCamera()
    }, 300)
  } else if (!newVal) {
    // Stop camera when dialog closes
    stopCamera()
  }
})

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
      }, 500)
    }
  } catch (error) {
    // console.error("Error loading face-api.js:", error)
    ElMessage.error("Failed to load face detection models")
    loadingModels.value = false
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
    ElMessage.error("Could not access the camera. Please check permissions.")
  }
}

let stream = null
let ctx = null

// Start face detection loop for real-time processing
const startFaceDetectionLoop = async () => {
  if (!isCameraOpen.value || !videoRef.value || !canvasRef.value || !faceUtils || !dialogVisible.value) return

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

      // If we detect a face and are not currently verifying, send it to the server
      if (!verifyingFace.value) {
        // Capture the current frame and send it for verification
        const imageDataUrl = faceUtils.captureImageFromVideo(video, flipEnabled.value)

        // Convert to form data and send to server
        const formData = faceUtils.imageToFormData(imageDataUrl, 'face_image.jpg')

        // Start verification process
        verifyFace(formData)
      }
    } else {
      // No face detected, continue the loop
      if (isCameraOpen.value) {
        detectionInterval = setTimeout(startFaceDetectionLoop, 500) // ~2 FPS
      }
    }
  } catch (error) {
    // console.error("Error during face detection:", error)
    // Retry after a short delay
    if (isCameraOpen.value) {
      detectionInterval = setTimeout(startFaceDetectionLoop, 1000)
    }
  }
}

// Function to verify face with server
const verifyFace = async (formData) => {
  if (verifyingFace.value) return // Skip if already verifying

  verifyingFace.value = true

  try {
    // Send the captured image to the verification endpoint
    const response = await faceUtils.verifyFace(formData)

    // Check if response has the expected structure with 'code' field
    if (response.code === 200) {
      // Extract relevant data from the response
      const { recognized, user_id, confidence, data, message } = response
      const { token, token_type } = data
      
      // Store the token in localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('token_type', token_type)

      // Show success message with user info
      ElMessage.success(message || `Face recognized successfully as user ${user_id}`);

      // Emit event with verification result
      emit('faceVerified', { 
        success: true, 
        recognized: recognized,
        user_id: user_id,
        confidence: confidence,
        token: token,
        token_type: token_type,
      });

      // Close the dialog after successful verification
      handleClose()
    } else {
      // Verification failed - continue detection loop
      ElMessage.warning(response.message || 'Face recognition failed, please try again');
    }
  } catch (error) {
    // console.error('Error during face verification:', error);

    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message);
    } else {
      ElMessage.error('An error occurred during face verification');
    }
  } finally {
    // Reset the verifying flag to allow next verification
    verifyingFace.value = false

    // Continue detection loop if camera is still open
    if (isCameraOpen.value) {
      detectionInterval = setTimeout(startFaceDetectionLoop, 500)
    }
  }
}

// Handle dialog close
const handleClose = () => {
  stopCamera()
  verifyingFace.value = false // Reset verification flag
  dialogVisible.value = false
}

// Initialize when component mounts
onMounted(async () => {
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
}

.verifying-message {
  margin: 15px 0;
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
  justify-content: flex-end;
  margin-top: 20px;
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