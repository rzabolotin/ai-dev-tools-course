<template>
  <div
    class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center p-4"
  >
    <div class="max-w-2xl w-full">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-white mb-4">Code Interview Platform</h1>
        <p class="text-xl text-gray-300">Real-time collaborative coding interviews</p>
      </div>

      <!-- Main Card -->
      <div class="bg-white rounded-2xl shadow-2xl p-8">
        <div class="space-y-6">
          <!-- Create Session Section -->
          <div>
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Start a New Interview</h2>
            <p class="text-gray-600 mb-6">
              Create a new coding session and share the link with your candidate
            </p>

            <!-- Language Selection -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2"> Select Language </label>
              <select
                v-model="selectedLanguage"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            </div>

            <!-- Initial Code (Optional) -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Initial Code (Optional)
              </label>
              <textarea
                v-model="initialCode"
                rows="6"
                placeholder="// Write your starter code here..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
            </div>

            <!-- Create Button -->
            <button
              :disabled="creating"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-lg transition-colors text-lg"
              @click="createNewSession"
            >
              {{ creating ? 'Creating...' : 'Create Interview Session' }}
            </button>
          </div>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-500">or</span>
            </div>
          </div>

          <!-- Join Session Section -->
          <div>
            <h2 class="text-xl font-bold text-gray-800 mb-4">Join an Existing Session</h2>
            <div class="flex space-x-3">
              <input
                v-model="joinSessionId"
                type="text"
                placeholder="Enter session ID"
                class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @keyup.enter="joinSession"
              />
              <button
                :disabled="!joinSessionId"
                class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold px-6 rounded-lg transition-colors"
                @click="joinSession"
              >
                Join
              </button>
            </div>
          </div>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
          >
            {{ errorMessage }}
          </div>
        </div>
      </div>

      <!-- Features -->
      <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        <div class="text-white">
          <div class="text-3xl mb-2">⚡</div>
          <div class="font-semibold mb-1">Real-time Sync</div>
          <div class="text-sm text-gray-400">See changes instantly</div>
        </div>
        <div class="text-white">
          <div class="text-3xl mb-2">🎨</div>
          <div class="font-semibold mb-1">Syntax Highlighting</div>
          <div class="text-sm text-gray-400">8+ languages supported</div>
        </div>
        <div class="text-white">
          <div class="text-3xl mb-2">▶️</div>
          <div class="font-semibold mb-1">Run Code</div>
          <div class="text-sm text-gray-400">Execute in browser</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '@/api';

const router = useRouter();

const selectedLanguage = ref('javascript');
const initialCode = ref('');
const joinSessionId = ref('');
const creating = ref(false);
const errorMessage = ref('');

const createNewSession = async () => {
  creating.value = true;
  errorMessage.value = '';

  try {
    const session: any = await api.createSession(selectedLanguage.value, initialCode.value);

    // Navigate to the new session
    router.push(`/session/${session.session_id}`);
  } catch (error: any) {
    console.error('Failed to create session:', error);
    errorMessage.value = 'Failed to create session. Please try again.';
  } finally {
    creating.value = false;
  }
};

const joinSession = () => {
  if (joinSessionId.value.trim()) {
    router.push(`/session/${joinSessionId.value.trim()}`);
  }
};
</script>
