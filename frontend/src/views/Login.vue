<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>Login</h2>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="100px" class="login-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="loginForm.username" placeholder="Enter your username"></el-input>
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="Enter your password"></el-input>
        </el-form-item>
        <el-form-item>
          <div class="button-group">
            <el-button type="primary" @click="handleLogin" :loading="loginLoading">Login</el-button>
            <el-button @click="resetForm">Reset</el-button>
          </div>
        </el-form-item>
      </el-form>
      <p>Don't have an account? <router-link to="/signup">Sign Up</router-link></p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: 'Please enter your username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password length should be at least 6 characters', trigger: 'blur' }
  ]
}

const loginFormRef = ref()
const loginLoading = ref(false)

const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => {})
  if (!valid) return

  loginLoading.value = true
  try {
    const formData = new FormData()
    formData.append('username', loginForm.username)
    formData.append('password', loginForm.password)
    
    // Using the environment variable for API base URL
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/user/login`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // Handle the response according to the actual format
    const { access_token, token_type } = response.data
    
    // Store the access token in localStorage with the correct key
    localStorage.setItem('token', `${access_token}`)
    localStorage.setItem('token_type', `${token_type}`)

    console.log('Login successful:', response.data)
    
    // Also store username for display in header
    localStorage.setItem('username', loginForm.username)
    
    ElMessage.success('Login successful!')
    
    // 获取路由参数中的重定向路径，如果有的话
    const redirectPath = route.query.redirect || '/user'
    // Redirect to the intended page or home page
    router.push(redirectPath)
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error(error.response?.data?.detail || 'Login failed')
  } finally {
    loginLoading.value = false
  }
}

const resetForm = () => {
  loginFormRef.value.resetFields()
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-form {
  margin-top: 20px;
}

.button-group {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

.button-group .el-button {
  flex: 1;
}
</style>