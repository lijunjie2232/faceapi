<template>
  <div class="user-manager component-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="table-container">
          <div class="header-actions">
            <h3 class="section-header">Manage Users</h3>
            <div class="header-buttons">
              <el-button type="primary" @click="openDrawer" :icon="Plus">
                Add User
              </el-button>
              <el-button type="success" @click="refreshUsers" :icon="Refresh" :loading="loading" plain>
                Refresh
              </el-button>
              <el-dropdown v-if="selectedUsers.length > 0" @command="handleBatchAction">
                <el-button type="warning" :icon="Operation">
                  Batch Actions <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="activate">Activate Selected</el-dropdown-item>
                    <el-dropdown-item command="deactivate">Deactivate Selected</el-dropdown-item>
                    <el-dropdown-item command="reset-password" divided>Reset Password</el-dropdown-item>
                    <el-dropdown-item command="delete-face">Delete Face Data</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <span v-if="selectedUsers.length > 0" class="selection-info">
                {{ selectedUsers.length }} user(s) selected
              </span>
            </div>
          </div>

          <el-card>
            <el-table 
              :data="users" 
              style="width: 100%" 
              v-loading="loading"
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="55"></el-table-column>
              <el-table-column prop="id" label="ID" width="80"></el-table-column>
              <el-table-column prop="username" label="Username" width="120"></el-table-column>
              <el-table-column prop="email" label="Email" min-width="200"></el-table-column>
              <el-table-column prop="full_name" label="Full Name" width="120"></el-table-column>
              <el-table-column prop="head_pic" label="Face Data" min-width="150">
                <template #default="scope">
                  <el-button :type="scope.row.head_pic === '1' ? 'success' : 'danger'" size="small"
                    @click="openFaceDetection(scope.row)" @mouseenter="handleMouseEnter(scope.row.id)"
                    @mouseleave="handleMouseLeave" plain>
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
              <el-table-column prop="is_active" label="Status" width="80">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.is_active"
                    :active-value="true"
                    :inactive-value="false"
                    @change="handleStatusChange(scope.row)"
                    :loading="statusLoading[scope.row.id]"
                  >
                    <template #active-action>
                      <el-icon><CircleCheckFilled /></el-icon>
                    </template>
                    <template #inactive-action>
                      <el-icon><RemoveFilled /></el-icon>
                    </template>
                  </el-switch>
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
              <el-table-column label="Actions" min-width="220" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="editUser(scope.row)" type="primary">
                    <el-icon>
                      <Edit />
                    </el-icon>
                    Edit
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteUser(scope.row.id)" plain>
                    <el-icon>
                      <Delete />
                    </el-icon>
                    Delete
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="table-footer">
              <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
                :current-page="pagination.page" :page-sizes="[5, 10, 20, 50]" :page-size="pagination.size"
                layout="total, sizes, prev, pager, next, jumper" :total="pagination.total"
                style="margin-top: 20px; text-align: right;"></el-pagination>
              <div class="footer-actions">
                <el-button type="success" @click="refreshUsers" :icon="Refresh" :loading="loading" size="large" plain>
                  Refresh List
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 右侧抽屉表单 -->
    <el-drawer v-model="drawerVisible" :title="formTitle" direction="rtl" size="500px"
      :before-close="handleDrawerClose">
      <div class="drawer-content">
        <el-form :model="userForm" :rules="formRules" ref="userFormRef" label-width="120px">
          <el-form-item label="Username" prop="username">
            <el-input v-model="userForm.username" placeholder="Enter username"></el-input>
          </el-form-item>

          <el-form-item label="Email" prop="email">
            <el-input v-model="userForm.email" placeholder="Enter email address"></el-input>
          </el-form-item>

          <el-form-item label="Full Name" prop="full_name">
            <el-input v-model="userForm.full_name" placeholder="Enter full name"></el-input>
          </el-form-item>

          <el-form-item label="Role" v-if="userForm.id">
            <el-switch v-model="userForm.is_admin" active-text="Admin" inactive-text="User" />
          </el-form-item>

          <el-form-item label="Status">
            <el-switch v-model="userForm.is_active">
              <template #active-action>
                <el-icon><CircleCheckFilled /></el-icon>
              </template>
              <template #inactive-action>
                <el-icon><RemoveFilled /></el-icon>
              </template>
            </el-switch>
          </el-form-item>

          <el-form-item label="Password" :prop="!userForm.id ? 'password' : ''" :required="!userForm.id">
            <el-input v-model="userForm.password" type="password"
              :placeholder="userForm.id ? 'Leave blank to keep current password' : 'Enter password'"></el-input>
          </el-form-item>

          <div class="form-actions">
            <el-button type="primary" @click="submitForm" :loading="submitting" style="flex: 1;">
              <span>{{ userForm.id ? 'Update User' : 'Create User' }}</span>
            </el-button>

            <el-button @click="resetForm" v-if="userForm.id" style="flex: 1; margin-left: 10px;">
              Cancel
            </el-button>
          </div>
        </el-form>
      </div>
    </el-drawer>

    <!-- 密码重置对话框 -->
    <el-dialog
      v-model="passwordResetDialogVisible"
      title="Reset Password"
      width="400px"
      :before-close="handlePasswordResetCancel"
    >
      <el-form
        :model="{ newPassword }"
        :rules="passwordResetRules"
        ref="passwordResetFormRef"
        label-width="120px"
      >
        <el-form-item label="New Password" prop="newPassword">
          <el-input
            v-model="newPassword"
            type="password"
            placeholder="Enter new password"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm new password"
            show-password
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handlePasswordResetCancel">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="confirmPasswordReset"
            :loading="submitting"
          >
            Reset Password
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, CircleCheckFilled, RemoveFilled, Operation, ArrowDown } from '@element-plus/icons-vue'
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
// 添加状态更新loading状态
const statusLoading = ref({})
// 添加多选状态管理
const selectedUsers = ref([])
// 添加密码重置相关状态
const passwordResetDialogVisible = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const passwordResetFormRef = ref()

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

