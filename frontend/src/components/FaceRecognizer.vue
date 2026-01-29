<template>
  <div class="face-recognizer component-container">
    <el-row :gutter="30" class="main-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" class="col-container">
        <div class="upload-section">
          <h3 class="section-header">Upload Image for Recognition</h3>
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
            @click="recognizeFace"
            :disabled="!imagePreview || loading"
            class="recognize-btn"
          >
            <el-icon><VideoCamera /></el-icon>
            <span>Recognize Face{{ loading ? '...' : '' }}</span>
          </el-button>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="12" :lg="12" class="col-container">
        <div class="result-section">
          <h3 class="section-header">Recognition Results</h3>
          <div v-if="results.length === 0" class="no-results">
            <el-empty description="No results yet" :image-size="100">
              <p>Upload an image and click "Recognize Face" to see results</p>
            </el-empty>
          </div>
          <div v-else class="results-list">
            <el-card 
              v-for="(result, index) in results" 
              :key="index" 
              class="result-item"
              :class="{ 'recognized': result.recognized }"
            >
              <template #header>
                <div class="card-header">
                  <span :class="result.recognized ? 'recognized-text' : 'unknown-text'">
                    {{ result.recognized ? '✅ Recognized' : '❓ Unknown Face' }}
                  </span>
                </div>
              </template>
              <div class="result-content">
                <p><strong>User ID:</strong> {{ result.user_id || 'N/A' }}</p>
                <p><strong>Confidence:</strong> 
                  <el-progress 
                    :percentage="result.confidence ? parseFloat((result.confidence * 100).toFixed(2)) : 0" 
                    :color="result.confidence > 0.7 ? '#67C23A' : result.confidence > 0.5 ? '#E6A23C' : '#F56C6C'"
                    :format="() => result.confidence ? `${(result.confidence * 100).toFixed(2)}%` : 'N/A'"
                  />
                </p>
                <p><strong>Message:</strong> {{ result.message }}</p>
              </div>
            </el-card>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <el-row v-if="imagePreview" :gutter="30" class="preview-row">
      <el-col :span="24">
        <h3 class="section-header">Image Preview</h3>
        <div class="preview-wrapper">
          <img :src="imagePreview" alt="Preview" class="preview-image rounded-img" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { Upload, VideoCamera } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'FaceRecognizer',
  components: {
    Upload,
    VideoCamera
  },
  data() {
    return {
      imagePreview: null,
      imageFile: null,
      results: [],
      loading: false
    }
  },
  methods: {
    handleImageUpload(file) {
      this.imageFile = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
      
      // Prevent upload to server at this point
      return false;
    },
    async recognizeFace() {
      if (!this.imageFile) {
        this.$message.error('Please select an image first');
        return;
      }

      this.loading = true;
      
      try {
        // Convert image to base64
        const base64 = await this.fileToBase64(this.imageFile);
        
        // Prepare request
        const requestData = {
          image_data: base64,
          image_format: this.imageFile.type.split('/')[1] || 'jpg'
        };
        
        // Call backend API
        const response = await axios.post(
          'http://localhost:8000/api/v1/recognize-face',
          requestData
        );
        
        if (response.data.success) {
          this.results = response.data.data.results;
          this.$message.success('Face recognition completed');
        } else {
          this.$message.error(response.data.message || 'Recognition failed');
        }
      } catch (error) {
        this.$message.error(error.response?.data?.detail || 'An error occurred during recognition');
      } finally {
        this.loading = false;
      }
    },
    fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
      });
    }
  }
}
</script>

<style scoped>
.face-recognizer {
  padding: 25px;
}

.main-row {
  margin-bottom: 30px;
}

.col-container {
  margin-bottom: 20px;
}

.upload-section {
  text-align: center;
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.image-uploader {
  margin-bottom: 25px;
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

.recognize-btn {
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
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
  text-align: center;
}

.result-item {
  margin-bottom: 15px;
  border-radius: 8px;
}

.result-item.recognized {
  border-left: 4px solid #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recognized-text {
  color: #67c23a;
  font-weight: bold;
}

.unknown-text {
  color: #e6a23c;
  font-weight: bold;
}

.result-content p {
  margin: 12px 0;
}

.result-content p:last-child {
  margin-bottom: 0;
}

.preview-row {
  margin-top: 30px;
}

.preview-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}
</style>