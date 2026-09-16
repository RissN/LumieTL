<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', label: 'Terjemahkan', icon: '🖼' },
  { path: '/batch', label: 'Batch', icon: '⚡' },
  { path: '/history', label: 'Riwayat', icon: '📋' },
  { path: '/settings', label: 'Pengaturan', icon: '⚙' },
]

const currentPath = computed(() => route.path)
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <span class="logo-icon">L</span>
        <span class="logo-text">LumieTL</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="['nav-item', { active: currentPath === item.path }]"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <span class="version-tag">v1.0.0</span>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  min-width: 220px;
  height: 100vh;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--border);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--accent);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  color: #fff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 450;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.nav-item.active {
  background: color-mix(in srgb, var(--accent) 15%, transparent);
  color: var(--accent);
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
}

.version-tag {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.6;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
    min-width: 60px;
  }
  .logo-text,
  .nav-label {
    display: none;
  }
  .sidebar-logo {
    justify-content: center;
  }
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  .nav-icon {
    font-size: 20px;
  }
}
</style>
