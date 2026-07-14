import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/LandingView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/TransactionsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/UploadView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/budget',
    name: 'Budget',
    component: () => import('@/views/BudgetView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/health',
    name: 'Health',
    component: () => import('@/views/HealthView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/goals',
    name: 'Goals',
    component: () => import('@/views/GoalsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/verify-otp',
    name: 'VerifyOtp',
    component: () => import('@/views/VerifyOtpView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPasswordView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  if (to.meta.requiresAuth && !auth.user) return { name: 'Login' }
  if (to.meta.requiresGuest && auth.user) return { name: 'Dashboard' }
})

export default router
