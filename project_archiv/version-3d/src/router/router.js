import * as vueRouter from 'vue-router';

const routes = [
    {
        path: '/',
        name: 'Rink',
        component: () => ( import('../views/Rink.vue')),
    },
    {
        path: '/editor',
        name: 'Editor',
        component: () => ( import('../views/Editor.vue')),
    }
];

const baseUrl = '' 

const router = vueRouter.createRouter({
    history: vueRouter.createWebHistory(baseUrl),
    routes
});



export default router;