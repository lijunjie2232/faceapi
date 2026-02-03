<template>
  <div class="user-manager component-container">
    <el-row :gutter="30">
      <el-col :lg="16" :xl="17">
        <div class="table-container">
          <h3 class="section-header">Manage Users</h3>
          
          <el-card>
            <el-table :data="users" style="width: 100%" v-loading="loading">
              <el-table-column prop="id" label="ID" width="80"></el-table-column>
              <el-table-column prop="username" label="Username"></el-table-column>
              <el-table-column prop="email" label="Email"></el-table-column>
              <el-table-column prop="full_name" label="Full Name"></el-table-column>
              <el-table-column prop="is_active" label="Active" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                    {{ scope.row.is_active ? 'Yes' : 'No' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="Created At" width="180"></el-table-column>
              <el-table-column label="Actions" width="180">
                <template #default="scope">
                  <el-button size="small" @click="editUser(scope.row)" type="primary" plain>
                    Edit
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="deleteUser(scope.row.id)"
                    plain
                  >
                    Delete
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="pagination.page"
              :page-sizes="[5, 10, 20, 50]"
              :page-size="pagination.size"
              layout="total, sizes, prev, pager, next, jumper"
              :total="pagination.total"
              style="margin-top: 20px; text-align: right;"
            ></el-pagination>
          </el-card>
        </div>
      </el-col>
      
      <el-col :lg="8" :xl="7">
        <el-affix :offset="80" class="affix-form">
          <el-card class="form-section">
            <template #header>
              <div class="card-header">
                <h3>{{ formTitle }}</h3>
              </div>
            </template>
            
            <el-form :model="userForm" :rules="formRules" ref="userFormRef" label-width="120px">
              <el-form-item label="Username" prop="username">
                <el-input 
                  v-model="userForm.username" 
                  :disabled="!!userForm.id"
                  placeholder="Enter username"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="Email" prop="email">
                <el-input 
                  v-model="userForm.email" 
                  placeholder="Enter email address"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="Full Name" prop="full_name">
                <el-input 
                  v-model="userForm.full_name" 
                  placeholder="Enter full name"
                ></el-input>
              </el-form-item>
              
              <el-form-item 
                label="Password" 
                :prop="!userForm.id ? 'password' : ''"
                :required="!userForm.id"
              >
                <el-input 
                  v-model="userForm.password" 
                  type="password" 
                  :placeholder="userForm.id ? 'Leave blank to keep current password' : 'Enter password'"
                ></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="submitForm"
                  :loading="submitting"
                  style="width: 100%;"
                >
                  <span>{{ userForm.id ? 'Update User' : 'Create User' }}</span>
                </el-button>
                
                <el-button 
                  @click="resetForm" 
                  v-if="userForm.id"
                  style="width: 100%; margin-top: 10px;"
                >
                  Cancel
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-affix>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const userFormRef = ref()

const userForm = reactive({
  id: undefined,
  username: '',
  email: '',
  full_name: '',
  password: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const formRules = computed(() => {
  return {
    username: [
      { required: true, message: 'Please enter a username', trigger: 'blur' },
      { min: 3, max: 30, message: 'Length should be 3 to 30 characters', trigger: 'blur' }
    ],
    email: [
      { required: true, message: 'Please enter an email address', trigger: 'blur' },
      { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
    ],
    password: [
      { required: !userForm.id, message: 'Please enter a password', trigger: 'blur' },
      { min: 6, message: 'Password should be at least 6 characters', trigger: 'blur' }
    ]
  }
})

const formTitle = computed(() => {
  return userForm.id ? 'Edit User' : 'Create New User'
})

onMounted(() => {
  fetchUsers()
})

const fetchUsers = async () => {
  loading.value = true
  try {
    // Get token from localStorage and set in header
    const token = localStorage.getItem('token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/admin/users?skip=${(pagination.page - 1) * pagination.size}&limit=${pagination.size}`,
      { headers }
    )
    
    if (response.data.success) {
      users.value = response.data.data.map(user => ({
        ...user,
        created_at: new Date(user.created_at).toLocaleString()
      }))
      pagination.total = response.data.total || users.value.length
    } else {
      ElMessage.error(response.data.message || 'Failed to fetch users')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'An error occurred while fetching users')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchUsers()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchUsers()
}

const editUser = (user) => {
  Object.assign(userForm, user)
}

const resetForm = () => {
  userForm.id = undefined
  userForm.username = ''
  userForm.email = ''
  userForm.full_name = ''
  userForm.password = ''
  userFormRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await userFormRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  
  try {
    let response
    // Get token from localStorage and set in header
    const token = localStorage.getItem('userToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    if (userForm.id) {
      // Update existing user
      response = await axios.put(
        `${API_BASE_URL}/api/v1/users/${userForm.id}`,
        {
          username: userForm.username,
          email: userForm.email,
          full_name: userForm.full_name,
          ...(userForm.password && { password: userForm.password })
        },
        { headers }
      )
    } else {
      // Create new user
      response = await axios.post(
        `${API_BASE_URL}/api/v1/users/`,
        {
          username: userForm.username,
          email: userForm.email,
          full_name: userForm.full_name,
          password: userForm.password
        },
        { headers }
      )
    }
    
    if (response.data.success) {
      ElMessage.success(
        userForm.id ? 'User updated successfully' : 'User created successfully'
      )
      resetForm()
      fetchUsers()
    } else {
      ElMessage.error(response.data.message || 'Operation failed')
    }
  } catch (error) {
    ElMessage.error(
      error.response?.data?.detail || 
      (userForm.id ? 'Failed to update user' : 'Failed to create user')
    )
  } finally {
    submitting.value = false
  }
}

const deleteUser = async (userId) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this user? This action cannot be undone.',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    // Get token from localStorage and set in header
    const token = localStorage.getItem('userToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    await axios.delete(`${API_BASE_URL}/api/v1/users/${userId}`, { headers })
    ElMessage.success('User deleted successfully')
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Failed to delete user')
  }
}
</script>

<style scoped>
.user-manager {
  padding: 25px;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 25px;
}

.form-section {
  border-radius: 12px;
}

.form-section .el-card__body {
  padding: 20px;
}

.affix-form {
  top: 90px;
}

.card-header {
  padding-bottom: 0;
  margin-bottom: -5px;
}
</style>