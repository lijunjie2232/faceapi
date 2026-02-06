<template>
  <div class="user-dashboard">
    <h2>User Dashboard</h2>
    <p>Welcome to your personal user dashboard. Here you can manage your profile and view your recognition history.</p>

    <div class="user-info">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>Your Profile</span>
            <el-button v-if="!editing" type="primary" size="small" @click="startEditing">
              Edit Profile
            </el-button>
            <div v-else>
              <el-button type="success" size="small" @click="saveProfile" :disabled="updating">
                {{ updating ? 'Updating...' : 'Save Changes' }}
              </el-button>
              <el-button size="small" @click="cancelEditing" :disabled="updating">
                Cancel
              </el-button>
            </div>
          </div>
        </template>

        <div v-if="loading">
          <el-skeleton :rows="4" animated />
        </div>
        <div v-else-if="userInfo && !authError">
          <el-form v-if="!editing" :model="userInfo" label-position="left" class="profile-display">
            <el-form-item label="Username:">
              <span>{{ userInfo.username }}</span>
            </el-form-item>
            <el-form-item label="Email:">
              <span>{{ userInfo.email }}</span>
            </el-form-item>
            <el-form-item label="Full Name:">
              <span>{{ userInfo.full_name }}</span>
            </el-form-item>
            <el-form-item label="ID:">
              <span>{{ userInfo.id }}</span>
            </el-form-item>
            <el-form-item label="Status:">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? 'Active' : 'Inactive' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="Role:">
              <el-tag :type="userInfo.is_admin ? 'warning' : 'info'">
                {{ userInfo.is_admin ? 'Administrator' : 'Regular User' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="Member Since:">
              <span id="memberSince">{{ formatDate(userInfo.created_at) }}</span>
            </el-form-item>
            <el-form-item label="Last Updated:">
              <span id="lastUpdated">{{ formatDate(userInfo.updated_at) }}</span>
            </el-form-item>

            <!-- Head Pic Field -->
            <el-form-item label="Face Image:">
              <div class="head-pic-container">
                <div v-if="userInfo.head_pic" class="head-pic-preview">
                  <img :src="'data:image/jpeg;base64,' + userInfo.head_pic" alt="Face Image Preview"
                    class="head-pic-image" />
                </div>
                <div v-else class="head-pic-placeholder">
                  Image not uploaded
                </div>

                <el-button :type="isHoveringFaceButton ? 'primary' : (userInfo.head_pic ? 'success' : 'warning')"
                  @click="updateFace" @mouseenter="isHoveringFaceButton = true"
                  @mouseleave="isHoveringFaceButton = false" class="face-image-btn">
                  <span class="button-text">
                    {{ isHoveringFaceButton ? (userInfo.head_pic ? 'Update face' : 'Go to set face') :
                      (userInfo.head_pic ?
                        'Face is set' : 'Face is not set') }}
                  </span>
                </el-button>
              </div>
            </el-form-item>
          </el-form>

          <el-form v-else :model="editableInfo" :rules="formRules" ref="profileFormRef" label-position="left"
            class="profile-edit">
            <el-form-item label="Username:" prop="username">
              <el-input v-model="editableInfo.username" placeholder="Username" />
            </el-form-item>
            <el-form-item label="Email:" prop="email">
              <el-input v-model="editableInfo.email" placeholder="Email" />
            </el-form-item>
            <el-form-item label="Full Name:" prop="full_name">
              <el-input v-model="editableInfo.full_name" placeholder="Full Name" />
            </el-form-item>
            <el-form-item label="New Password:" prop="new_password">
              <el-input v-model="editableInfo.new_password" type="password"
                placeholder="Leave blank to keep current password" />
            </el-form-item>
            <el-form-item label="ID:">
              <span>{{ userInfo.id }}</span>
            </el-form-item>
            <el-form-item label="Status:">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? 'Active' : 'Inactive' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="Role:">
              <el-tag :type="userInfo.is_admin ? 'warning' : 'info'">
                {{ userInfo.is_admin ? 'Administrator' : 'Regular User' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="Member Since:">
              <span id="memberSince">{{ formatDate(userInfo.created_at) }}</span>
            </el-form-item>
            <el-form-item label="Last Updated:">
              <span id="lastUpdated">{{ formatDate(userInfo.updated_at) }}</span>
            </el-form-item>

            <!-- Head Pic Field in Edit Mode -->
            <el-form-item label="Face Image:">
              <div class="head-pic-container">
                <div v-if="userInfo.head_pic" class="head-pic-preview">
                  <img :src="'data:image/jpeg;base64,' + userInfo.head_pic" alt="Face Image Preview"
                    class="head-pic-image" />
                </div>
                <div v-else class="head-pic-placeholder">
                  Image not uploaded
                </div>

                <el-button :type="isHoveringFaceButton ? 'primary' : (userInfo.head_pic ? 'success' : 'warning')"
                  @click="updateFace" @mouseenter="isHoveringFaceButton = true"
                  @mouseleave="isHoveringFaceButton = false" class="face-image-btn">
                  <span class="button-text">
                    {{ isHoveringFaceButton ? (userInfo.head_pic ? 'Update face' : 'Go to set face') :
                      (userInfo.head_pic ?
                        'Face is set' : 'Face is not set') }}
                  </span>
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <div v-else-if="authError">
          <p class="auth-error">Authentication failed. Redirecting to login...</p>
        </div>
        <div v-else>
          <p>Error loading user information. Please refresh the page.</p>
        </div>
      </el-card>

      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>Recognition History</span>
          </div>
        </template>
        <p>Recent face recognition logs and activity will appear here.</p>
        <el-table :data="recognitionHistory" style="width: 100%; margin-top: 15px;">
          <el-table-column prop="date" label="Date" width="180"></el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'Success' ? 'success' : 'danger'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="Confidence" width="120"></el-table-column>
          <el-table-column prop="details" label="Details"></el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Face Detection Pop-out Window -->
    <FaceDetectionPopOut v-model="showFaceDetectionPopOut" :_handler="handleFaceCaptured" />
  </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import FaceDetectionPopOut from '../components/FaceDetectionPopOut.vue';

// Inject userInfo from parent component (App)
const injectedUserInfo = inject('userInfo');
const userInfo = ref(null);
const editableInfo = ref({
  username: '',
  email: '',
  full_name: '',
  new_password: ''  // New field for password
});
const loading = ref(true);
const editing = ref(false);
const updating = ref(false);
const authError = ref(false);
const isHoveringFaceButton = ref(false);
const showFaceDetectionPopOut = ref(false);
const recognitionHistory = ref([
  { date: '2023-11-30 14:30:22', status: 'Success', confidence: '98.5%', details: 'Office entrance' },
  { date: '2023-11-30 09:15:47', status: 'Success', confidence: '96.2%', details: 'Main gate' },
  { date: '2023-11-29 18:45:12', status: 'Failed', confidence: '78.1%', details: 'Back entrance' },
  { date: '2023-11-29 08:22:33', status: 'Success', confidence: '95.7%', details: 'Main gate' }
]);
const profileFormRef = ref(null);
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const router = useRouter();

// Inject checkLoginStatus from parent component (App)
const injectedCheckLoginStatus = inject('checkLoginStatus');

// Form validation rules
const formRules = {
  username: [
    { required: true, message: 'Please enter a username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Length should be 3 to 20 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: 'Please enter your full name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Length should be 2 to 50 characters', trigger: 'blur' }
  ],
  new_password: [
    { min: 8, message: 'Password should be at least 8 characters', trigger: 'blur' }
  ]
};

// Function to format dates
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// Function to handle face detection pop-out
const updateFace = () => {
  showFaceDetectionPopOut.value = true;
};

// Start editing profile
const startEditing = () => {
  // Copy current user info to editable fields
  editableInfo.value = {
    username: userInfo.value.username,
    email: userInfo.value.email,
    full_name: userInfo.value.full_name,
    new_password: ''  // Initialize as empty
  };
  editing.value = true;
};

// Function to get token from localStorage
const getToken = () => {
  return localStorage.getItem('token') || '';
};

// Save profile changes
const saveProfile = async () => {
  // Validate form before submitting
  if (!profileFormRef.value) return;

  const valid = await profileFormRef.value.validate().catch(() => false);
  if (!valid) {
    ElMessage.error('Please correct the errors in the form');
    return;
  }

  updating.value = true;

  try {
    const token = getToken();

    // Prepare request data without password initially
    const requestData = {
      username: editableInfo.value.username,
      email: editableInfo.value.email,
      full_name: editableInfo.value.full_name
    };

    // Only add the password field if it's provided
    if (editableInfo.value.new_password && editableInfo.value.new_password.trim() !== '') {
      requestData.password = editableInfo.value.new_password;
    }

    const response = await axios.put(
      `${API_BASE_URL}/api/v1/user/me`,
      requestData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.data.code === 200 || response.data.success) {
      // Update the user info in the app state
      userInfo.value = response.data.data;

      // Update the injected user info in App.vue
      if (injectedUserInfo && injectedUserInfo.value) {
        injectedUserInfo.value = response.data.data;
      }

      editing.value = false;
      ElMessage.success(response.data.message || 'Profile updated successfully');

      // Call checkLoginStatus function from App.vue to refresh user info in header
      if (injectedCheckLoginStatus) {
        injectedCheckLoginStatus();
      }

    } else {
      ElMessage.error(response.data.message || 'Failed to update profile');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error(error.message || 'An error occurred while updating profile');
    }
  } finally {
    updating.value = false;
  }
};

// Cancel editing and revert changes
const cancelEditing = () => {
  ElMessageBox.confirm(
    'Are you sure you want to discard unsaved changes?',
    'Warning',
    {
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
      type: 'warning'
    }
  ).then(() => {
    editing.value = false;
    // Reset editable fields to original values
    editableInfo.value = {
      username: userInfo.value.username,
      email: userInfo.value.email,
      full_name: userInfo.value.full_name,
      new_password: ''
    };
  }).catch(() => {
    // User canceled, continue editing
  });
};

// Watch for changes in the injected userInfo
watch(injectedUserInfo, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0) {
    userInfo.value = newVal;
    loading.value = false;
  } else {
    loading.value = false;
    authError.value = true;
  }
}, { immediate: true });

// Initialize with the current value
if (injectedUserInfo && injectedUserInfo.value && Object.keys(injectedUserInfo.value).length > 0) {
  userInfo.value = injectedUserInfo.value;
  loading.value = false;
} else {
  loading.value = false;
  authError.value = true;
}

// Redirect to login if auth error occurs
watch(authError, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  }
});



// Function to handle face captured from pop-out window
const handleFaceCaptured = async (imageData) => {
  try {
    // Create FormData to send image as form data
    const formData = new FormData();

    // get token
    const token = getToken();

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

    // Upload the captured image to update the user's head pic
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/face/me`,
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
      // Update user info to reflect the new head pic
      if (injectedUserInfo && injectedUserInfo.value) {
        injectedUserInfo.value.head_pic = imageData.split(',')[1]; // Store just the base64 part
      }
    } else {
      ElMessage.error(response.data.message || 'Failed to update face image');
    }
  } catch (error) {
    console.error('Error updating face image:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error(error.message || 'An error occurred while updating face image');
    }
  }
};

</script>

<style scoped>
.user-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  color: #303133;
  margin-bottom: 20px;
}

.user-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.info-card {
  text-align: left;
}

.card-header {
  font-weight: bold;
  color: #303133;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.auth-error {
  color: #f56c6c;
  font-weight: bold;
  text-align: center;
  padding: 20px;
}

.el-table {
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 20px;
}

.profile-display .el-form-item {
  margin-bottom: 12px;
}

.profile-display .el-form-item__label {
  font-weight: bold;
  color: #606266;
  width: 120px;
}

.profile-display .el-form-item__content {
  display: block;
  font-size: 14px;
}

.profile-edit .el-form-item {
  margin-bottom: 18px;
}

.profile-edit .el-form-item__label {
  font-weight: bold;
  color: #606266;
  width: 120px;
}

.face-image-btn {
  position: relative;
  overflow: hidden;
}

/* Default text when not hovering */
.face-image-btn .button-text:not(:hover)::before {
  content: attr(data-normal-text);
}

/* Hover text when hovering */
.face-image-btn:hover .button-text::before {
  content: attr(data-hover-text);
}

.head-pic-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.head-pic-preview {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.head-pic-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  display: block;
}

.head-pic-placeholder {
  padding: 40px 20px;
  text-align: center;
  color: #909399;
  font-size: 14px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>