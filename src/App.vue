<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import Toast from '@/components/Toast.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="app-main">
      <div class="app-content-container">
        <RouterView />
      </div>
    </main>
    <Toast />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-canvas);
  position: relative;
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  max-height: 100vh;
  position: relative;
  z-index: 1;
  padding: 32px 40px;
}

.app-content-container {
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 1024px) {
  .app-main {
    padding: 24px 28px;
  }
}

@media (max-width: 768px) {
  .app-main {
    padding: 20px 16px;
  }
}
</style>
