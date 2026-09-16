<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'

const route = useRoute()
const settingsStore = useSettingsStore()

const navItems = [
  {
    path: '/',
    label: 'Terjemahkan',
    desc: 'Gambar tunggal & slider',
    icon: 'translate',
  },
  {
    path: '/batch',
    label: 'Batch Process',
    desc: 'Banyak file & folder',
    icon: 'batch',
  },
  {
    path: '/history',
    label: 'Riwayat',
    desc: 'Arsip terjemahan',
    icon: 'history',
  },
  {
    path: '/settings',
    label: 'Pengaturan',
    desc: 'API keys & engine',
    icon: 'settings',
  },
]

const currentPath = computed(() => route.path)
</script>

<template>
  <aside class="sidebar">
    <!-- Header / Brand -->
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <div class="brand-badge">
          <!-- Manga Speech Bubble + Sparkle SVG -->
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" class="brand-svg">
            <path
              d="M12 2C6.477 2 2 6.03 2 11c0 2.821 1.45 5.347 3.73 7.02L5 22l4.47-1.49C10.25 20.81 11.11 21 12 21c5.523 0 10-4.03 10-9s-4.477-10-10-10z"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M15 8l.7 1.6L17.3 10.3l-1.6.7L15 12.6l-.7-1.6-1.6-.7 1.6-.7L15 8z"
              fill="currentColor"
            />
            <circle cx="9" cy="11.5" r="1.2" fill="currentColor" />
          </svg>
        </div>
        <div class="brand-info">
          <div class="brand-title">
            <span>Lumie</span><span class="brand-tag">TL</span>
          </div>
          <span class="brand-subtitle">AI Manga Translator</span>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <div class="nav-section-title">MENU UTAMA</div>
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="['nav-item', { active: currentPath === item.path }]"
      >
        <span class="nav-active-bar"></span>
        <div class="nav-icon-wrap">
          <!-- Terjemahkan Icon -->
          <svg v-if="item.icon === 'translate'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>

          <!-- Batch Icon -->
          <svg v-else-if="item.icon === 'batch'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"/>
            <polyline points="2 17 12 22 22 17"/>
            <polyline points="2 12 12 17 22 12"/>
          </svg>

          <!-- Riwayat Icon -->
          <svg v-else-if="item.icon === 'history'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>

          <!-- Settings Icon -->
          <svg v-else-if="item.icon === 'settings'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="21" x2="4" y2="14"/>
            <line x1="4" y1="10" x2="4" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12" y2="3"/>
            <line x1="20" y1="21" x2="20" y2="16"/>
            <line x1="20" y1="12" x2="20" y2="3"/>
            <line x1="1" y1="14" x2="7" y2="14"/>
            <line x1="9" y1="8" x2="15" y2="8"/>
            <line x1="17" y1="16" x2="23" y2="16"/>
          </svg>
        </div>

        <div class="nav-text-col">
          <span class="nav-label">{{ item.label }}</span>
          <span class="nav-desc">{{ item.desc }}</span>
        </div>
      </RouterLink>
    </nav>

    <!-- Footer System Status -->
    <div class="sidebar-footer">
      <div class="status-card">
        <div class="status-row">
          <div class="status-indicator">
            <span class="dot-pulse"></span>
            <span class="status-text">Server Aktif</span>
          </div>
          <span class="status-port">:18420</span>
        </div>
        <div class="hardware-row">
          <span class="hw-label">Akselerasi</span>
          <span class="hw-badge" :class="{ 'cuda-active': settingsStore.settings.gpu_enabled }">
            {{ settingsStore.settings.gpu_enabled ? 'CUDA GPU' : 'CPU Mode' }}
          </span>
        </div>
      </div>
      <div class="version-row">
        <span>LumieTL Web</span>
        <span class="version-num">v1.0.0</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  min-width: 260px;
  height: 100vh;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(20px);
}

.sidebar-header {
  padding: 24px 20px 20px 20px;
  border-bottom: 1px solid var(--border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-badge {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  flex-shrink: 0;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-heading);
  font-size: 19px;
  font-weight: 700;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  gap: 4px;
  letter-spacing: -0.4px;
}

.brand-tag {
  font-size: 12px;
  font-weight: 800;
  padding: 1px 6px;
  background: rgba(99, 102, 241, 0.25);
  color: #A5B4FC;
  border-radius: 6px;
  border: 1px solid rgba(99, 102, 241, 0.4);
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.2px;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.8px;
  padding: 0 12px 6px 12px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.nav-active-bar {
  position: absolute;
  left: 0;
  top: 15%;
  bottom: 15%;
  width: 3px;
  border-radius: 0 4px 4px 0;
  background: var(--accent);
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease;
  transform: scaleY(0.4);
}

.nav-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.nav-text-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.nav-label {
  font-family: var(--font-heading);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
}

.nav-desc {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

.nav-item:hover .nav-icon-wrap {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.nav-item.active .nav-active-bar {
  opacity: 1;
  transform: scaleY(1);
}

.nav-item.active .nav-icon-wrap {
  color: #818CF8;
  background: rgba(99, 102, 241, 0.15);
}

.nav-item.active .nav-label {
  color: #FFFFFF;
}

.nav-item.active .nav-desc {
  color: #A5B4FC;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-card {
  background: rgba(13, 14, 21, 0.6);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
}

.status-text {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-port {
  font-size: 11px;
  font-family: monospace;
  color: var(--text-muted);
}

.hardware-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 6px;
}

.hw-label {
  font-size: 11px;
  color: var(--text-muted);
}

.hw-badge {
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
}

.hw-badge.cuda-active {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.version-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  padding: 0 4px;
}

.version-num {
  font-family: monospace;
  background: rgba(255, 255, 255, 0.05);
  padding: 1px 6px;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .sidebar {
    width: 72px;
    min-width: 72px;
  }
  .brand-info,
  .nav-text-col,
  .nav-section-title,
  .sidebar-footer {
    display: none;
  }
  .sidebar-header {
    padding: 18px 0;
    display: flex;
    justify-content: center;
  }
  .sidebar-nav {
    padding: 16px 8px;
    align-items: center;
  }
  .nav-item {
    justify-content: center;
    padding: 12px;
    width: 48px;
    height: 48px;
  }
}
</style>
