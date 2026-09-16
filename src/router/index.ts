import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'translate',
    component: () => import('@/pages/PageTranslate.vue'),
  },
  {
    path: '/batch',
    name: 'batch',
    component: () => import('@/pages/PageBatch.vue'),
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/pages/PageHistory.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/pages/PageSettings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
