<template>
  <div class="admin-panel">
    <el-main class="app-main">
      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        <el-tab-pane label="User Management" name="users" class="tab-content">
          <user-manager />
        </el-tab-pane>
        <el-tab-pane label="Face Detection Recognizer" name="detection-recognizer" class="tab-content">
          <face-detection-recognizer />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import UserManager from '@/components/UserManager.vue';
import FaceDetectionRecognizer from '@/components/FaceDetectionRecognizer.vue';

// 设置默认激活的标签页
const activeTab = ref('users');
</script>

<style scoped>
.app-main {
  padding: 20px;
}

.main-tabs {
  min-height: 500px;
}

.tab-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>