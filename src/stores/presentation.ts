/**
 * Presentation Store
 * 
 * Manages the presentation state and atomic operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { AtomicEngine } from '@/utils/atomicEngine'
import type { 
  Presentation, 
  Slide, 
  PPTElement, 
  PresentationTheme,
  CanvasState,
  EditorState 
} from '@/types/slides'
import { 
  AtomicOperation,
  ElementType 
} from '@/types/atoms'
import type { 
  AtomicOperationData
} from '@/types/atoms'

export const usePresentationStore = defineStore('presentation', () => {
  // State
  const presentation = ref<Presentation>(createDefaultPresentation())
  const canvas = ref<CanvasState>(createDefaultCanvasState())
  const history = ref<{ past: any[], present: any, future: any[] }>({
    past: [],
    present: null,
    future: []
  })
  const clipboard = ref<PPTElement[]>([])
  const isPlaying = ref(false)
  const isFullscreen = ref(false)
  const selectedElements = ref<string[]>([])
  const atomicEngine = ref<AtomicEngine | null>(null)

  // Computed
  const currentSlide = computed(() => {
    return presentation.value.slides[canvas.value.activeSlide] || null
  })

  const totalSlides = computed(() => {
    return presentation.value.slides.length
  })

  const canUndo = computed(() => {
    return history.value.past.length > 0
  })

  const canRedo = computed(() => {
    return history.value.future.length > 0
  })

  // Actions
  function initializeEngine() {
    atomicEngine.value = new AtomicEngine(presentation.value)
    
    // Listen to operations for history management
    atomicEngine.value.onOperation((operation, result) => {
      saveToHistory()
      // Emit to backend for AI learning
      emitOperationToBackend(operation, result)
    })
  }

  async function executeAtomicOperation(operation: AtomicOperationData): Promise<any> {
    if (!atomicEngine.value) {
      initializeEngine()
    }
    
    try {
      const result = await atomicEngine.value!.execute(operation)
      
      // Update local state
      presentation.value = atomicEngine.value!.getPresentation()
      
      return result
    } catch (error) {
      console.error('Failed to execute atomic operation:', error)
      throw error
    }
  }

  // Atomic Operation Helpers
  async function addText(slideIndex: number, data: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.ADD,
      type: ElementType.TEXT,
      target: slideIndex,
      data,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function addImage(slideIndex: number, data: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.ADD,
      type: ElementType.IMAGE,
      target: slideIndex,
      data,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function addShape(slideIndex: number, data: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.ADD,
      type: ElementType.SHAPE,
      target: slideIndex,
      data,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function addChart(slideIndex: number, data: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.ADD,
      type: ElementType.CHART,
      target: slideIndex,
      data,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function addTable(slideIndex: number, data: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.ADD,
      type: ElementType.TABLE,
      target: slideIndex,
      data,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function removeElement(elementId: string) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.REMOVE,
      type: 'element',
      target: elementId,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function modifyElement(elementId: string, changes: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.MODIFY,
      type: 'element',
      target: elementId,
      data: changes,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function createSlide(data: any = {}) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.CREATE,
      type: ElementType.SLIDE,
      target: canvas.value.activeSlide,
      data: { after: canvas.value.activeSlide, ...data },
      timestamp: Date.now()
    }
    const result = await executeAtomicOperation(operation)
    
    // Move to new slide
    canvas.value.activeSlide = Math.min(canvas.value.activeSlide + 1, totalSlides.value - 1)
    
    return result
  }

  async function deleteSlide(slideIndex: number) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.DELETE,
      type: ElementType.SLIDE,
      target: slideIndex,
      timestamp: Date.now()
    }
    const result = await executeAtomicOperation(operation)
    
    // Adjust active slide if necessary
    if (canvas.value.activeSlide >= totalSlides.value) {
      canvas.value.activeSlide = Math.max(0, totalSlides.value - 1)
    }
    
    return result
  }

  async function reorderSlides(newOrder: number[]) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.REORDER,
      type: 'slides',
      target: newOrder,
      data: { order: newOrder },
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  async function applyTheme(themeData: any) {
    const operation: AtomicOperationData = {
      op: AtomicOperation.APPLY,
      type: ElementType.THEME,
      target: 'all',
      data: themeData,
      timestamp: Date.now()
    }
    return executeAtomicOperation(operation)
  }

  // Canvas Operations
  function setActiveSlide(index: number) {
    if (index >= 0 && index < totalSlides.value) {
      canvas.value.activeSlide = index
      selectedElements.value = []
    }
  }

  function setZoom(zoom: number) {
    canvas.value.zoom = Math.max(0.1, Math.min(5, zoom))
  }

  function setCanvasOffset(x: number, y: number) {
    canvas.value.offsetX = x
    canvas.value.offsetY = y
  }

  function selectElements(elementIds: string[]) {
    selectedElements.value = elementIds
  }

  function toggleElementSelection(elementId: string) {
    const index = selectedElements.value.indexOf(elementId)
    if (index === -1) {
      selectedElements.value.push(elementId)
    } else {
      selectedElements.value.splice(index, 1)
    }
  }

  function clearSelection() {
    selectedElements.value = []
  }

  // History Management
  function saveToHistory() {
    history.value.past.push(JSON.parse(JSON.stringify(presentation.value)))
    history.value.future = []
    
    // Limit history size
    if (history.value.past.length > 50) {
      history.value.past.shift()
    }
  }

  function undo() {
    if (canUndo.value) {
      history.value.future.unshift(JSON.parse(JSON.stringify(presentation.value)))
      const previousState = history.value.past.pop()
      presentation.value = previousState
      
      // Reinitialize engine with restored state
      initializeEngine()
    }
  }

  function redo() {
    if (canRedo.value) {
      history.value.past.push(JSON.parse(JSON.stringify(presentation.value)))
      const nextState = history.value.future.shift()
      presentation.value = nextState
      
      // Reinitialize engine with restored state
      initializeEngine()
    }
  }

  // Clipboard Operations
  function copyElements(elementIds: string[]) {
    const elements = currentSlide.value?.elements.filter(el => 
      elementIds.includes(el.id)
    ) || []
    clipboard.value = JSON.parse(JSON.stringify(elements))
  }

  async function pasteElements() {
    if (clipboard.value.length === 0) return
    
    const operations: AtomicOperationData[] = []
    
    for (const element of clipboard.value) {
      const newElement = { 
        ...element, 
        id: uuidv4(),
        left: element.left + 20,
        top: element.top + 20
      }
      
      operations.push({
        op: AtomicOperation.ADD,
        type: element.type as ElementType,
        target: canvas.value.activeSlide,
        data: newElement,
        timestamp: Date.now()
      })
    }
    
    // Execute all paste operations
    for (const operation of operations) {
      await executeAtomicOperation(operation)
    }
  }

  // Presentation Management
  function newPresentation() {
    presentation.value = createDefaultPresentation()
    canvas.value = createDefaultCanvasState()
    history.value = { past: [], present: null, future: [] }
    selectedElements.value = []
    initializeEngine()
  }

  function loadPresentation(data: Presentation) {
    presentation.value = data
    canvas.value = createDefaultCanvasState()
    history.value = { past: [], present: null, future: [] }
    selectedElements.value = []
    initializeEngine()
  }

  // Export current state
  function exportPresentation() {
    return JSON.parse(JSON.stringify(presentation.value))
  }

  // Performance metrics
  function getPerformanceMetrics() {
    return atomicEngine.value?.getPerformanceMetrics() || {}
  }

  // Backend communication
  async function emitOperationToBackend(operation: AtomicOperationData, result: any) {
    try {
      // This would send the operation to the backend for AI learning
      const response = await fetch('/api/operations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation,
          result,
          presentationId: presentation.value.id,
          slideIndex: canvas.value.activeSlide,
          context: {
            totalSlides: totalSlides.value,
            currentElements: currentSlide.value?.elements.length || 0,
            selectedElements: selectedElements.value.length
          }
        })
      })
      
      if (!response.ok) {
        console.warn('Failed to send operation to backend')
      }
    } catch (error) {
      console.warn('Backend communication error:', error)
    }
  }

  // Initialize on store creation
  initializeEngine()

  return {
    // State
    presentation,
    canvas,
    history,
    clipboard,
    isPlaying,
    isFullscreen,
    selectedElements,
    
    // Computed
    currentSlide,
    totalSlides,
    canUndo,
    canRedo,
    
    // Actions
    executeAtomicOperation,
    addText,
    addImage,
    addShape,
    addChart,
    addTable,
    removeElement,
    modifyElement,
    createSlide,
    deleteSlide,
    reorderSlides,
    applyTheme,
    setActiveSlide,
    setZoom,
    setCanvasOffset,
    selectElements,
    toggleElementSelection,
    clearSelection,
    saveToHistory,
    undo,
    redo,
    copyElements,
    pasteElements,
    newPresentation,
    loadPresentation,
    exportPresentation,
    getPerformanceMetrics
  }
})

// Helper functions
function createDefaultPresentation(): Presentation {
  const defaultTheme: PresentationTheme = {
    id: uuidv4(),
    name: 'Default',
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      background: '#FFFFFF',
      text: '#333333',
      accent: '#FF5722'
    },
    fonts: {
      heading: 'Arial',
      body: 'Arial'
    },
    layouts: {},
    templates: {}
  }

  const defaultSlide: Slide = {
    id: uuidv4(),
    elements: [],
    layout: 'blank',
    createdAt: Date.now(),
    updatedAt: Date.now()
  }

  return {
    id: uuidv4(),
    title: 'New Presentation',
    slides: [defaultSlide],
    theme: defaultTheme,
    settings: {
      width: 1920,
      height: 1080,
      ratio: '16:9'
    },
    metadata: {
      author: 'AI-PPT User',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      version: '1.0.0',
      tags: []
    }
  }
}

function createDefaultCanvasState(): CanvasState {
  return {
    zoom: 1,
    offsetX: 0,
    offsetY: 0,
    selectedElements: [],
    activeSlide: 0,
    gridVisible: false,
    guidesVisible: false,
    snapToGrid: true
  }
}