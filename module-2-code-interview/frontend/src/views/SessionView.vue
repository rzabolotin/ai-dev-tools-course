<template>
  <div class="min-h-screen bg-gray-900">
    <!-- Header -->
    <div class="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-white">Code Interview Session</h1>
          <p class="text-sm text-gray-400 mt-1">
            Session ID: <span class="font-mono text-blue-400">{{ sessionId }}</span>
          </p>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Language Selector -->
          <select
            v-model="selectedLanguage"
            class="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
            @change="handleLanguageChange"
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
            <option value="php">PHP</option>
          </select>

          <!-- Share Button -->
          <button
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            @click="copyShareLink"
          >
            {{ copied ? 'Copied!' : 'Share Link' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4" style="height: calc(100vh - 100px)">
      <!-- Code Editor -->
      <div class="lg:col-span-2 bg-gray-800 rounded-lg overflow-hidden">
        <CodeEditor
          v-if="!loading"
          v-model="code"
          :language="selectedLanguage"
          @update:model-value="handleCodeChange"
        />
        <div v-else class="flex items-center justify-center h-full">
          <div class="text-white">Loading session...</div>
        </div>
      </div>

      <!-- Output Panel -->
      <div class="bg-gray-800 rounded-lg flex flex-col">
        <!-- Execution Controls -->
        <div class="p-4 border-b border-gray-700">
          <button
            :disabled="executing"
            class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            @click="runCode"
          >
            {{ executing ? 'Running...' : 'Run Code' }}
          </button>
        </div>

        <!-- Output Display -->
        <div class="flex-1 overflow-auto p-4">
          <div class="text-sm">
            <div class="text-gray-400 mb-2 font-semibold">Output:</div>
            <pre v-if="output" class="text-green-400 font-mono whitespace-pre-wrap">{{
              output
            }}</pre>
            <pre v-if="error" class="text-red-400 font-mono whitespace-pre-wrap">{{ error }}</pre>
            <div v-if="!output && !error" class="text-gray-500 italic">
              No output yet. Run your code to see results.
            </div>
          </div>
        </div>

        <!-- Connection Status -->
        <div class="p-4 border-t border-gray-700">
          <div class="flex items-center space-x-2">
            <div :class="['w-2 h-2 rounded-full', connected ? 'bg-green-500' : 'bg-red-500']" />
            <span class="text-sm text-gray-400">
              {{ connected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { api } from '@/api';
import { useWebSocket } from '@/composables/useWebSocket';
import { executeCode } from '@/composables/useCodeExecution';
import CodeEditor from '@/components/CodeEditor.vue';

const route = useRoute();
const ws = useWebSocket();

const sessionId = ref(route.params.id as string);
const code = ref('');
const selectedLanguage = ref('javascript');
const output = ref('');
const error = ref('');
const loading = ref(true);
const executing = ref(false);
const connected = ref(false);
const copied = ref(false);
const clientId = ref<string | null>(null);

let wsConnection: WebSocket | null = null;
let updateTimeout: ReturnType<typeof setTimeout> | null = null;

onMounted(async () => {
  try {
    // Load session data
    const session: any = await api.getSession(sessionId.value);
    code.value = session.code || '';
    selectedLanguage.value = session.language || 'javascript';

    // Connect to WebSocket
    wsConnection = ws.joinSession(sessionId.value, {
      onConnected: (data: any) => {
        clientId.value = data.clientId;
        connected.value = true;
      },
      onCodeUpdated: (data: any) => {
        code.value = data.code;
      },
      onLanguageChanged: (data: any) => {
        selectedLanguage.value = data.language;
      },
    });

    loading.value = false;
  } catch (err: any) {
    console.error('Failed to load session:', err);
    error.value = 'Failed to load session. Please check the session ID.';
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  if (wsConnection) {
    ws.leaveSession(sessionId.value);
  }
});

const handleCodeChange = (newCode: string) => {
  // Debounce code updates to avoid too many API calls
  if (updateTimeout) {
    clearTimeout(updateTimeout);
  }

  updateTimeout = setTimeout(async () => {
    try {
      await api.updateCode(sessionId.value, newCode, clientId.value || undefined);
    } catch (err) {
      console.error('Failed to update code:', err);
    }
  }, 500);
};

const handleLanguageChange = async () => {
  try {
    await api.updateLanguage(sessionId.value, selectedLanguage.value, clientId.value || undefined);
  } catch (err) {
    console.error('Failed to update language:', err);
  }
};

const runCode = async () => {
  executing.value = true;
  output.value = '';
  error.value = '';

  try {
    const result = await executeCode(code.value, selectedLanguage.value);
    output.value = result.output;
    error.value = result.error || '';
  } catch (err: any) {
    error.value = err.message || 'Failed to execute code';
  } finally {
    executing.value = false;
  }
};

const copyShareLink = () => {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
};
</script>
