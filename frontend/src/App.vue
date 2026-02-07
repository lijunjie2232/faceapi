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
            <el-button v-if="userInfo && userInfo.is_admin" class="admin-link-btn" type="text" @click="goToAdmin">
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

    <!-- ルート出口、ログインおよび登録ページの表示用 -->
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

// 子コンポーネントにuserInfoを提供
provide('userInfo', userInfo);

// APIからユーザー情報を取得
const fetchUserInfo = async () => {
  try {
    loading.value = true;

    // ローカルストレージからトークンを取得
    const token = localStorage.getItem('token');

    // 認証ヘッダー付きでAPIリクエストを行う
    const response = await axios.get(`${API_BASE_URL}/api/v1/user/me`, {
      headers: {
        'Authorization': `Bearer ${token}`  // Bearerトークン形式を使用
      }
    });

    if (response.data.code === 200) {
      userInfo.value = response.data.data;
      localStorage.setItem('username', userInfo.value.username);
      localStorage.setItem('userInfo', JSON.stringify(response.data.data)); // 完全なユーザー情報を保存
      username.value = userInfo.value.username;
    } else if (response.data.detail === "Not authenticated") {
      // トークンが無効、再度ログインが必要
      // console.error('トークンが無効です、ログインページにリダイレクトします');
      // ローカルストレージをクリア
      localStorage.removeItem('token'); // トークンも削除
      localStorage.removeItem('username'); // ユーザー名も削除
      localStorage.removeItem('userInfo'); // ユーザー情報も削除
    } else {
      // console.error('ユーザー情報の取得に失敗しました:', response.data.message);
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail === "Not authenticated") {
      // トークンが無効、再度ログインが必要
      // console.error('トークンが無効です、ログインページにリダイレクトします');
      // ローカルストレージをクリア
      localStorage.removeItem('token'); // トークンも削除
      localStorage.removeItem('uesrname'); // ユーザー名も削除
    } else {
      // console.error('ユーザー情報の取得中にエラーが発生しました:', error);
    }
  } finally {
    loading.value = false;
  }
};

const checkLoginStatus = async () => {
  try {
    // userInfoの代わりにlocalStorageからユーザートークンを確認
    const token = localStorage.getItem('token');
    if (token) {
      await fetchUserInfo();
      // トークンが存在することを確認し、必要に応じてそこからユーザー名を抽出
      // 実際の実装では、JWTをデコードしてユーザー情報を取得する場合があります
      // 今のところ、ユーザー名を別途保存するかAPIから取得します
      showMainApp.value = true;
      // console.log('ユーザーは認証されています');

      // 現在ログイン/サインアップページにいるが認証されている場合、ルートに基づいてリダイレクト
      if (route.path === '/login' || route.path === '/signup') {
        // ログインページから来た場合は、デフォルトページ（ユーザー）に移動
        router.push('/user');
      }
    } else {
      showMainApp.value = false;
      // ログインしていないかつログイン/サインアップページにいない場合は、ログインにリダイレクト
      if (route.path !== '/login' && route.path !== '/signup' && route.path !== '/') {
        router.push('/login');
      }
    }
  } catch (error) {
    // console.error('ログイン状態の確認に失敗しました:', error);
    showMainApp.value = false;
    router.push('/login');
  }
};

// 子コンポーネントにcheckLoginStatus関数を提供
provide('checkLoginStatus', checkLoginStatus);

const logout = async () => {
  try {
    // ローカルストレージからトークンとユーザー情報をクリア
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('userInfo'); // ユーザー情報も削除
    username.value = '';
    userInfo.value = {};
    showMainApp.value = false;
    await router.push('/login');
    ElMessage.success('正常にログアウトしました');
  } catch (error) {
    // console.error('ログアウトに失敗しました:', error);
    ElMessage.error('ログアウトに失敗しました');
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

// ルート変更を監視
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

/* 他のページ用の汎用スタイルを保持 */
.admin-panel {
  min-height: calc(100vh - 80px - 65px);
}
</style>