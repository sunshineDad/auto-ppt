/**
 * AI Store
 * 
 * Manages AI predictions, learning, and autonomous operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  AtomicOperationData, 
  AtomPrediction, 
  AIContext,
  OperationSequence 
} from '@/types/atoms'
import { usePresentationStore } from './presentation'

export const useAIStore = defineStore('ai', () => {
  // State
  const isLearning = ref(false)
  const predictions = ref<AtomPrediction[]>([])
  const operationSequences = ref<OperationSequence[]>([])
  const aiSuggestions = ref<AtomicOperationData[]>([])
  const learningProgress = ref(0)
  const modelMetrics = ref({
    accuracy: 0,
    totalOperations: 0,
    successfulPredictions: 0,
    averageConfidence: 0
  })

  // Computed
  const topPrediction = computed(() => {
    return predictions.value.length > 0 ? predictions.value[0] : null
  })

  const isAIReady = computed(() => {
    return modelMetrics.value.totalOperations > 100 && modelMetrics.value.accuracy > 0.7
  })

  const suggestionCount = computed(() => {
    return aiSuggestions.value.length
  })

  // Actions
  async function predictNextAtom(context: AIContext): Promise<AtomPrediction | null> {
    try {
      const response = await fetch('/api/ai/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI prediction')
      }

      const prediction: AtomPrediction = await response.json()
      
      // Add to predictions list
      predictions.value.unshift(prediction)
      
      // Keep only recent predictions
      if (predictions.value.length > 10) {
        predictions.value = predictions.value.slice(0, 10)
      }

      return prediction
    } catch (error) {
      console.error('AI prediction error:', error)
      return null
    }
  }

  async function generateSuggestions(slideIndex: number): Promise<AtomicOperationData[]> {
    const presentationStore = usePresentationStore()
    
    const context: AIContext = {
      currentSlide: {
        index: slideIndex,
        elements: presentationStore.currentSlide?.elements || [],
        layout: presentationStore.currentSlide?.layout || 'blank'
      },
      presentation: {
        totalSlides: presentationStore.totalSlides,
        theme: presentationStore.presentation.theme.name,
        purpose: 'general' // This could be inferred or user-specified
      },
      userBehavior: {
        recentOperations: await getRecentOperations(),
        patterns: await getOperationPatterns(),
        preferences: await getUserPreferences()
      }
    }

    try {
      const response = await fetch('/api/ai/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI suggestions')
      }

      const suggestions: AtomicOperationData[] = await response.json()
      aiSuggestions.value = suggestions

      return suggestions
    } catch (error) {
      console.error('AI suggestions error:', error)
      return []
    }
  }

  async function executeAISuggestion(suggestion: AtomicOperationData) {
    const presentationStore = usePresentationStore()
    
    try {
      await presentationStore.executeAtomicOperation(suggestion)
      
      // Remove executed suggestion
      const index = aiSuggestions.value.findIndex(s => 
        s.op === suggestion.op && 
        s.type === suggestion.type && 
        s.timestamp === suggestion.timestamp
      )
      if (index !== -1) {
        aiSuggestions.value.splice(index, 1)
      }

      // Update metrics
      modelMetrics.value.successfulPredictions++
      updateModelMetrics()

    } catch (error) {
      console.error('Failed to execute AI suggestion:', error)
      throw error
    }
  }

  async function learnFromOperation(operation: AtomicOperationData, result: any) {
    try {
      const response = await fetch('/api/ai/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation,
          result,
          timestamp: Date.now()
        })
      })

      if (response.ok) {
        modelMetrics.value.totalOperations++
        updateModelMetrics()
      }
    } catch (error) {
      console.error('AI learning error:', error)
    }
  }

  async function generatePresentation(prompt: string): Promise<OperationSequence> {
    isLearning.value = true
    learningProgress.value = 0

    try {
      const response = await fetch('/api/ai/generate-presentation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      })

      if (!response.ok) {
        throw new Error('Failed to generate presentation')
      }

      const sequence: OperationSequence = await response.json()
      operationSequences.value.push(sequence)

      return sequence
    } catch (error) {
      console.error('Presentation generation error:', error)
      throw error
    } finally {
      isLearning.value = false
      learningProgress.value = 0
    }
  }

  async function executeOperationSequence(sequence: OperationSequence) {
    const presentationStore = usePresentationStore()
    
    for (let i = 0; i < sequence.atoms.length; i++) {
      const operation = sequence.atoms[i]
      
      try {
        await presentationStore.executeAtomicOperation(operation)
        learningProgress.value = ((i + 1) / sequence.atoms.length) * 100
        
        // Small delay for visual feedback
        await new Promise(resolve => setTimeout(resolve, 100))
      } catch (error) {
        console.error(`Failed to execute operation ${i}:`, error)
        break
      }
    }
  }

  async function analyzeUserPatterns(): Promise<string[]> {
    try {
      const response = await fetch('/api/ai/analyze-patterns')
      
      if (!response.ok) {
        throw new Error('Failed to analyze patterns')
      }

      const patterns: string[] = await response.json()
      return patterns
    } catch (error) {
      console.error('Pattern analysis error:', error)
      return []
    }
  }

  async function getOperationSequences(): Promise<OperationSequence[]> {
    try {
      const response = await fetch('/api/ai/sequences')
      
      if (!response.ok) {
        throw new Error('Failed to get operation sequences')
      }

      const sequences: OperationSequence[] = await response.json()
      operationSequences.value = sequences
      
      return sequences
    } catch (error) {
      console.error('Failed to get sequences:', error)
      return []
    }
  }

  function clearSuggestions() {
    aiSuggestions.value = []
  }

  function clearPredictions() {
    predictions.value = []
  }

  // Helper functions
  async function getRecentOperations(): Promise<AtomicOperationData[]> {
    try {
      const response = await fetch('/api/operations/recent')
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get recent operations:', error)
    }
    return []
  }

  async function getOperationPatterns(): Promise<string[]> {
    try {
      const response = await fetch('/api/ai/patterns')
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get operation patterns:', error)
    }
    return []
  }

  async function getUserPreferences(): Promise<Record<string, any>> {
    try {
      const response = await fetch('/api/user/preferences')
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get user preferences:', error)
    }
    return {}
  }

  function updateModelMetrics() {
    if (modelMetrics.value.totalOperations > 0) {
      modelMetrics.value.accuracy = 
        modelMetrics.value.successfulPredictions / modelMetrics.value.totalOperations
    }
  }

  // Auto-suggestion system
  let suggestionTimer: NodeJS.Timeout | null = null

  function startAutoSuggestions() {
    if (suggestionTimer) return

    suggestionTimer = setInterval(async () => {
      const presentationStore = usePresentationStore()
      
      if (isAIReady.value && aiSuggestions.value.length < 3) {
        await generateSuggestions(presentationStore.canvas.activeSlide)
      }
    }, 5000) // Generate suggestions every 5 seconds
  }

  function stopAutoSuggestions() {
    if (suggestionTimer) {
      clearInterval(suggestionTimer)
      suggestionTimer = null
    }
  }

  // Smart templates based on content analysis
  async function suggestTemplate(content: string): Promise<string> {
    try {
      const response = await fetch('/api/ai/suggest-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      })

      if (response.ok) {
        const { template } = await response.json()
        return template
      }
    } catch (error) {
      console.error('Template suggestion error:', error)
    }
    return 'blank'
  }

  // Content enhancement suggestions
  async function enhanceContent(elementId: string, content: string): Promise<string> {
    try {
      const response = await fetch('/api/ai/enhance-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ elementId, content })
      })

      if (response.ok) {
        const { enhancedContent } = await response.json()
        return enhancedContent
      }
    } catch (error) {
      console.error('Content enhancement error:', error)
    }
    return content
  }

  return {
    // State
    isLearning,
    predictions,
    operationSequences,
    aiSuggestions,
    learningProgress,
    modelMetrics,
    
    // Computed
    topPrediction,
    isAIReady,
    suggestionCount,
    
    // Actions
    predictNextAtom,
    generateSuggestions,
    executeAISuggestion,
    learnFromOperation,
    generatePresentation,
    executeOperationSequence,
    analyzeUserPatterns,
    getOperationSequences,
    clearSuggestions,
    clearPredictions,
    startAutoSuggestions,
    stopAutoSuggestions,
    suggestTemplate,
    enhanceContent
  }
})