<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <h1 class="app-title">
          <el-icon>
            <User />
          </el-icon>
          <span>Face Recognition System</span>
        </h1>
      </el-header>

      <el-main class="app-main">
        <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
          <el-tab-pane label="Face Detection" name="detection" class="tab-content">
            <face-detection />
          </el-tab-pane>
          <el-tab-pane label="Face Recognition" name="recognize" class="tab-content">
            <face-recognizer />
          </el-tab-pane>
          <el-tab-pane label="User Management" name="users" class="tab-content">
            <user-manager />
          </el-tab-pane>
          <el-tab-pane label="Face Registration" name="register" class="tab-content">
            <face-register />
          </el-tab-pane>
        </el-tabs>
      </el-main>

      <el-footer class="app-footer">
        <p class="footer-text">Face Recognition System &copy; {{ currentYear }} | Advanced Facial Recognition Technology
        </p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import FaceRecognizer from './components/FaceRecognizer.vue'
import UserManager from './components/UserManager.vue'
import FaceRegister from './components/FaceRegister.vue'
import FaceDetection from './components/FaceDetection.vue'
import { User } from '@element-plus/icons-vue'

const activeTab = ref('detection')

const currentYear = computed(() => {
  return new Date().getFullYear()
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #409EFF 0%, #327de8 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 80px;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.app-title .el-icon {
  font-size: 32px;
}

.app-main {
  flex: 1;
  padding: 20px 0;
  background-color: #f0f2f5;
}

.main-tabs {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  overflow: hidden;
  border: none;
  height: 100%;
  margin: 12px;
}

.tab-content {
  background: #f9fbfd;
}

.app-footer {
  background-color: #ffffff;
  color: #606266;
  text-align: center;
  line-height: 40px;
  border-top: 1px solid #e6e9f0;
  margin-top: auto;
  padding: 0 20px;
  flex-shrink: 0;
}

.footer-text {
  margin: 0;
  font-size: 14px;
  color: #909399;
}
</style>