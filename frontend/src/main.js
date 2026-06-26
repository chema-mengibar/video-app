import { createApp } from 'vue';
import App from './App.vue';
import './styles.scss'
import { createServiceRegistry, SERVICES_KEY } from './services/ServiceRegistry';

const app = createApp(App);
const services = createServiceRegistry();
app.provide(SERVICES_KEY, services);
app.mount('#app');