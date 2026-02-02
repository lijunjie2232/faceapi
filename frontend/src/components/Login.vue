<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="card-title">Login to Face Recognition System</h2>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="Username" 
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="Password" 
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="submit-btn" 
            @click="handleLogin"
            :loading="isLoading"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="signup-section">
        <p>Don't have an account? <router-link to="/signup" class="link">Sign up here</router-link></p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const isLoading = ref(false)
const loginFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('Password is required'))
  } else if (value.length < 6) {
    callback(new Error('Password must be at least 6 characters'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: 'Please input username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be between 3 and 20 characters', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isLoading.value = true
        
        // Create FormData object to send form-data as required
        const formData = new FormData();
        formData.append('username', loginForm.username);
        formData.append('password', loginForm.password);
        
        const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/login`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.token) {
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('username', loginForm.username)
          ElMessage.success('Login successful!')
          router.push('/dashboard') // Redirect to dashboard or home page
        } else {
          ElMessage.error('Login failed: Invalid credentials')
        }
      } catch (error) {
        console.error('Login error:', error)
        if (error.response) {
          ElMessage.error(error.response.data.message || 'Login failed')
        } else {
          ElMessage.error('Network error or server is unreachable')
        }
      } finally {
        isLoading.value = false
      }
    } else {
      ElMessage.warning('Please fill in all required fields correctly')
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-weight: 500;
}

.login-form {
  margin-top: 20px;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
}

.signup-section {
  text-align: center;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.link {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

.link:hover {
  color: #327de8;
  text-decoration: underline;
}
</style>