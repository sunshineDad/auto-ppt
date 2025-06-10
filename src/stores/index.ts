import { createPinia } from 'pinia'

export const pinia = createPinia()

export { usePresentationStore } from './presentation'
export { useAIStore } from './ai'