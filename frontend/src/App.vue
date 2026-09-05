<template>
  <div class="flex h-screen w-screen overflow-hidden bg-[#0F0F11] text-[#E8E8ED]">
    <!-- Sidebar -->
    <aside class="w-56 bg-[#18181C] border-r border-[#2A2A30] flex flex-col p-4 shrink-0">
      <!-- App Brand -->
      <div class="flex items-center gap-2.5 px-2 py-3 mb-4">
        <div class="w-8 h-8 rounded-lg bg-[#6C8EF5]/15 border border-[#6C8EF5]/30 flex items-center justify-center text-[#6C8EF5]">
          <Languages class="w-4 h-4" />
        </div>
        <span class="font-bold text-lg tracking-wide text-[#E8E8ED]">LumieTL</span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1">
        <router-link
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <Image class="w-4 h-4" />
          <span>Terjemahkan</span>
        </router-link>

        <router-link
          to="/batch"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/batch' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <Layers class="w-4 h-4" />
          <span>Batch</span>
        </router-link>

        <router-link
          to="/history"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/history' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <History class="w-4 h-4" />
          <span>Riwayat</span>
        </router-link>

        <router-link
          to="/settings"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/settings' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <Settings class="w-4 h-4" />
          <span>Pengaturan</span>
        </router-link>
      </nav>

      <!-- Version -->
      <div class="pt-4 border-t border-[#2A2A30] text-[11px] text-[#8A8A96] px-2 flex items-center justify-between">
        <span>LumieTL Web</span>
        <span class="text-[10px] bg-[#222228] px-1.5 py-0.5 rounded border border-[#2A2A30]">v1.0</span>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto p-6 bg-[#0F0F11]">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { Languages, Image, Layers, History, Settings } from 'lucide-vue-next'
</script>
