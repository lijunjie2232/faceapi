<template>
  <div class="face-register component-container">
    <el-row :gutter="30">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="upload-section">
          <h3 class="section-header">Register New Face</h3>
          <p>Select a user and upload an image containing their face</p>
          
          <el-select 
            v-model="selectedUserId" 
            placeholder="Select a user"
            style="width: 100%; margin-bottom: 20px;"
            filterable
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="`${user.username} (${user.full_name})`"
              :value="user.id"
            />
          </el-select>
          
          <el-upload
            class="image-uploader"
            drag
            :show-file-list="false"
            accept="image/*"
            :before-upload="handleImageUpload"
          >
            <el-icon class="uploader-icon"><Upload /></el-icon>
            <div class="uploader-text">Click or drag an image to this area to upload</div>
            <p class="uploader-hint">Supports JPG, PNG, WEBP formats</p>
          </el-upload>
          
          <el-button 
            type="primary" 
            @click="registerFace"
            :disabled="!imagePreview || !selectedUserId || loading"
            class="register-btn"
          >
            <el-icon><UserFilled /></el-icon>
            <span>Register Face{{ loading ? '...' : '' }}</span>
          </el-button>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="result-section">
          <h3 class="section-header">Registration Status</h3>
          <div v-if="statusMessage" class="status-message" :class="{ 'success': statusSuccess, 'error': !statusSuccess }">
            <el-icon :class="statusSuccess ? 'success-icon' : 'error-icon'">
              <CheckCircle v-if="statusSuccess" />
              <CircleClose v-else />
            </el-icon>
            <p>{{ statusMessage }}</p>
          </div>
          
          <div v-if="imagePreview" class="preview-container">
            <h4>Image Preview</h4>
            <div class="preview-wrapper">
              <img :src="imagePreview" alt="Preview" class="preview-image rounded-img" />
            </div>
          </div>
          
          <div v-if="!imagePreview" class="empty-preview">
            <el-empty description="No image selected" :image-size="100">
              <p>Upload an image to preview</p>
            </el-empty>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
// import { Upload, UserFilled, CheckCircle, CircleClose } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const users = ref([])
const selectedUserId = ref(null)
const imagePreview = ref(null)
const imageFile = ref(null)
const loading = ref(false)
const statusMessage = ref('')
const statusSuccess = ref(false)

onMounted(() => {
  fetchUsers()
})

const fetchUsers = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/users/')
    
    if (response.data.success) {
      users.value = response.data.data
    } else {
      ElMessage.error(response.data.message || 'Failed to fetch users')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'An error occurred while fetching users')
  }
}

const handleImageUpload = (file) => {
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  
  // Reset status message when new image is uploaded
  statusMessage.value = ''
  statusSuccess.value = false
  
  // Prevent upload to server at this point
  return false
}

const registerFace = async () => {
  if (!imageFile.value) {
    ElMessage.error('Please select an image first')
    return
  }
  
  if (!selectedUserId.value) {
    ElMessage.error('Please select a user first')
    return
  }
  
  loading.value = true
  statusMessage.value = ''
  
  try {
    // Convert image to base64
    const base64 = await fileToBase64(imageFile.value)
    
    // Prepare request
    const requestData = {
      user_id: selectedUserId.value,
      image_data: base64,
      image_format: imageFile.value.type.split('/')[1] || 'jpg'
    }
    
    // Call backend API
    const response = await axios.post(
      'http://localhost:8000/api/v1/register-face',
      requestData
    )
    
    if (response.data.success) {
      statusSuccess.value = true
      statusMessage.value = 'Face registered successfully!'
      ElMessage.success('Face registered successfully')
    } else {
      statusSuccess.value = false
      statusMessage.value = response.data.message || 'Registration failed'
      ElMessage.error(response.data.message || 'Registration failed')
    }
  } catch (error) {
    statusSuccess.value = false
    statusMessage.value = error.response?.data?.detail || 'An error occurred during registration'
    ElMessage.error(error.response?.data?.detail || 'An error occurred during registration')
  } finally {
    loading.value = false
  }
}

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}
</script>

<style scoped>
.face-register {
  padding: 25px;
}

.upload-section {
  text-align: center;
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.image-uploader {
  margin-bottom: 25px;
  flex-grow: 1;
}

.uploader-icon {
  font-size: 68px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  margin: 0 auto;
  transition: all 0.3s;
}

.uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.uploader-text {
  font-size: 16px;
  color: #606266;
  margin-top: 15px;
}

.uploader-hint {
  font-size: 14px;
  color: #909399;
  margin: 10px 0 0;
}

.register-btn {
  margin-top: 20px;
  width: 100%;
  max-width: 300px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
}

.result-section {
  min-height: 400px;
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.status-message {
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.status-message.success {
  background-color: #f0f9ec;
  color: #67c23a;
  border: 1px solid #67c23a;
}

.status-message.error {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.status-message .el-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.status-message .success-icon {
  color: #67c23a;
}

.status-message .error-icon {
  color: #f56c6c;
}

.status-message p {
  margin: 0;
  font-size: 16px;
}

.preview-container {
  margin-top: 30px;
}

.preview-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
  text-align: center;
  min-height: 300px;
}
</style>