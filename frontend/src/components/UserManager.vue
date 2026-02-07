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

          <!-- Search Filters Section -->
          <div class="filter-section">
            <el-space wrap :size="10" class="filter-tags">
              <el-tag v-for="tag in filterTags" :key="tag.name" closable :type="getFilterTagType(tag.name)"
                @close="removeFilterTag(tag.name)" round>
                {{ tag.label }}: {{ tag.value }}
              </el-tag>

              <el-button type="info" size="middle" icon="Plus" @click="showFilterDialog = true" round plain>
                Filte By Column
              </el-button>
            </el-space>
          </div>

          <el-card>
            <el-table :data="users" style="width: 100%" v-loading="loading" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="55"></el-table-column>
              <el-table-column prop="id" label="ID" width="80"></el-table-column>
              <el-table-column prop="username" label="Username" width="120"></el-table-column>
              <el-table-column prop="email" label="Email" min-width="200"></el-table-column>
              <el-table-column prop="full_name" label="Full Name" width="200"></el-table-column>
              <el-table-column prop="head_pic" label="Face Data" min-width="100">
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
                  <el-tag :type="scope.row.is_admin ? 'danger' : 'info'" size="middle" round>
                    {{ scope.row.is_admin ? 'Admin' : 'User' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="Status" width="80">
                <template #default="scope">
                  <el-switch v-model="scope.row.is_active" :active-value="true" :inactive-value="false"
                    @change="handleStatusChange(scope.row)" :loading="statusLoading[scope.row.id]">
                    <template #active-action>
                      <el-icon>
                        <CircleCheckFilled />
                      </el-icon>
                    </template>
                    <template #inactive-action>
                      <el-icon>
                        <RemoveFilled />
                      </el-icon>
                    </template>
                  </el-switch>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="Created" width="160">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="Last Updated" width="160">
                <template #default="scope">
                  {{ formatDate(scope.row.updated_at) }}
                </template>
              </el-table-column>
              <el-table-column label="Actions" min-width="140" fixed="right">
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

    <!-- Filter Dialog -->
    <el-dialog v-model="showFilterDialog" title="Add Filter" width="500px" :before-close="closeFilterDialog">
      <el-form :model="filterForm" label-width="120px">
        <el-form-item label="Filter Type">
          <el-select v-model="filterForm.key" placeholder="Select filter type" @change="onFilterKeyChange"
            style="width: 100%;">
            <el-option v-for="option in filterOptions" :key="option.value" :label="option.label" :value="option.value">
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item v-if="['username', 'email', 'full_name'].includes(filterForm.key)"
          :label="filterOptions.find(o => o.value === filterForm.key)?.label || 'Value'">
          <el-input v-model="filterForm.value" placeholder="Enter value" @keyup.enter="addFilterTag">
          </el-input>
        </el-form-item>

        <el-form-item v-else-if="['is_active', 'is_admin', 'set_face'].includes(filterForm.key)"
          :label="filterOptions.find(o => o.value === filterForm.key)?.label || 'Value'">
          <el-select v-model="filterForm.value" placeholder="Select value" style="width: 100%;">
            <el-option label="Yes" :value="true"></el-option>
            <el-option label="No" :value="false"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item v-else label="Value">
          <el-input v-model="filterForm.value" placeholder="Enter value" @keyup.enter="addFilterTag">
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeFilterDialog">Cancel</el-button>
          <el-button type="primary" @click="addFilterTag"
            :disabled="!filterForm.key || (filterForm.value !== false && !filterForm.value)">
            Add Filter
          </el-button>
        </div>
      </template>
    </el-dialog>

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
                <el-icon>
                  <CircleCheckFilled />
                </el-icon>
              </template>
              <template #inactive-action>
                <el-icon>
                  <RemoveFilled />
                </el-icon>
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
    <el-dialog v-model="passwordResetDialogVisible" title="Reset Password" width="400px"
      :before-close="handlePasswordResetCancel">
      <el-form :model="{ newPassword, confirmPassword }" :rules="passwordResetRules" ref="passwordResetFormRef"
        label-width="120px">
        <el-form-item label="New Password" prop="newPassword">
          <el-input v-model="newPassword" type="password" placeholder="Enter new password" show-password
            @input="validatePasswordMatch"></el-input>
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirmPassword" :validate-status="passwordMatchStatus"
          :help="passwordMatchMessage">
          <el-input v-model="confirmPassword" type="password" placeholder="Confirm new password" show-password
            @input="validatePasswordMatch">
            <template #suffix>
              <el-icon v-if="passwordMatchStatus === 'success'" class="password-match-icon success">
                <Check />
              </el-icon>
              <el-icon v-else-if="passwordMatchStatus === 'error'" class="password-match-icon error">
                <Close />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handlePasswordResetCancel">Cancel</el-button>
          <el-button type="primary" @click="confirmPasswordReset" :loading="submitting" :disabled="!isPasswordValid">
            Reset Password
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Face Detection Pop-out Window -->
    <FaceDetectionPopOut v-model="showFaceDetectionPopOut" :_handler="updateUserFace" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, CircleCheckFilled, RemoveFilled, Operation, ArrowDown, Check, Close } from '@element-plus/icons-vue'
import FaceDetectionPopOut from './FaceDetectionPopOut.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const userFormRef = ref()
const drawerVisible = ref(false)
const showFaceDetectionPopOut = ref(false)  // Changed from faceDetectionVisible
// const currentUserToken = ref('')
const selectedUserForFace = ref(null)
// const currentUserRole = ref(false) // 当前用户是否为管理员
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

// 添加搜索过滤相关状态
const filterTags = ref([])
const showFilterDialog = ref(false)
const filterForm = reactive({
  key: '',
  value: ''
})

// 添加密码确认验证状态
const passwordMatchStatus = ref('')
const passwordMatchMessage = ref('')

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

const filterOptions = [
  { value: 'username', label: 'Username' },
  { value: 'email', label: 'Email' },
  { value: 'full_name', label: 'Full Name' },
  { value: 'is_active', label: 'Active Status' },
  { value: 'is_admin', label: 'Admin Role' },
  { value: 'set_face', label: 'Has Face Data' }
]

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
      { min: 6, message: 'Password should be at least 6 characters', trigger: 'blur' }
    ]
  }
})

