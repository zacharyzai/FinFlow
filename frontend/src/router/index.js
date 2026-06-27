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
    component: () => import('@/views/ComingSoonView.vue'),
    meta: { requiresAuth: true },
    props: {
      headerTitle: 'Budget',
      heading: 'Budget Planner',
      description: 'Coming in Phase 1 — daily budget calculator and calendar view.',
      iconPath: 'M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    },
  },
  {
    path: '/health',
    name: 'Health',
    component: () => import('@/views/ComingSoonView.vue'),
    meta: { requiresAuth: true },
    props: {
      headerTitle: 'Health Score',
      heading: 'Financial Health Score',
      description: 'Coming in Phase 2 — 0–100 score across savings, consistency, and adherence.',
      iconPath: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
    },
  },
  {
    path: '/goals',
    name: 'Goals',
    component: () => import('@/views/ComingSoonView.vue'),
    meta: { requiresAuth: true },
    props: {
      headerTitle: 'Goals',
      heading: 'Savings Goals',
      description: 'Coming in Phase 1 — set targets, deadlines, and track progress.',
      iconPath: 'M3 3v1.5M3 21v-6m0 0l2.77-.693a9 9 0 016.208.682l.108.054a9 9 0 006.086.71l3.114-.732a48.524 48.524 0 01-.005-10.499l-3.11.732a9 9 0 01-6.085-.711l-.108-.054a9 9 0 00-6.208-.682L3 4.5M3 15V4.5',
    },
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
