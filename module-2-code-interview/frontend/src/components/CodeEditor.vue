<template>
  <textarea
    :value="modelValue"
    @input="handleInput"
    :readonly="readOnly"
    class="code-editor"
    spellcheck="false"
  ></textarea>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  language: string
  readOnly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.code-editor {
  width: 100%;
  height: 100%;
  padding: 16px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border: none;
  outline: none;
  resize: none;
  tab-size: 2;
}

.code-editor::placeholder {
  color: #666;
}
</style>
