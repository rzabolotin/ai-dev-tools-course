<template>
  <div ref="editorContainer" class="h-full w-full"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps<{
  modelValue: string
  language: string
  readOnly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const editorContainer = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null
let isUpdatingFromExternal = false

onMounted(() => {
  if (editorContainer.value) {
    // Initialize Monaco Editor
    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue,
      language: getMonacoLanguage(props.language),
      theme: 'vs-dark',
      automaticLayout: true,
      fontSize: 14,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      readOnly: props.readOnly || false,
    })

    // Listen for content changes
    editor.onDidChangeModelContent(() => {
      if (!isUpdatingFromExternal && editor) {
        emit('update:modelValue', editor.getValue())
      }
    })
  }
})

// Watch for external changes to the model value
watch(
  () => props.modelValue,
  (newValue) => {
    if (editor && editor.getValue() !== newValue) {
      isUpdatingFromExternal = true
      const position = editor.getPosition()
      editor.setValue(newValue)
      if (position) {
        editor.setPosition(position)
      }
      isUpdatingFromExternal = false
    }
  }
)

// Watch for language changes
watch(
  () => props.language,
  (newLanguage) => {
    if (editor) {
      const model = editor.getModel()
      if (model) {
        monaco.editor.setModelLanguage(model, getMonacoLanguage(newLanguage))
      }
    }
  }
)

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
})

// Map our language names to Monaco language IDs
const getMonacoLanguage = (lang: string): string => {
  const languageMap: Record<string, string> = {
    javascript: 'javascript',
    typescript: 'typescript',
    python: 'python',
    java: 'java',
    cpp: 'cpp',
    go: 'go',
    rust: 'rust',
    php: 'php',
  }
  return languageMap[lang] || 'javascript'
}
</script>
