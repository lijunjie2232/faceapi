import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Login from '../views/Login.vue'
import Signup from '../views/Signup.vue'
import Admin from '../views/Admin.vue'
import User from '../views/User.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/user', // userページにリダイレクトしてデフォルトページとする
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user',
    name: 'User',
    component: User,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// グローバル前置ガード
router.beforeEach((to, from, next) => {
  // ルートが認証を必要とするかどうかをチェック
  if (to.meta.requiresAuth) {
    // ユーザーがログインしているかどうかをチェック
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.warning('まずログインしてください。');
      // ログインしていない場合はログインページにリダイレクト
      next('/login');
    } else {
      // 管理者権限が必要な場合
      if (to.meta.requiresAdmin) {
        // ユーザー情報を取得し、管理者かどうかをチェック
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        if (userInfo.is_admin) {
          ElMessage.success(`おかえりなさい、${userInfo.username}`);
          // ユーザーが管理者の場合、アクセスを許可
          next();
        } else {
          // ユーザーが管理者でない場合、エラーメッセージを表示してユーザーページにリダイレクト
          ElMessage.error('アクセス拒否：管理者権限が必要です');
          next('/user');
        }
      } else {
        // 管理者権限を必要としない認証ルート、ナビゲーションを続行
        next();
      }
    }
  } else {
    // 認証を必要としないルート、ナビゲーションを続行
    next();
  }
});

export default router;