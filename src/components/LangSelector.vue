<script setup lang="ts">
defineProps<{
  modelValue: string
  options: Record<string, string>
  label?: string
  id?: string
  hint?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="lang-selector-group">
    <div v-if="label" class="label-row">
      <label :for="id" class="selector-label">{{ label }}</label>
      <span v-if="hint" class="selector-hint">{{ hint }}</span>
    </div>
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
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </span>
    </div>
  </div>
</template>

<style scoped>
.lang-selector-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 170px;
}

.label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.selector-label {
  font-family: var(--font-heading);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.selector-hint {
  font-size: 11px;
  color: var(--text-muted);
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.selector-select {
  width: 100%;
  appearance: none;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 36px 10px 14px;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.selector-select:hover {
  background: var(--bg-surface-hover);
  border-color: var(--border-hover);
}

.selector-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.selector-select option {
  background: #181926;
  color: #F3F4F6;
  padding: 8px 12px;
}

.select-arrow {
  position: absolute;
  right: 12px;
  color: var(--text-muted);
  pointer-events: none;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
}

.selector-select:hover + .select-arrow,
.selector-select:focus + .select-arrow {
  color: var(--accent);
}
</style>
