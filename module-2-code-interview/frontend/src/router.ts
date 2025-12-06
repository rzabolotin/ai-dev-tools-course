import { createRouter, createWebHistory } from 'vue-router';
import HomeView from './views/HomeView.vue';
import SessionView from './views/SessionView.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/session/:id', component: SessionView },
  ],
});
