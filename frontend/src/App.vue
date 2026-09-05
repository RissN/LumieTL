<template>
  <div class="flex h-screen w-screen overflow-hidden bg-[#0F0F11] text-[#E8E8ED]">
    <!-- Sidebar -->
    <aside class="w-56 bg-[#18181C] border-r border-[#2A2A30] flex flex-col p-4 shrink-0">
      <!-- App Brand -->
      <div class="flex items-center gap-2.5 px-2 py-3 mb-4">
        <span class="text-xl">✨</span>
        <span class="font-bold text-lg tracking-wide text-[#E8E8ED]">LumieTL</span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1">
        <router-link
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <span class="text-base">🖼</span>
          <span>Terjemahkan</span>
        </router-link>

        <router-link
          to="/batch"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/batch' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <span class="text-base">⚡</span>
          <span>Batch</span>
        </router-link>

        <router-link
          to="/history"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/history' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <span class="text-base">📋</span>
          <span>Riwayat</span>
        </router-link>

        <router-link
          to="/settings"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
          :class="$route.path === '/settings' ? 'bg-[#222228] text-[#6C8EF5] font-semibold' : 'text-[#8A8A96] hover:bg-[#222228] hover:text-[#E8E8ED]'"
        >
          <span class="text-base">⚙</span>
          <span>Pengaturan</span>
        </router-link>
      </nav>

      <!-- Version -->
      <div class="pt-4 border-t border-[#2A2A30] text-[11px] text-[#8A8A96] px-2">
        v1.0.0 (Web)
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto p-6 bg-[#0F0F11]">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