const formTitle = computed(() => {
  return userForm.id ? 'Edit User' : 'Create New User'
})

// // 判断当前用户是否可以修改角色（只有管理员可以修改角色）
// const canModifyRole = computed(() => {
//   return currentUserRole.value === true
// })

onMounted(() => {
  fetchUsers()
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    // 构建查询参数
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }

    // 添加过滤参数
    filterTags.value.forEach(tag => {
      params[tag.name] = tag.value
    })

    const queryParams = new URLSearchParams(params).toString()

    const response = await axios.get(
      `${API_BASE_URL}/api/v1/admin/users?${queryParams}`,
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
  pagination.page = 1
  pagination.size = size
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
      ...(userForm.password && { password: userForm.password }),
      is_admin: userForm.is_admin,
    }


    if (userForm.id) {
      // Update existing user
      response = await axios.put(
        `${API_BASE_URL}/api/v1/admin/users/${userForm.id}`,
        userData,
        { headers }
      )
    } else {
      // Create new user
      response = await axios.post(
        `${API_BASE_URL}/api/v1/admin/users/`,
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
  showFaceDetectionPopOut.value = true  // Changed from faceDetectionVisible.value = true
}

// 添加鼠标事件处理方法
const handleMouseEnter = (userId) => {
  hoveredUserId.value = userId
}

const handleMouseLeave = () => {
  hoveredUserId.value = null
}


// Function to update a user's face as an admin
const updateUserFace = async (imageData) => {
  try {
    // Create FormData to send image as form data
    const formData = new FormData();

    // get userId
    const userId = selectedUserForFace.value.id;

    // get token
    const token = localStorage.getItem('token') || '';

    // Convert base64 image data to blob and append to form data
    const byteCharacters = atob(imageData.split(',')[1]); // Remove data:image/jpeg;base64, prefix
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
      const slice = byteCharacters.slice(offset, offset + 512);
      const byteNumbers = new Array(slice.length);

      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }

    const blob = new Blob(byteArrays, { type: 'image/jpeg' });
    formData.append('image', blob, 'face_image.jpg');

    // Upload the captured image to update the specified user's face
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/admin/face/${userId}`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    // Check if response has the expected structure with 'code' field
    if (response.data.code === 200 || response.data.success) {
      ElMessage.success(response.data.message || 'Face image updated successfully');

      // Update user list to reflect the new face data
      const userIndex = users.value.findIndex(u => u.id === userId);
      if (userIndex !== -1) {
        users.value[userIndex].head_pic = '1'; // Mark as having face data
      }
    } else {
      ElMessage.error(response.data.message || 'Failed to update face image');
    }

    // return response.data;
  } catch (error) {
    // console.error('Error updating user face image:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error(error.message || 'An error occurred while updating face image');
    }
    throw error;
  }
  finally {

    // refresh user list
    fetchUsers();
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
    // console.error('Batch operation failed:', error)
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
    passwordMatchStatus.value = ''
    passwordMatchMessage.value = ''
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

// 密码匹配验证方法
const validatePasswordMatch = () => {
  if (!confirmPassword.value) {
    passwordMatchStatus.value = ''
    passwordMatchMessage.value = ''
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    passwordMatchStatus.value = 'error'
    passwordMatchMessage.value = 'Passwords do not match'
  } else {
    passwordMatchStatus.value = 'success'
    passwordMatchMessage.value = 'Passwords match'
  }
}

// 计算密码是否有效（用于禁用提交按钮）
const isPasswordValid = computed(() => {
  return newPassword.value.length >= 6 &&
    confirmPassword.value.length >= 6 &&
    newPassword.value === confirmPassword.value
})

const handlePasswordResetCancel = () => {
  passwordResetDialogVisible.value = false
  newPassword.value = ''
  confirmPassword.value = ''
  passwordMatchStatus.value = ''
  passwordMatchMessage.value = ''
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

// 新增过滤标签相关方法
const onFilterKeyChange = () => {
  filterForm.value = ''
}

const addFilterTag = () => {
  if (!filterForm.key || (filterForm.value !== false && !filterForm.value)) return

  // 获取标签显示名称
  const option = filterOptions.find(opt => opt.value === filterForm.key)
  const label = option ? option.label : filterForm.key

  // 检查是否已经存在相同的过滤条件，如果存在则替换
  const existingIndex = filterTags.value.findIndex(tag => tag.name === filterForm.key)
  if (existingIndex !== -1) {
    // 替换现有的过滤条件
    filterTags.value[existingIndex] = {
      name: filterForm.key,
      value: filterForm.value,
      label: label,
      type: getFilterTagType(filterForm.key)
    }
  } else {
    // 添加新标签
    filterTags.value.push({
      name: filterForm.key,
      value: filterForm.value,
      label: label,
      type: getFilterTagType(filterForm.key)
    })
  }

  // 重置选择器
  filterForm.key = ''
  filterForm.value = ''

  // 关闭对话框
  showFilterDialog.value = false

  // 重新获取用户列表
  pagination.page = 1
  fetchUsers()
}

const removeFilterTag = (tagName) => {
  const index = filterTags.value.findIndex(tag => tag.name === tagName)
  if (index !== -1) {
    filterTags.value.splice(index, 1)
    fetchUsers()
  }
}

// 新增方法：打开过滤器对话框
const closeFilterDialog = () => {
  showFilterDialog.value = false
  filterForm.key = ''
  filterForm.value = ''
}

// 添加计算属性来获取不同过滤类型的标签颜色
const getFilterTagType = (filterName) => {
  switch (filterName) {
    case 'username':
      return 'info'
    case 'email':
      return 'warning'
    case 'full_name':
      return 'success'
    case 'is_active':
      return 'primary'
    case 'is_admin':
      return 'danger'
    case 'set_face':
      return 'warning'
    default:
      return 'primary'
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

.filter-section {
  margin-bottom: 20px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: center;
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

/* 对话框底部样式 */
:deep(.el-dialog__footer) {
  text-align: right;
}
</style>