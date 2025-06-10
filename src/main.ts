import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { pinia } from '@/stores'
import App from './App.vue'
import Editor from '@/views/Editor.vue'

// Global styles
import '@/assets/styles/global.css'

// Router configuration
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Editor',
      component: Editor
    },
    {
      path: '/presentation/:id',
      name: 'Presentation',
      component: Editor,
      props: true
    }
  ]
})

// Create and mount app
const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#app')

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err, info)
}

// Performance monitoring
if (import.meta.env.DEV) {
  console.log('🎯 AI-PPT System initialized in development mode')
  console.log('📊 Performance monitoring enabled')
}