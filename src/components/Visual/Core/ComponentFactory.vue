<template>
  <div class="component-factory">
    <!-- This component handles creation of all visual components -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { nanoid } from 'nanoid'
import type { 
  VisualComponent, 
  TextComponent, 
  ImageComponent, 
  ShapeComponent, 
  ChartComponent, 
  TableComponent, 
  IconComponent,
  ComponentFactory as IComponentFactory
} from '../Types/ComponentTypes'
import { ElementType } from '@/types/atoms'

// Component Factory Implementation
const componentFactory: IComponentFactory = {
  createText(options = {}) {
    const defaultText: TextComponent = {
      id: nanoid(),
      type: ElementType.TEXT,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 200,
      height: options.height || 50,
      content: options.content || 'New Text',
      style: {
        fontSize: 16,
        fontFamily: 'Inter, sans-serif',
        fontWeight: 'normal',
        fontStyle: 'normal',
        color: '#000000',
        textAlign: 'left',
        verticalAlign: 'top',
        lineHeight: 1.4,
        ...options.style
      },
      editable: true,
      ...options
    }
    return defaultText
  },

  createImage(options = {}) {
    const defaultImage: ImageComponent = {
      id: nanoid(),
      type: ElementType.IMAGE,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 300,
      height: options.height || 200,
      src: options.src || '/placeholder-image.jpg',
      alt: options.alt || 'Image',
      style: {
        objectFit: 'cover',
        objectPosition: 'center',
        borderRadius: 0,
        ...options.style
      },
      ...options
    }
    return defaultImage
  },

  createShape(options = {}) {
    const defaultShape: ShapeComponent = {
      id: nanoid(),
      type: ElementType.SHAPE,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 150,
      height: options.height || 150,
      shape: options.shape || 'rectangle',
      style: {
        fill: '#3498db',
        stroke: '#2980b9',
        strokeWidth: 2,
        cornerRadius: 8,
        ...options.style
      },
      ...options
    }
    return defaultShape
  },

  createChart(options = {}) {
    const defaultChart: ChartComponent = {
      id: nanoid(),
      type: ElementType.CHART,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 400,
      height: options.height || 300,
      chartType: options.chartType || 'bar',
      data: options.data || {
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [{
          label: 'Sales',
          data: [30, 45, 60, 80],
          backgroundColor: '#3498db',
          borderColor: '#2980b9',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          }
        },
        ...options.options
      },
      style: {
        backgroundColor: '#ffffff',
        borderRadius: 8,
        ...options.style
      },
      ...options
    }
    return defaultChart
  },

  createTable(options = {}) {
    const defaultTable: TableComponent = {
      id: nanoid(),
      type: ElementType.TABLE,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 400,
      height: options.height || 200,
      data: options.data || {
        headers: ['Column 1', 'Column 2', 'Column 3'],
        rows: [
          ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
          ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3'],
          ['Row 3 Col 1', 'Row 3 Col 2', 'Row 3 Col 3']
        ]
      },
      style: {
        variant: 'modern',
        headerStyle: {
          backgroundColor: '#f8f9fa',
          color: '#2c3e50',
          fontWeight: 'bold',
          textAlign: 'left',
          padding: { top: 12, right: 16, bottom: 12, left: 16 }
        },
        cellStyle: {
          backgroundColor: '#ffffff',
          color: '#2c3e50',
          textAlign: 'left',
          padding: { top: 8, right: 16, bottom: 8, left: 16 },
          border: { width: 1, style: 'solid', color: '#e9ecef', radius: 0 }
        },
        borderCollapse: 'collapse',
        ...options.style
      },
      ...options
    }
    return defaultTable
  },

  createIcon(options = {}) {
    const defaultIcon: IconComponent = {
      id: nanoid(),
      type: 'icon' as any,
      x: options.x || 100,
      y: options.y || 100,
      width: options.width || 48,
      height: options.height || 48,
      iconName: options.iconName || 'star',
      iconSet: options.iconSet || 'feather',
      style: {
        color: '#3498db',
        size: 24,
        strokeWidth: 2,
        fill: false,
        ...options.style
      },
      ...options
    }
    return defaultIcon
  }
}

// Expose factory methods
defineExpose({
  createText: componentFactory.createText,
  createImage: componentFactory.createImage,
  createShape: componentFactory.createShape,
  createChart: componentFactory.createChart,
  createTable: componentFactory.createTable,
  createIcon: componentFactory.createIcon
})
</script>

<style scoped>
.component-factory {
  display: none; /* This is a utility component */
}
</style>