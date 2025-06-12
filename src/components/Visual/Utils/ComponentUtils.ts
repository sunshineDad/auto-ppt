/**
 * Component Utilities - Helper functions for visual components
 */

import { nanoid } from 'nanoid'
import type { 
  VisualComponent, 
  BaseComponent,
  TextComponent,
  ImageComponent,
  ShapeComponent,
  ChartComponent,
  TableComponent,
  IconComponent,
  ComponentTheme
} from '../Types/ComponentTypes'
import { ElementType } from '@/types/atoms'

// Component Creation Utilities
export function createComponentId(): string {
  return nanoid()
}

export function createBaseComponent(type: ElementType, x = 0, y = 0, width = 100, height = 100): BaseComponent {
  return {
    id: createComponentId(),
    type,
    x,
    y,
    width,
    height,
    rotation: 0,
    opacity: 1,
    zIndex: 1,
    locked: false,
    visible: true,
    metadata: {
      createdAt: Date.now(),
      updatedAt: Date.now(),
      version: '1.0.0'
    }
  }
}

// Component Validation
export function validateComponent(component: VisualComponent): { valid: boolean; errors: string[] } {
  const errors: string[] = []
  
  // Basic validation
  if (!component.id) errors.push('Component must have an ID')
  if (!component.type) errors.push('Component must have a type')
  if (typeof component.x !== 'number') errors.push('Component x position must be a number')
  if (typeof component.y !== 'number') errors.push('Component y position must be a number')
  if (typeof component.width !== 'number' || component.width <= 0) errors.push('Component width must be a positive number')
  if (typeof component.height !== 'number' || component.height <= 0) errors.push('Component height must be a positive number')
  
  // Type-specific validation
  switch (component.type) {
    case ElementType.TEXT:
      const textComp = component as TextComponent
      if (!textComp.content) errors.push('Text component must have content')
      if (!textComp.style) errors.push('Text component must have style')
      break
      
    case ElementType.IMAGE:
      const imageComp = component as ImageComponent
      if (!imageComp.src) errors.push('Image component must have src')
      break
      
    case ElementType.CHART:
      const chartComp = component as ChartComponent
      if (!chartComp.data) errors.push('Chart component must have data')
      if (!chartComp.chartType) errors.push('Chart component must have chartType')
      break
      
    case ElementType.TABLE:
      const tableComp = component as TableComponent
      if (!tableComp.data) errors.push('Table component must have data')
      if (!tableComp.data.headers) errors.push('Table component must have headers')
      if (!tableComp.data.rows) errors.push('Table component must have rows')
      break
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

// Component Transformation Utilities
export function moveComponent(component: VisualComponent, deltaX: number, deltaY: number): VisualComponent {
  return {
    ...component,
    x: component.x + deltaX,
    y: component.y + deltaY,
    metadata: {
      ...component.metadata,
      updatedAt: Date.now()
    }
  }
}

export function resizeComponent(component: VisualComponent, newWidth: number, newHeight: number): VisualComponent {
  return {
    ...component,
    width: Math.max(20, newWidth), // Minimum size
    height: Math.max(20, newHeight),
    metadata: {
      ...component.metadata,
      updatedAt: Date.now()
    }
  }
}

export function rotateComponent(component: VisualComponent, rotation: number): VisualComponent {
  return {
    ...component,
    rotation: rotation % 360,
    metadata: {
      ...component.metadata,
      updatedAt: Date.now()
    }
  }
}

export function scaleComponent(component: VisualComponent, scaleX: number, scaleY: number): VisualComponent {
  return {
    ...component,
    width: Math.max(20, component.width * scaleX),
    height: Math.max(20, component.height * scaleY),
    metadata: {
      ...component.metadata,
      updatedAt: Date.now()
    }
  }
}

// Component Duplication
export function duplicateComponent(component: VisualComponent, offsetX = 20, offsetY = 20): VisualComponent {
  const duplicated = {
    ...JSON.parse(JSON.stringify(component)), // Deep clone
    id: createComponentId(),
    x: component.x + offsetX,
    y: component.y + offsetY,
    metadata: {
      ...component.metadata,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
  }
  
  return duplicated
}

// Component Bounds Calculation
export interface ComponentBounds {
  left: number
  top: number
  right: number
  bottom: number
  width: number
  height: number
  centerX: number
  centerY: number
}

export function getComponentBounds(component: VisualComponent): ComponentBounds {
  const left = component.x
  const top = component.y
  const right = component.x + component.width
  const bottom = component.y + component.height
  
  return {
    left,
    top,
    right,
    bottom,
    width: component.width,
    height: component.height,
    centerX: left + component.width / 2,
    centerY: top + component.height / 2
  }
}

export function getMultipleComponentsBounds(components: VisualComponent[]): ComponentBounds {
  if (components.length === 0) {
    return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0, centerX: 0, centerY: 0 }
  }
  
  const bounds = components.map(getComponentBounds)
  const left = Math.min(...bounds.map(b => b.left))
  const top = Math.min(...bounds.map(b => b.top))
  const right = Math.max(...bounds.map(b => b.right))
  const bottom = Math.max(...bounds.map(b => b.bottom))
  
  return {
    left,
    top,
    right,
    bottom,
    width: right - left,
    height: bottom - top,
    centerX: left + (right - left) / 2,
    centerY: top + (bottom - top) / 2
  }
}

// Component Collision Detection
export function isComponentColliding(comp1: VisualComponent, comp2: VisualComponent): boolean {
  const bounds1 = getComponentBounds(comp1)
  const bounds2 = getComponentBounds(comp2)
  
  return !(
    bounds1.right < bounds2.left ||
    bounds1.left > bounds2.right ||
    bounds1.bottom < bounds2.top ||
    bounds1.top > bounds2.bottom
  )
}

export function getCollidingComponents(component: VisualComponent, components: VisualComponent[]): VisualComponent[] {
  return components.filter(comp => comp.id !== component.id && isComponentColliding(component, comp))
}

// Component Alignment Utilities
export function alignComponents(components: VisualComponent[], alignment: 'left' | 'center' | 'right' | 'top' | 'middle' | 'bottom'): VisualComponent[] {
  if (components.length < 2) return components
  
  const bounds = getMultipleComponentsBounds(components)
  
  return components.map(component => {
    let newX = component.x
    let newY = component.y
    
    switch (alignment) {
      case 'left':
        newX = bounds.left
        break
      case 'center':
        newX = bounds.centerX - component.width / 2
        break
      case 'right':
        newX = bounds.right - component.width
        break
      case 'top':
        newY = bounds.top
        break
      case 'middle':
        newY = bounds.centerY - component.height / 2
        break
      case 'bottom':
        newY = bounds.bottom - component.height
        break
    }
    
    return {
      ...component,
      x: newX,
      y: newY,
      metadata: {
        ...component.metadata,
        updatedAt: Date.now()
      }
    }
  })
}

export function distributeComponents(components: VisualComponent[], direction: 'horizontal' | 'vertical'): VisualComponent[] {
  if (components.length < 3) return components
  
  const sorted = [...components].sort((a, b) => 
    direction === 'horizontal' ? a.x - b.x : a.y - b.y
  )
  
  const first = sorted[0]
  const last = sorted[sorted.length - 1]
  const totalSpace = direction === 'horizontal' 
    ? (last.x + last.width) - first.x
    : (last.y + last.height) - first.y
  
  const componentSpace = sorted.reduce((sum, comp) => 
    sum + (direction === 'horizontal' ? comp.width : comp.height), 0
  )
  
  const spacing = (totalSpace - componentSpace) / (sorted.length - 1)
  
  let currentPos = direction === 'horizontal' ? first.x : first.y
  
  return sorted.map((component, index) => {
    if (index === 0) return component
    
    currentPos += spacing + (direction === 'horizontal' 
      ? sorted[index - 1].width 
      : sorted[index - 1].height
    )
    
    return {
      ...component,
      x: direction === 'horizontal' ? currentPos : component.x,
      y: direction === 'vertical' ? currentPos : component.y,
      metadata: {
        ...component.metadata,
        updatedAt: Date.now()
      }
    }
  })
}

// Component Grouping
export interface ComponentGroup {
  id: string
  name: string
  components: VisualComponent[]
  bounds: ComponentBounds
  locked: boolean
  visible: boolean
}

export function createComponentGroup(components: VisualComponent[], name = 'Group'): ComponentGroup {
  return {
    id: createComponentId(),
    name,
    components: [...components],
    bounds: getMultipleComponentsBounds(components),
    locked: false,
    visible: true
  }
}

export function ungroupComponents(group: ComponentGroup): VisualComponent[] {
  return group.components
}

// Component Snapping
export interface SnapGuide {
  type: 'vertical' | 'horizontal'
  position: number
  components: string[]
}

export function getSnapGuides(component: VisualComponent, allComponents: VisualComponent[], snapDistance = 10): SnapGuide[] {
  const guides: SnapGuide[] = []
  const bounds = getComponentBounds(component)
  
  allComponents.forEach(comp => {
    if (comp.id === component.id) return
    
    const compBounds = getComponentBounds(comp)
    
    // Vertical guides (for horizontal alignment)
    const verticalPositions = [compBounds.left, compBounds.centerX, compBounds.right]
    const componentVerticalPositions = [bounds.left, bounds.centerX, bounds.right]
    
    verticalPositions.forEach(pos => {
      componentVerticalPositions.forEach(compPos => {
        if (Math.abs(pos - compPos) <= snapDistance) {
          guides.push({
            type: 'vertical',
            position: pos,
            components: [comp.id]
          })
        }
      })
    })
    
    // Horizontal guides (for vertical alignment)
    const horizontalPositions = [compBounds.top, compBounds.centerY, compBounds.bottom]
    const componentHorizontalPositions = [bounds.top, bounds.centerY, bounds.bottom]
    
    horizontalPositions.forEach(pos => {
      componentHorizontalPositions.forEach(compPos => {
        if (Math.abs(pos - compPos) <= snapDistance) {
          guides.push({
            type: 'horizontal',
            position: pos,
            components: [comp.id]
          })
        }
      })
    })
  })
  
  return guides
}

// Component Export/Import
export function exportComponent(component: VisualComponent): string {
  return JSON.stringify(component, null, 2)
}

export function importComponent(data: string): VisualComponent | null {
  try {
    const component = JSON.parse(data)
    const validation = validateComponent(component)
    
    if (validation.valid) {
      return {
        ...component,
        id: createComponentId(), // Generate new ID
        metadata: {
          ...component.metadata,
          createdAt: Date.now(),
          updatedAt: Date.now()
        }
      }
    }
    
    console.error('Invalid component data:', validation.errors)
    return null
  } catch (error) {
    console.error('Failed to parse component data:', error)
    return null
  }
}

// Theme Application
export function applyThemeToComponent(component: VisualComponent, theme: ComponentTheme): VisualComponent {
  const updated = { ...component }
  
  switch (component.type) {
    case ElementType.TEXT:
      const textComp = updated as TextComponent
      textComp.style = {
        ...textComp.style,
        color: theme.colors.text,
        fontFamily: theme.fonts.primary
      }
      break
      
    case ElementType.SHAPE:
      const shapeComp = updated as ShapeComponent
      shapeComp.style = {
        ...shapeComp.style,
        fill: theme.colors.primary,
        stroke: theme.colors.border
      }
      break
      
    case ElementType.CHART:
      const chartComp = updated as ChartComponent
      chartComp.style = {
        ...chartComp.style,
        backgroundColor: theme.colors.surface
      }
      break
  }
  
  updated.metadata = {
    ...updated.metadata,
    updatedAt: Date.now()
  }
  
  return updated
}

// Performance Utilities
export function shouldComponentUpdate(oldComponent: VisualComponent, newComponent: VisualComponent): boolean {
  // Quick reference check
  if (oldComponent === newComponent) return false
  
  // Check key properties that affect rendering
  const keyProps = ['x', 'y', 'width', 'height', 'rotation', 'opacity', 'visible']
  
  for (const prop of keyProps) {
    if ((oldComponent as any)[prop] !== (newComponent as any)[prop]) {
      return true
    }
  }
  
  // Check type-specific properties
  switch (newComponent.type) {
    case ElementType.TEXT:
      const oldText = oldComponent as TextComponent
      const newText = newComponent as TextComponent
      return oldText.content !== newText.content || 
             JSON.stringify(oldText.style) !== JSON.stringify(newText.style)
             
    case ElementType.IMAGE:
      const oldImage = oldComponent as ImageComponent
      const newImage = newComponent as ImageComponent
      return oldImage.src !== newImage.src ||
             JSON.stringify(oldImage.style) !== JSON.stringify(newImage.style)
             
    case ElementType.CHART:
      const oldChart = oldComponent as ChartComponent
      const newChart = newComponent as ChartComponent
      return oldChart.chartType !== newChart.chartType ||
             JSON.stringify(oldChart.data) !== JSON.stringify(newChart.data)
             
    default:
      return true
  }
}

// Component Search and Filtering
export function searchComponents(components: VisualComponent[], query: string): VisualComponent[] {
  const lowerQuery = query.toLowerCase()
  
  return components.filter(component => {
    // Search in component type
    if (component.type.toLowerCase().includes(lowerQuery)) return true
    
    // Search in component content
    switch (component.type) {
      case ElementType.TEXT:
        const textComp = component as TextComponent
        return textComp.content.toLowerCase().includes(lowerQuery)
        
      case ElementType.IMAGE:
        const imageComp = component as ImageComponent
        return imageComp.alt?.toLowerCase().includes(lowerQuery) || false
        
      default:
        return false
    }
  })
}

export function filterComponentsByType(components: VisualComponent[], types: ElementType[]): VisualComponent[] {
  return components.filter(component => types.includes(component.type))
}

export function sortComponents(components: VisualComponent[], sortBy: 'position' | 'size' | 'type' | 'created'): VisualComponent[] {
  return [...components].sort((a, b) => {
    switch (sortBy) {
      case 'position':
        return a.y - b.y || a.x - b.x
      case 'size':
        return (b.width * b.height) - (a.width * a.height)
      case 'type':
        return a.type.localeCompare(b.type)
      case 'created':
        return (a.metadata?.createdAt || 0) - (b.metadata?.createdAt || 0)
      default:
        return 0
    }
  })
}