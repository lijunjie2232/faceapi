<template>
  <div class="signup-container">
    <el-card class="signup-card">
      <h2>Sign Up</h2>
      <el-form :model="signupForm" :rules="signupRules" ref="signupFormRef" label-width="150px" class="signup-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="signupForm.username" placeholder="Enter a username"></el-input>
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="signupForm.email" type="email" placeholder="Enter your email"></el-input>
        </el-form-item>
        <el-form-item label="Full Name" prop="full_name">
          <el-input v-model="signupForm.full_name" placeholder="Enter your full name"></el-input>
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="signupForm.password" type="password" placeholder="Enter your password"></el-input>
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input v-model="signupForm.confirmPassword" type="password" placeholder="Confirm your password"></el-input>
        </el-form-item>
        <el-form-item>
          <div class="button-group">
            <el-button type="primary" @click="handleSignup" :loading="signupLoading">Sign Up</el-button>
          </div>
        </el-form-item>
      </el-form>
      <p>Already have an account? <router-link to="/login">Login</router-link></p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const signupForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: ''
})

const signupRules = {
  username: [
    { required: true, message: 'Please enter a username', trigger: 'blur' },
    { min: 3, message: 'Username should be at least 3 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: 'Please enter your full name', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password length should be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== signupForm.password) {
          callback(new Error('Passwords do not match'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const signupFormRef = ref()
const signupLoading = ref(false)

const handleSignup = async () => {
  const valid = await signupFormRef.value.validate().catch(() => { })
  if (!valid) return

  signupLoading.value = true
  try {
    const userData = {
      username: signupForm.username,
      email: signupForm.email,
      full_name: signupForm.full_name,
      password: signupForm.password
    }

    // Using the environment variable for API base URL
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/user/signup`, userData, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.data.code === 200) {
      ElMessage.success('Registration successful! Please login.')
      // Redirect to login page after successful registration
      router.push('/login')
    }
    else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    // console.error('Signup error:', error)
    ElMessage.error(error.response?.data?.message || 'Registration failed')
  } finally {
    signupLoading.value = false
  }
}


</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.signup-card {
  width: 520px;
  padding: 20px;
}

.signup-form {
  margin-top: 20px;
}

/* 调整表单项样式，为长标签提供更多空间 */
.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  text-align: left;
  width: 130px;
  /* 调整标签宽度 */
  padding-right: 10px;
  /* 为标签和输入框之间添加一些间距 */
}

.el-form-item__content {
  flex: 1;
  /* 确保输入框可以充分伸展 */
  min-width: 0;
  /* 防止内容溢出 */
}

.button-group {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
  margin-top: 10px;
}

.button-group .el-button {
  flex: 0 1 auto;
  /* 按钮不需要填充全部空间 */
  min-width: 120px;
  /* 设置最小宽度 */
}
</style>