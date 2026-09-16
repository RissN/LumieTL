<script setup lang="ts">
defineProps<{
  modelValue: string
  options: Record<string, string>
  label?: string
  id?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="lang-selector">
    <label v-if="label" :for="id" class="selector-label">{{ label }}</label>
    <div class="select-wrapper">
      <select
        :id="id"
        :value="modelValue"
        class="selector-select"
        @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option
          v-for="(name, code) in options"
          :key="code"
          :value="code"
        >
          {{ name }}
        </option>
      </select>
      <span class="select-arrow">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="6,9 12,15 18,9" />
        </svg>
      </span>
    </div>
  </div>
</template>

<style scoped>
.lang-selector {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.selector-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.select-wrapper {
  position: relative;
  display: inline-flex;
}

.selector-select {
  appearance: none;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 32px 8px 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s ease;
  min-width: 160px;
}

.selector-select:hover {
  border-color: var(--accent);
}

.selector-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent) 20%, transparent);
}

.selector-select option {
  background: var(--bg-surface);
  color: var(--text-primary);
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
}
</style>
