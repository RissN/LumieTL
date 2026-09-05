<template>
  <div class="space-y-6 max-w-2xl">
    <!-- Header -->
    <div>
      <h1 class="text-xl font-bold text-[#E8E8ED]">Pengaturan</h1>
      <p class="text-sm text-[#8A8A96]">Konfigurasi server dan kredensial API penerjemah</p>
    </div>

    <!-- Section 1: Default Langs -->
    <div class="bg-[#18181C] border border-[#2A2A30] rounded-xl p-5 space-y-4">
      <h2 class="text-sm font-semibold text-[#6C8EF5]">Bahasa & Engine Default</h2>
      
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-[#8A8A96] mb-1">Bahasa Sumber:</label>
          <select
            v-model="form.default_source_lang"
            class="w-full bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded p-2 focus:border-[#6C8EF5] outline-none"
          >
            <option value="auto">Auto-detect</option>
            <option value="JPN">Jepang</option>
            <option value="KOR">Korea</option>
            <option value="CHS">Mandarin (Simplified)</option>
            <option value="CHT">Mandarin (Traditional)</option>
          </select>
        </div>

        <div>
          <label class="block text-xs text-[#8A8A96] mb-1">Bahasa Target:</label>
          <select
            v-model="form.default_target_lang"
            class="w-full bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded p-2 focus:border-[#6C8EF5] outline-none"
          >
            <option value="ID">Indonesia</option>
            <option value="EN">Inggris</option>
            <option value="VI">Vietnam</option>
            <option value="TH">Thailand</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-xs text-[#8A8A96] mb-1">Engine Default:</label>
        <select
          v-model="form.default_engine"
          class="w-full bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded p-2 focus:border-[#6C8EF5] outline-none"
        >
          <option value="google">Google Translate</option>
          <option value="deepl">DeepL</option>
          <option value="openai">OpenAI GPT-4o</option>
        </select>
      </div>
    </div>

    <!-- Section 2: API Keys -->
    <div class="bg-[#18181C] border border-[#2A2A30] rounded-xl p-5 space-y-4">
      <h2 class="text-sm font-semibold text-[#6C8EF5]">Kredensial API (Disimpan Terenkripsi)</h2>

      <div>
        <div class="flex items-center justify-between mb-1">
          <label class="text-xs text-[#8A8A96]">DeepL API Key:</label>
          <span class="text-[11px]" :class="settingsStore.apiKeys.deepl_set ? 'text-[#4CAF82]' : 'text-[#8A8A96]'">
            {{ settingsStore.apiKeys.deepl_set ? '● Sudah Terpasang' : '○ Belum Diatur' }}
          </span>
        </div>
        <div class="flex gap-2">
          <input
            v-model="deeplKey"
            type="password"
            placeholder="Masukkan kunci DeepL baru"
            class="flex-1 bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded p-2 focus:border-[#6C8EF5] outline-none"
          />
          <button
            @click="saveKey('deepl', deeplKey)"
            class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30]"
          >
            Simpan
          </button>
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between mb-1">
          <label class="text-xs text-[#8A8A96]">OpenAI API Key:</label>
          <span class="text-[11px]" :class="settingsStore.apiKeys.openai_set ? 'text-[#4CAF82]' : 'text-[#8A8A96]'">
            {{ settingsStore.apiKeys.openai_set ? '● Sudah Terpasang' : '○ Belum Diatur' }}
          </span>
        </div>
        <div class="flex gap-2">
          <input
            v-model="openaiKey"
            type="password"
            placeholder="sk-proj-..."
            class="flex-1 bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded p-2 focus:border-[#6C8EF5] outline-none"
          />
          <button
            @click="saveKey('openai', openaiKey)"
            class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30]"
          >
            Simpan
          </button>
        </div>
      </div>
    </div>

    <!-- Section 3: Save Button -->
    <div class="flex justify-end">
      <button
        @click="saveAllSettings"
        class="bg-[#6C8EF5] hover:bg-[#7D9CF8] text-white text-xs font-semibold px-5 py-2.5 rounded-md transition-colors"
      >
        Simpan Pengaturan
      </button>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import Toast from '@/components/Toast.vue'

const settingsStore = useSettingsStore()
const form = ref({ ...settingsStore.settings })
const deeplKey = ref('')
const openaiKey = ref('')
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

async function saveKey(provider: 'deepl' | 'openai', key: string) {
  if (!key.trim()) return
  try {
    await settingsStore.saveApiKey(provider, key)
    if (provider === 'deepl') deeplKey.value = ''
    if (provider === 'openai') openaiKey.value = ''
    toastRef.value?.show(`API Key ${provider} berhasil disimpan!`)
  } catch (e) {
    toastRef.value?.show('Gagal menyimpan API Key', 'error')
  }
}

async function saveAllSettings() {
  try {
    await settingsStore.saveSettings(form.value)
    toastRef.value?.show('Pengaturan berhasil diperbarui!')
  } catch (e) {
    toastRef.value?.show('Gagal menyimpan pengaturan', 'error')
  }
}

onMounted(async () => {
  await settingsStore.fetchSettings()
  form.value = { ...settingsStore.settings }
})
</script>
