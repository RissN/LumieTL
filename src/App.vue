<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import Toast from '@/components/Toast.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="app-main">
      <RouterView />
    </main>
    <Toast />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-base);
}

.app-main {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  max-height: 100vh;
}

@media (max-width: 768px) {
  .app-main {
    padding: 20px 16px;
  }
}
</style>
