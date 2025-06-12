<template>
  <div class="visual-chart" :class="chartClasses" :style="chartContainerStyle">
    <canvas
      ref="chartCanvas"
      :width="component.width"
      :height="component.height"
      :style="canvasStyle"
    ></canvas>
    
    <!-- Loading state -->
    <div v-if="loading" class="chart-loading">
      <div class="loading-spinner"></div>
      <span>Loading chart...</span>
    </div>
    
    <!-- Error state -->
    <div v-if="error" class="chart-error">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
      <span>Failed to render chart</span>
      <button @click="retryChart" class="retry-button">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { ChartComponent } from '../Types/ComponentTypes'

// Register Chart.js components
Chart.register(...registerables)

interface Props {
  component: ChartComponent
  selected?: boolean
}

interface Emits {
  (e: 'update', component: ChartComponent, changes: Partial<ChartComponent>): void
  (e: 'error', component: ChartComponent, error: Error): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false
})

const emit = defineEmits<Emits>()

const chartCanvas = ref<HTMLCanvasElement>()
const chartInstance = ref<Chart | null>(null)
const loading = ref(true)
const error = ref(false)
const errorMessage = ref('')

// Computed properties
const chartClasses = computed(() => ({
  'visual-chart': true,
  'selected': props.selected,
  'loading': loading.value,
  'error': error.value
}))

const chartContainerStyle = computed(() => ({
  width: '100%',
  height: '100%',
  backgroundColor: props.component.style.backgroundColor || 'transparent',
  borderRadius: props.component.style.borderRadius ? `${props.component.style.borderRadius}px` : '0',
  padding: props.component.style.padding ? 
    `${props.component.style.padding.top}px ${props.component.style.padding.right}px ${props.component.style.padding.bottom}px ${props.component.style.padding.left}px` : 
    '0',
  boxShadow: props.component.style.shadow ? buildShadowString(props.component.style.shadow) : 'none',
  border: props.component.style.border ? 
    `${props.component.style.border.width}px ${props.component.style.border.style} ${props.component.style.border.color}` : 
    'none',
  position: 'relative',
  overflow: 'hidden'
}))

const canvasStyle = computed(() => ({
  width: '100%',
  height: '100%',
  display: loading.value || error.value ? 'none' : 'block'
}))

// Helper functions
function buildShadowString(shadow: NonNullable<ChartComponent['style']['shadow']>) {
  return `${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.spreadRadius || 0}px ${shadow.color}${shadow.inset ? ' inset' : ''}`
}

// Chart creation and management
async function createChart() {
  if (!chartCanvas.value) return
  
  try {
    loading.value = true
    error.value = false
    
    // Wait for canvas to be properly mounted
    await nextTick()
    
    // Ensure canvas has proper dimensions
    const canvas = chartCanvas.value
    if (!canvas.offsetParent && canvas.offsetWidth === 0 && canvas.offsetHeight === 0) {
      // Canvas not yet in DOM, retry after next tick
      await nextTick()
      return createChart()
    }
    
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      throw new Error('Failed to get 2D context from canvas')
    }
    
    // Destroy existing chart instance
    if (chartInstance.value) {
      chartInstance.value.destroy()
      chartInstance.value = null
    }
    
    // Ensure canvas has proper dimensions
    if (canvas.width === 0 || canvas.height === 0) {
      canvas.width = props.component.width || 400
      canvas.height = props.component.height || 300
    }
    
    // Create chart configuration
    const config = {
      type: props.component.chartType,
      data: {
        ...props.component.data,
        datasets: props.component.data.datasets.map(dataset => ({
          ...dataset,
          backgroundColor: dataset.backgroundColor || generateColors(props.component.data.labels.length),
          borderColor: dataset.borderColor || generateColors(props.component.data.labels.length, 0.8),
          borderWidth: dataset.borderWidth || 2
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 750,
          easing: 'easeInOutQuart'
        },
        plugins: {
          legend: {
            display: true,
            position: 'top' as const,
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#3498db',
            borderWidth: 1,
            cornerRadius: 6,
            displayColors: true
          }
        },
        scales: getScalesConfig(),
        ...props.component.options
      }
    }
    
    // Create chart instance
    chartInstance.value = new Chart(ctx, config as any)
    
    loading.value = false
    
  } catch (err) {
    console.error('Failed to create chart:', err)
    error.value = true
    errorMessage.value = err instanceof Error ? err.message : 'Unknown error'
    loading.value = false
    emit('error', props.component, err instanceof Error ? err : new Error('Chart creation failed'))
  }
}

function getScalesConfig() {
  const isCartesian = ['bar', 'line', 'area', 'scatter'].includes(props.component.chartType)
  
  if (!isCartesian) return {}
  
  return {
    x: {
      grid: {
        color: 'rgba(0, 0, 0, 0.1)',
        lineWidth: 1
      },
      ticks: {
        font: {
          size: 11
        },
        color: '#666'
      }
    },
    y: {
      grid: {
        color: 'rgba(0, 0, 0, 0.1)',
        lineWidth: 1
      },
      ticks: {
        font: {
          size: 11
        },
        color: '#666'
      },
      beginAtZero: true
    }
  }
}

function generateColors(count: number, alpha = 1) {
  const colors = [
    `rgba(52, 152, 219, ${alpha})`,   // Blue
    `rgba(46, 204, 113, ${alpha})`,   // Green
    `rgba(231, 76, 60, ${alpha})`,    // Red
    `rgba(241, 196, 15, ${alpha})`,   // Yellow
    `rgba(155, 89, 182, ${alpha})`,   // Purple
    `rgba(230, 126, 34, ${alpha})`,   // Orange
    `rgba(26, 188, 156, ${alpha})`,   // Turquoise
    `rgba(149, 165, 166, ${alpha})`   // Gray
  ]
  
  const result = []
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length])
  }
  
  return result
}

function retryChart() {
  createChart()
}

// Lifecycle hooks
onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
})

// Watch for component changes
watch(() => props.component, () => {
  createChart()
}, { deep: true })

watch(() => [props.component.width, props.component.height], () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
})

// Expose methods
defineExpose({
  updateChart() {
    createChart()
  },
  getChartInstance() {
    return chartInstance.value
  },
  exportChart(format: 'png' | 'jpeg' = 'png') {
    if (chartInstance.value) {
      return chartInstance.value.toBase64Image(format, 1.0)
    }
    return null
  }
})
</script>

<style scoped>
.visual-chart {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.visual-chart.selected {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

.chart-loading,
.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #6c757d;
  font-size: 14px;
  text-align: center;
  padding: 20px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e9ecef;
  border-top: 3px solid var(--primary, #3498db);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chart-error svg {
  color: #dc3545;
}

.retry-button {
  background: var(--primary, #3498db);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background: var(--primary-dark, #2980b9);
}

/* Canvas styling */
canvas {
  max-width: 100%;
  max-height: 100%;
  user-select: none;
}

/* Hover effects */
.visual-chart:hover {
  transform: scale(1.01);
  transition: transform 0.2s ease;
}

.visual-chart.selected:hover {
  transform: scale(1.02);
}
</style>