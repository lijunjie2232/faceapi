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
    redirect: '/user', // 重定向到user页面作为默认页面
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

// 全局前守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 检查用户是否已登录
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.warning('Please log in first.');
      // 如果未登录，重定向到登录页面
      next('/login');
    } else {
      // 如果需要管理员权限
      if (to.meta.requiresAdmin) {
        // 获取用户信息，检查是否为管理员
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        if (userInfo.is_admin) {
          ElMessage.success(`Welcome back, ${userInfo.username}`);
          // 用户是管理员，允许访问
          next();
        } else {
          // 用户不是管理员，显示错误消息并重定向到用户页面
          ElMessage.error('Access denied: Administrator privileges required');
          next('/user');
        }
      } else {
        // 不需要管理员权限的认证路由，继续导航
        next();
      }
    }
  } else {
    // 不需要认证的路由，继续导航
    next();
  }
});

export default router;