const passwordResetRules = computed(() => {
  return {
    newPassword: [
      { required: true, message: 'Please enter a new password', trigger: 'blur' },
      { min: 6, message: 'Password should be at least 6 characters', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: 'Please confirm the password', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          if (value !== newPassword.value) {
            callback(new Error('Passwords do not match'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
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
    const token = localStorage.getItem('token')
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
    const token = localStorage.getItem('token')
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

const handleStatusChange = async (user) => {
  try {
    statusLoading.value[user.id] = true
    
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/admin/users/${user.id}`,
      {
        is_active: user.is_active
      },
      { headers }
    )
    
    if (response.data.success) {
      ElMessage.success(`User ${user.is_active ? 'activated' : 'deactivated'} successfully`)
    } else {
      // Revert the change if API call fails
      user.is_active = !user.is_active
      ElMessage.error(response.data.message || 'Failed to update user status')
    }
  } catch (error) {
    // Revert the change if API call fails
    user.is_active = !user.is_active
    ElMessage.error(error.response?.data?.detail || 'Failed to update user status')
  } finally {
    statusLoading.value[user.id] = false
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

    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    await axios.delete(`${API_BASE_URL}/api/v1/users/${userId}`, { headers })
    ElMessage.success('User deleted successfully')
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Failed to delete user')
  }
}

const refreshUsers = async () => {
  loading.value = true
  try {
    await fetchUsers()
    ElMessage.success('User list refreshed successfully')
  } catch (error) {
    ElMessage.error('Failed to refresh user list')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const handleBatchAction = async (command) => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('Please select at least one user')
    return
  }

  try {
    switch (command) {
      case 'activate':
        await batchUpdateStatus(true)
        break
      case 'deactivate':
        await batchUpdateStatus(false)
        break
      case 'reset-password':
        await batchResetPassword()
        break
      case 'delete-face':
        await batchDeleteFace()
        break
    }
  } catch (error) {
    console.error('Batch operation failed:', error)
  }
}

const batchUpdateStatus = async (isActive) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to ${isActive ? 'activate' : 'deactivate'} ${selectedUsers.value.length} user(s)?`,
      'Confirm Batch Action',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    // 使用新的批量操作API端点
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/admin/batch/${isActive ? 'active' : 'inactive'}`,
      {
        user_ids: selectedUsers.value.map(user => user.id)
      },
      { headers }
    )

    if (response.data.success) {
      const result = response.data.data
      ElMessage.success(`Successfully ${isActive ? 'activated' : 'deactivated'} ${result.success_count} of ${result.total_count} user(s)`)
      
      // 更新本地用户状态
      selectedUsers.value.forEach(user => {
        const userIndex = users.value.findIndex(u => u.id === user.id)
        if (userIndex !== -1) {
          users.value[userIndex].is_active = isActive
        }
      })
    } else {
      ElMessage.error(response.data.message || 'Batch operation failed')
    }

    // 清除选择并刷新列表
    selectedUsers.value = []
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || 'Batch operation failed')
    }
  }
}

const batchResetPassword = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to reset passwords for ${selectedUsers.value.length} user(s)?`,
      'Confirm Password Reset',
      {
        confirmButtonText: 'Continue',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    // Show password input dialog
    newPassword.value = ''
    confirmPassword.value = ''
    passwordResetDialogVisible.value = true
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Password reset cancelled')
    }
  }
}

const confirmPasswordReset = async () => {
  try {
    await passwordResetFormRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    // 使用新的批量重置密码API端点
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/admin/batch/reset-password`,
      {
        user_ids: selectedUsers.value.map(user => user.id),
        value: newPassword.value
      },
      { headers }
    )

    if (response.data.success) {
      const result = response.data.data
      ElMessage.success(`Successfully reset passwords for ${result.success_count} of ${result.total_count} user(s)`)
    } else {
      ElMessage.error(response.data.message || 'Password reset failed')
    }

    // 关闭对话框并清除选择
    passwordResetDialogVisible.value = false
    newPassword.value = ''
    confirmPassword.value = ''
    selectedUsers.value = []
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Password reset failed')
  } finally {
    submitting.value = false
  }
}

const handlePasswordResetCancel = () => {
  passwordResetDialogVisible.value = false
  newPassword.value = ''
  confirmPassword.value = ''
  passwordResetFormRef.value?.clearValidate()
}

const batchDeleteFace = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete face data for ${selectedUsers.value.length} user(s)? This action cannot be undone.`,
      'Confirm Face Data Deletion',
      {
        confirmButtonText: 'Delete Face Data',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
    )

    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    // 使用新的批量重置面部数据API端点
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/admin/batch/reset-face`,
      {
        user_ids: selectedUsers.value.map(user => user.id)
      },
      { headers }
    )

    if (response.data.success) {
      const result = response.data.data
      ElMessage.success(`Successfully deleted face data for ${result.success_count} of ${result.total_count} user(s)`)
      
      // 更新用户列表中的人脸状态
      selectedUsers.value.forEach(user => {
        const userIndex = users.value.findIndex(u => u.id === user.id)
        if (userIndex !== -1) {
          users.value[userIndex].head_pic = '0' // 标记为人脸数据已删除
        }
      })
    } else {
      ElMessage.error(response.data.message || 'Face data deletion failed')
    }

    // 清除选择并刷新列表
    selectedUsers.value = []
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || 'Face data deletion failed')
    }
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
  flex-wrap: wrap;
  gap: 15px;
}

.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.section-header {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  flex: 1;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.footer-actions {
  display: flex;
  align-items: center;
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

.selection-info {
  margin-left: 15px;
  color: #606266;
  font-size: 14px;
  background: #f5f7fa;
  padding: 5px 10px;
  border-radius: 4px;
}

/* Responsive adjustments for header actions */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .selection-info {
    margin-left: 0;
    margin-top: 10px;
    text-align: center;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-buttons {
    justify-content: center;
  }
  
  .table-footer {
    flex-direction: column;
    align-items: stretch;
  }
  
  .footer-actions {
    justify-content: center;
  }
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