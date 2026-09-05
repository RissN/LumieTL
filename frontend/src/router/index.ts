import { createRouter, createWebHistory } from 'vue-router'
import PageTranslate from '@/pages/PageTranslate.vue'
import PageBatch from '@/pages/PageBatch.vue'
import PageHistory from '@/pages/PageHistory.vue'
import PageSettings from '@/pages/PageSettings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'translate', component: PageTranslate },
    { path: '/batch', name: 'batch', component: PageBatch },
    { path: '/history', name: 'history', component: PageHistory },
    { path: '/settings', name: 'settings', component: PageSettings }
  ]
})

export default router
