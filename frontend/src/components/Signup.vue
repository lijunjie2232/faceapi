<template>
  <div class="signup-container">
    <el-card class="signup-card">
      <h2 class="card-title">Create Account</h2>
      
      <el-form :model="signupForm" :rules="rules" ref="signupFormRef" class="signup-form">
        <el-form-item prop="username">
          <el-input 
            v-model="signupForm.username" 
            placeholder="Choose a username" 
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="signupForm.email" 
            type="email" 
            placeholder="Email address" 
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="signupForm.password" 
            type="password" 
            placeholder="Password" 
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="signupForm.confirmPassword" 
            type="password" 
            placeholder="Confirm password" 
            size="large"
            prefix-icon="Unlock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="success" 
            size="large" 
            class="submit-btn" 
            @click="handleSignup"
            :loading="isLoading"
          >
            Sign Up
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-section">
        <p>Already have an account? <router-link to="/login" class="link">Log in here</router-link></p>
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
const signupFormRef = ref()

const signupForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
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

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('Please confirm your password'))
  } else if (value !== signupForm.password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: 'Please input username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be between 3 and 20 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please input email address', trigger: 'blur' },
    { type: 'email', message: 'Please input a valid email address', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleSignup = async () => {
  await signupFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isLoading.value = true
        
        // Create FormData object to send form-data
        const formData = new FormData();
        formData.append('username', signupForm.username);
        formData.append('email', signupForm.email);
        formData.append('password', signupForm.password);
        
        const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/register`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success) {
          ElMessage.success('Account created successfully! Please log in.')
          router.push('/login')
        } else {
          ElMessage.error(response.data.message || 'Registration failed')
        }
      } catch (error) {
        console.error('Signup error:', error)
        if (error.response) {
          ElMessage.error(error.response.data.message || 'Registration failed')
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
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.signup-card {
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

.signup-form {
  margin-top: 20px;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
}

.login-section {
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