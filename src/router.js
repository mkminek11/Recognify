import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/',        name: 'HomePage', component: () => import('./pages/Home.vue') },
  { path: '/set/:id', name: 'SetPage',  component: () => import('./pages/Set.vue') }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;