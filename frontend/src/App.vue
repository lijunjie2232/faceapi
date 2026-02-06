<template>
  <div id="app">
    <el-container v-if="showMainApp">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon>
              <User />
            </el-icon>
            <span>Face Recognition System</span>
          </h1>
          <div class="user-actions">
            <el-button 
              v-if="userInfo && userInfo.is_admin" 
              class="admin-link-btn" 
              type="text" 
              @click="goToAdmin"
            >
              <el-icon>
                <Management />
              </el-icon>
              <span>Admin</span>
            </el-button>
            <el-dropdown placement="bottom-end">
              <el-button class="user-profile-btn" type="text">
                <span class="user-name">{{ username }}</span>
                <el-icon>
                  <ArrowDown />
                </el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goToProfile">Profile</el-dropdown-item>
                  <el-dropdown-item @click="logout">Logout</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>

      <el-footer class="app-footer">
        <p class="footer-text">Face Recognition System &copy; {{ currentYear }} | Advanced Facial Recognition Technology
        </p>
      </el-footer>
    </el-container>

    <!-- 路由出口，用于显示登录和注册页面 -->
    <router-view v-if="!showMainApp" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, ArrowDown, Management } from '@element-plus/icons-vue';
import axios from 'axios';
import { provide } from 'vue';

const showMainApp = ref(false);
const username = ref('');
const currentYear = new Date().getFullYear();
const router = useRouter();
const route = useRoute();
const userInfo = ref({});
const loading = ref(true);
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Provide userInfo to child components
provide('userInfo', userInfo);

// Fetch user info from API
const fetchUserInfo = async () => {
  try {
    loading.value = true;

    // Get token from local storage
    const token = localStorage.getItem('token');

    // Make API request with authorization header
    const response = await axios.get(`${API_BASE_URL}/api/v1/user/me`, {
      headers: {
        'Authorization': `Bearer ${token}`  // Using Bearer token format
      }
    });

    if (response.data.success) {
      userInfo.value = response.data.data;
      localStorage.setItem('username', userInfo.value.username);
      localStorage.setItem('userInfo', JSON.stringify(response.data.data)); // Store full user info
      username.value = userInfo.value.username;
    } else if (response.data.detail === "Not authenticated") {
      // Token is invalid, need to login again
      console.error('Token is invalid, redirecting to login');
      // Clear local storage
      localStorage.removeItem('token'); // Also remove the token
      localStorage.removeItem('username'); // Also remove the username
      localStorage.removeItem('userInfo'); // Remove user info
    } else {
      console.error('Failed to fetch user info:', response.data.message);
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail === "Not authenticated") {
      // Token is invalid, need to login again
      console.error('Token is invalid, redirecting to login');
      // Clear local storage
      localStorage.removeItem('token'); // Also remove the token
      localStorage.removeItem('uesrname'); // Also remove the username
    } else {
      console.error('Error fetching user info:', error);
    }
  } finally {
    loading.value = false;
  }
};

const checkLoginStatus = async () => {
  try {
    // Check for user token in localStorage instead of userInfo
    await fetchUserInfo();
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token exists and extract username from it if needed
      // In a real implementation, you might decode JWT to get user info
      // For now, we'll store username separately or fetch from API
      showMainApp.value = true;
      console.log('User is authenticated');

      // If currently on login/signup page but authenticated, redirect based on route
      if (route.path === '/login' || route.path === '/signup') {
        // If coming from login page, navigate to default page (user)
        router.push('/user');
      }
    } else {
      showMainApp.value = false;
      // If not logged in and not on login/signup page, redirect to login
      if (route.path !== '/login' && route.path !== '/signup' && route.path !== '/') {
        router.push('/login');
      }
    }
  } catch (error) {
    console.error('Checking login status failed:', error);
    showMainApp.value = false;
    router.push('/login');
  }
};

// Provide checkLoginStatus function to child components
provide('checkLoginStatus', checkLoginStatus);

const logout = async () => {
  try {
    // Clear token and user information from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('userInfo'); // Also remove user info
    username.value = '';
    userInfo.value = {};
    showMainApp.value = false;
    await router.push('/login');
    ElMessage.success('Logged out successfully');
  } catch (error) {
    console.error('Logout failed:', error);
    ElMessage.error('Logout failed');
  }
};

const goToProfile = () => {
  router.push('/user');
};

const goToAdmin = () => {
  router.push('/admin');
};

onMounted(() => {
  checkLoginStatus();
});

// Listen for route changes
router.afterEach(() => {
  checkLoginStatus();
});

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #409EFF 0%, #327de8 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 80px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  /* max-width: 1200px; */
  padding: 0 40px;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.app-title .el-icon {
  font-size: 28px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-profile-btn {
  color: white;
  padding: 0 10px;
}

.admin-link-btn {
  color: white;
  padding: 0 10px;
  margin-right: 10px;
}

.admin-link-btn .el-icon {
  margin-right: 5px;
}

.user-name {
  font-weight: 500;
  margin-right: 5px;
}

.app-main {
  flex: 1;
  padding: 20px 0;
  background-color: #f0f2f5;
}

.app-footer {
  background-color: #323a45;
  color: white;
  text-align: center;
  padding: 15px 0;
  margin-top: auto;
}

.footer-text {
  margin: 0;
  font-size: 14px;
  color: #aeb7c2;
}

/* 为其他页面保留通用样式 */
.admin-panel {
  min-height: calc(100vh - 80px - 65px);
}
</style>