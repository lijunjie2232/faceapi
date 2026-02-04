<template>
  <div class="user-manager component-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="table-container">
          <div class="header-actions">
            <h3 class="section-header">Manage Users</h3>
            <el-button 
              type="primary" 
              @click="openDrawer"
              :icon="Plus"
            >
              Add User
            </el-button>
          </div>
          
          <el-card>
            <el-table :data="users" style="width: 100%" v-loading="loading">
              <el-table-column prop="id" label="ID" width="80"></el-table-column>
              <el-table-column prop="username" label="Username" width="120"></el-table-column>
              <el-table-column prop="email" label="Email"></el-table-column>
              <el-table-column prop="full_name" label="Full Name" width="150"></el-table-column>
              <el-table-column prop="head_pic" label="Face Data" width="120">
                <template #default="scope">
                  <el-button 
                    :type="scope.row.head_pic === '1' ? 'success' : 'danger'"
                    size="small"
                    @click="openFaceDetection(scope.row)"
                    @mouseenter="handleMouseEnter(scope.row.id)"
                    @mouseleave="handleMouseLeave"
                    plain
                  >
                    <span>{{ 
                      hoveredUserId === scope.row.id 
                        ? (scope.row.head_pic === '1' ? 'Update face' : 'Add face')
                        : (scope.row.head_pic === '1' ? 'Face Added' : 'No face') 
                    }}</span>
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column prop="is_admin" label="Role" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.is_admin ? 'danger' : 'info'" size="small">
                    {{ scope.row.is_admin ? 'Admin' : 'User' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="Status" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                    {{ scope.row.is_active ? 'Active' : 'Inactive' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="Created" width="180">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="Last Updated" width="180">
                <template #default="scope">
                  {{ formatDate(scope.row.updated_at) }}
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="180" fixed="right">
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
    </el-row>
    
    <!-- 右侧抽屉表单 -->
    <el-drawer
      v-model="drawerVisible"
      :title="formTitle"
      direction="rtl"
      size="500px"
      :before-close="handleDrawerClose"
    >
      <div class="drawer-content">
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
          
          <el-form-item label="Role" v-if="userForm.id">
            <el-switch
              v-model="userForm.is_admin"
              active-text="Admin"
              inactive-text="User"
              :disabled="!canModifyRole"
            />
            <div class="role-hint" v-if="!canModifyRole">
              <el-text size="small" type="info">
                Only admins can modify role permissions
              </el-text>
            </div>
          </el-form-item>
          
          <el-form-item label="Status">
            <el-switch
              v-model="userForm.is_active"
              active-text="Active"
              inactive-text="Inactive"
            />
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
          
          <div class="form-actions">
            <el-button 
              type="primary" 
              @click="submitForm"
              :loading="submitting"
              style="flex: 1;"
            >
              <span>{{ userForm.id ? 'Update User' : 'Create User' }}</span>
            </el-button>
            
            <el-button 
              @click="resetForm" 
              v-if="userForm.id"
              style="flex: 1; margin-left: 10px;"
            >
              Cancel
            </el-button>
          </div>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UserFilled, CirclePlus } from '@element-plus/icons-vue'
import FaceDetectionPopOut from './FaceDetectionPopOut.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const userFormRef = ref()
const drawerVisible = ref(false)
const faceDetectionVisible = ref(false)
const currentUserToken = ref('')
const selectedUserForFace = ref(null)
const currentUserRole = ref(false) // 当前用户是否为管理员
// 添加hover状态管理
const hoveredUserId = ref(null)

const userForm = reactive({
  id: undefined,
  username: '',
  email: '',
  full_name: '',
  is_admin: false,
  is_active: true,
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

// 判断当前用户是否可以修改角色（只有管理员可以修改角色）
const canModifyRole = computed(() => {
  return currentUserRole.value === true
})

onMounted(() => {
  fetchCurrentUser()
  fetchUsers()
})

const fetchCurrentUser = async () => {
  try {
    const token = localStorage.getItem('userToken')
    if (!token) return
    
    currentUserToken.value = token
    const headers = { 'Authorization': `Bearer ${token}` }
    const response = await axios.get(`${API_BASE_URL}/api/v1/users/me`, { headers })
    if (response.data.success) {
      currentUserRole.value = response.data.data.is_admin || false
    }
  } catch (error) {
    console.error('Failed to fetch current user:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/admin/users?skip=${(pagination.page - 1) * pagination.size}&limit=${pagination.size}`,
      { headers }
    )
    
    if (response.data.success) {
      users.value = response.data.data
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

const openDrawer = () => {
  resetForm()
  drawerVisible.value = true
}

const editUser = (user) => {
  Object.assign(userForm, {
    ...user,
    password: '' // 编辑时不显示原密码
  })
  drawerVisible.value = true
}

const handleDrawerClose = (done) => {
  resetForm()
  done()
}

const resetForm = () => {
  userForm.id = undefined
  userForm.username = ''
  userForm.email = ''
  userForm.full_name = ''
  userForm.is_admin = false
  userForm.is_active = true
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
    const token = localStorage.getItem('userToken')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    
    const userData = {
      username: userForm.username,
      email: userForm.email,
      full_name: userForm.full_name,
      is_active: userForm.is_active,
      ...(userForm.password && { password: userForm.password })
    }
    
    // 只有管理员才能修改角色
    if (canModifyRole.value && userForm.id) {
      userData.is_admin = userForm.is_admin
    }
    
    if (userForm.id) {
      // Update existing user
      response = await axios.put(
        `${API_BASE_URL}/api/v1/users/${userForm.id}`,
        userData,
        { headers }
      )
    } else {
      // Create new user
      response = await axios.post(
        `${API_BASE_URL}/api/v1/users/`,
        {
          ...userData,
          password: userForm.password
        },
        { headers }
      )
    }
    
    if (response.data.success) {
      ElMessage.success(
        userForm.id ? 'User updated successfully' : 'User created successfully'
      )
      drawerVisible.value = false
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

const openFaceDetection = (user) => {
  selectedUserForFace.value = user
  faceDetectionVisible.value = true
}

// 添加鼠标事件处理方法
const handleMouseEnter = (userId) => {
  hoveredUserId.value = userId
}

const handleMouseLeave = () => {
  hoveredUserId.value = null
}

const handleFaceCaptured = async (imageData) => {
  try {
    // 更新用户列表中对应用户的人脸状态
    const userIndex = users.value.findIndex(u => u.id === selectedUserForFace.value.id)
    if (userIndex !== -1) {
      users.value[userIndex].head_pic = '1' // 标记为已录入人脸数据
    }
    
    ElMessage.success('Face data updated successfully')
    selectedUserForFace.value = null
  } catch (error) {
    console.error('Error handling face capture:', error)
    ElMessage.error('Failed to update face data')
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
    
    const token = localStorage.getItem('userToken')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    
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

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.drawer-content {
  padding: 20px 0;
}

.form-actions {
  display: flex;
  margin-top: 30px;
  gap: 10px;
}

.role-hint {
  margin-top: 5px;
}

/* 抽屉样式优化 */
:deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

:deep(.el-drawer__body) {
  padding: 0 20px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-input__inner) {
  height: 40px;
}

/* 头像样式优化 */
:deep(.el-avatar) {
  background-color: #409eff;
  color: white;
  font-weight: 500;
}

/* 人脸按钮样式优化 */
:deep(.el-button .el-icon) {
  margin-right: 5px;
}
</style>