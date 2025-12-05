<template>
  <div ref="editorContainer" class="codemirror-wrapper"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState, Compartment } from '@codemirror/state'
import { javascript } from '@codemirror/lang-javascript'
import { python } from '@codemirror/lang-python'
import { java } from '@codemirror/lang-java'
import { cpp } from '@codemirror/lang-cpp'
import { rust } from '@codemirror/lang-rust'
import { php } from '@codemirror/lang-php'
import { oneDark } from '@codemirror/theme-one-dark'

const props = defineProps<{
  modelValue: string
  language: string
  readOnly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const editorContainer = ref<HTMLElement | null>(null)
let editorView: EditorView | null = null
let languageConf = new Compartment()
let isUpdatingFromProp = false

// Language support mapping
const getLanguageExtension = (lang: string) => {
  switch (lang) {
    case 'javascript':
    case 'typescript':
      return javascript({ typescript: lang === 'typescript' })
    case 'python':
      return python()
    case 'java':
      return java()
    case 'cpp':
      return cpp()
    case 'rust':
      return rust()
    case 'php':
      return php()
    default:
      return javascript()
  }
}

onMounted(() => {
  if (!editorContainer.value) return

  const startState = EditorState.create({
    doc: props.modelValue,
    extensions: [
      basicSetup,
      oneDark,
      languageConf.of(getLanguageExtension(props.language)),
      EditorView.updateListener.of((update) => {
        if (update.docChanged && !isUpdatingFromProp) {
          const newValue = update.state.doc.toString()
          emit('update:modelValue', newValue)
        }
      }),
      EditorView.editable.of(!props.readOnly),
      EditorView.theme({
        '&': {
          height: '100%',
          fontSize: '14px',
        },
        '.cm-scroller': {
          fontFamily: "'Fira Code', 'Courier New', monospace",
        },
        '.cm-content': {
          minHeight: '100%',
        },
      }),
    ],
  })

  editorView = new EditorView({
    state: startState,
    parent: editorContainer.value,
  })
})

// Watch for external value changes (from WebSocket)
watch(() => props.modelValue, (newValue) => {
  if (editorView && editorView.state.doc.toString() !== newValue) {
    isUpdatingFromProp = true
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: newValue,
      },
    })
    isUpdatingFromProp = false
  }
})

// Watch for language changes
watch(() => props.language, (newLang) => {
  if (editorView) {
    editorView.dispatch({
      effects: languageConf.reconfigure(getLanguageExtension(newLang)),
    })
  }
})

onBeforeUnmount(() => {
  if (editorView) {
    editorView.destroy()
    editorView = null
  }
})
</script>

<style scoped>
.codemirror-wrapper {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.codemirror-wrapper :deep(.cm-editor) {
  height: 100%;
}
</style>
