/**
 * Atomic Operations Utilities - Integration with the 7 atomic operations
 */

import { nanoid } from 'nanoid'
import type { 
  VisualComponent,
  AtomicComponentOperation,
  AtomicOperationResult,
  AtomicOperationContext,
  AtomicOperationHistory,
  OperationValidation,
  AtomicAddOperation,
  AtomicRemoveOperation,
  AtomicModifyOperation,
  AtomicCreateOperation,
  AtomicDeleteOperation,
  AtomicReorderOperation,
  AtomicApplyOperation
} from '../Types/AtomicTypes'
import { AtomicOperation, ElementType } from '@/types/atoms'
import { validateComponent, createComponentId } from './ComponentUtils'

// Operation Factory
export class AtomicOperationFactory {
  static createAddOperation(
    componentType: ElementType,
    data: any,
    position: { x: number; y: number },
    context: AtomicOperationContext
  ): AtomicAddOperation {
    return {
      operation: AtomicOperation.ADD,
      componentType,
      data,
      position,
      context
    }
  }

  static createRemoveOperation(
    componentIds: string[],
    context: AtomicOperationContext
  ): AtomicRemoveOperation {
    return {
      operation: AtomicOperation.REMOVE,
      componentIds,
      context
    }
  }

  static createModifyOperation(
    componentId: string,
    changes: any,
    context: AtomicOperationContext
  ): AtomicModifyOperation {
    return {
      operation: AtomicOperation.MODIFY,
      componentId,
      changes,
      context
    }
  }

  static createCreateOperation(
    createType: 'slide' | 'template' | 'group',
    data: any,
    context: AtomicOperationContext
  ): AtomicCreateOperation {
    return {
      operation: AtomicOperation.CREATE,
      createType,
      data,
      context
    }
  }

  static createDeleteOperation(
    deleteType: 'component' | 'slide' | 'group',
    targetIds: string[],
    context: AtomicOperationContext
  ): AtomicDeleteOperation {
    return {
      operation: AtomicOperation.DELETE,
      deleteType,
      targetIds,
      context
    }
  }

  static createReorderOperation(
    reorderType: 'components' | 'slides' | 'layers',
    data: any,
    context: AtomicOperationContext
  ): AtomicReorderOperation {
    return {
      operation: AtomicOperation.REORDER,
      reorderType,
      data,
      context
    }
  }

  static createApplyOperation(
    applyType: 'theme' | 'style' | 'animation' | 'layout' | 'template',
    data: any,
    targets: string[],
    context: AtomicOperationContext
  ): AtomicApplyOperation {
    return {
      operation: AtomicOperation.APPLY,
      applyType,
      data,
      targets,
      context
    }
  }
}

// Operation Validator
export class AtomicOperationValidator {
  static validate(operation: AtomicComponentOperation): OperationValidation {
    const errors: any[] = []
    const warnings: any[] = []

    // Basic validation
    if (!operation.operation) {
      errors.push({ code: 'MISSING_OPERATION', message: 'Operation type is required' })
    }

    if (!operation.context) {
      errors.push({ code: 'MISSING_CONTEXT', message: 'Operation context is required' })
    }

    // Operation-specific validation
    switch (operation.operation) {
      case AtomicOperation.ADD:
        this.validateAddOperation(operation as AtomicAddOperation, errors, warnings)
        break
      case AtomicOperation.REMOVE:
        this.validateRemoveOperation(operation as AtomicRemoveOperation, errors, warnings)
        break
      case AtomicOperation.MODIFY:
        this.validateModifyOperation(operation as AtomicModifyOperation, errors, warnings)
        break
      case AtomicOperation.CREATE:
        this.validateCreateOperation(operation as AtomicCreateOperation, errors, warnings)
        break
      case AtomicOperation.DELETE:
        this.validateDeleteOperation(operation as AtomicDeleteOperation, errors, warnings)
        break
      case AtomicOperation.REORDER:
        this.validateReorderOperation(operation as AtomicReorderOperation, errors, warnings)
        break
      case AtomicOperation.APPLY:
        this.validateApplyOperation(operation as AtomicApplyOperation, errors, warnings)
        break
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }

  private static validateAddOperation(operation: AtomicAddOperation, errors: any[], warnings: any[]) {
    if (!operation.componentType) {
      errors.push({ code: 'MISSING_COMPONENT_TYPE', message: 'Component type is required for ADD operation' })
    }

    if (!operation.data) {
      errors.push({ code: 'MISSING_DATA', message: 'Component data is required for ADD operation' })
    }

    if (!operation.position) {
      errors.push({ code: 'MISSING_POSITION', message: 'Position is required for ADD operation' })
    } else {
      if (typeof operation.position.x !== 'number' || typeof operation.position.y !== 'number') {
        errors.push({ code: 'INVALID_POSITION', message: 'Position must have numeric x and y coordinates' })
      }
    }

    // Check canvas bounds
    if (operation.context && operation.position) {
      if (operation.position.x < 0 || operation.position.y < 0) {
        warnings.push({ code: 'POSITION_OUT_OF_BOUNDS', message: 'Component position is outside canvas bounds' })
      }
    }
  }

  private static validateRemoveOperation(operation: AtomicRemoveOperation, errors: any[], warnings: any[]) {
    if (!operation.componentIds || operation.componentIds.length === 0) {
      errors.push({ code: 'MISSING_COMPONENT_IDS', message: 'Component IDs are required for REMOVE operation' })
    }
  }

  private static validateModifyOperation(operation: AtomicModifyOperation, errors: any[], warnings: any[]) {
    if (!operation.componentId) {
      errors.push({ code: 'MISSING_COMPONENT_ID', message: 'Component ID is required for MODIFY operation' })
    }

    if (!operation.changes || Object.keys(operation.changes).length === 0) {
      warnings.push({ code: 'NO_CHANGES', message: 'No changes specified for MODIFY operation' })
    }
  }

  private static validateCreateOperation(operation: AtomicCreateOperation, errors: any[], warnings: any[]) {
    if (!operation.createType) {
      errors.push({ code: 'MISSING_CREATE_TYPE', message: 'Create type is required for CREATE operation' })
    }

    if (!operation.data) {
      errors.push({ code: 'MISSING_DATA', message: 'Data is required for CREATE operation' })
    }
  }

  private static validateDeleteOperation(operation: AtomicDeleteOperation, errors: any[], warnings: any[]) {
    if (!operation.deleteType) {
      errors.push({ code: 'MISSING_DELETE_TYPE', message: 'Delete type is required for DELETE operation' })
    }

    if (!operation.targetIds || operation.targetIds.length === 0) {
      errors.push({ code: 'MISSING_TARGET_IDS', message: 'Target IDs are required for DELETE operation' })
    }
  }

  private static validateReorderOperation(operation: AtomicReorderOperation, errors: any[], warnings: any[]) {
    if (!operation.reorderType) {
      errors.push({ code: 'MISSING_REORDER_TYPE', message: 'Reorder type is required for REORDER operation' })
    }

    if (!operation.data) {
      errors.push({ code: 'MISSING_DATA', message: 'Data is required for REORDER operation' })
    }
  }

  private static validateApplyOperation(operation: AtomicApplyOperation, errors: any[], warnings: any[]) {
    if (!operation.applyType) {
      errors.push({ code: 'MISSING_APPLY_TYPE', message: 'Apply type is required for APPLY operation' })
    }

    if (!operation.data) {
      errors.push({ code: 'MISSING_DATA', message: 'Data is required for APPLY operation' })
    }

    if (!operation.targets || operation.targets.length === 0) {
      warnings.push({ code: 'NO_TARGETS', message: 'No targets specified for APPLY operation' })
    }
  }
}

// Operation Processor
export class AtomicOperationProcessor {
  private history: Map<string, AtomicOperationHistory[]> = new Map()
  private components: Map<string, VisualComponent[]> = new Map()

  async processOperation(operation: AtomicComponentOperation): Promise<AtomicOperationResult> {
    const startTime = Date.now()
    const operationId = nanoid()

    try {
      // Validate operation
      const validation = AtomicOperationValidator.validate(operation)
      if (!validation.valid) {
        throw new Error(`Operation validation failed: ${validation.errors.map(e => e.message).join(', ')}`)
      }

      // Process operation
      let result: AtomicOperationResult
      switch (operation.operation) {
        case AtomicOperation.ADD:
          result = await this.processAddOperation(operation as AtomicAddOperation, operationId)
          break
        case AtomicOperation.REMOVE:
          result = await this.processRemoveOperation(operation as AtomicRemoveOperation, operationId)
          break
        case AtomicOperation.MODIFY:
          result = await this.processModifyOperation(operation as AtomicModifyOperation, operationId)
          break
        case AtomicOperation.CREATE:
          result = await this.processCreateOperation(operation as AtomicCreateOperation, operationId)
          break
        case AtomicOperation.DELETE:
          result = await this.processDeleteOperation(operation as AtomicDeleteOperation, operationId)
          break
        case AtomicOperation.REORDER:
          result = await this.processReorderOperation(operation as AtomicReorderOperation, operationId)
          break
        case AtomicOperation.APPLY:
          result = await this.processApplyOperation(operation as AtomicApplyOperation, operationId)
          break
        default:
          throw new Error(`Unsupported operation: ${operation.operation}`)
      }

      // Add timing metadata
      result.metadata.duration = Date.now() - startTime

      // Record in history
      this.recordInHistory(operation, result)

      return result

    } catch (error) {
      return {
        success: false,
        operationId,
        operation: operation.operation,
        componentIds: [],
        changes: [],
        error: error instanceof Error ? error.message : 'Unknown error',
        metadata: {
          timestamp: Date.now(),
          duration: Date.now() - startTime,
          userId: operation.context.userId,
          sessionId: operation.context.sessionId
        }
      }
    }
  }

  private async processAddOperation(operation: AtomicAddOperation, operationId: string): Promise<AtomicOperationResult> {
    // Create new component
    const component = this.createComponentFromData(operation.componentType, operation.data, operation.position)
    
    // Validate component
    const validation = validateComponent(component)
    if (!validation.valid) {
      throw new Error(`Invalid component: ${validation.errors.join(', ')}`)
    }

    // Add to slide
    const slideId = operation.context.slideId
    const slideComponents = this.components.get(slideId) || []
    slideComponents.push(component)
    this.components.set(slideId, slideComponents)

    return {
      success: true,
      operationId,
      operation: AtomicOperation.ADD,
      componentIds: [component.id],
      changes: [component],
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private async processRemoveOperation(operation: AtomicRemoveOperation, operationId: string): Promise<AtomicOperationResult> {
    const slideId = operation.context.slideId
    const slideComponents = this.components.get(slideId) || []
    
    // Find components to remove
    const componentsToRemove = slideComponents.filter(comp => operation.componentIds.includes(comp.id))
    
    // Remove components
    const remainingComponents = slideComponents.filter(comp => !operation.componentIds.includes(comp.id))
    this.components.set(slideId, remainingComponents)

    return {
      success: true,
      operationId,
      operation: AtomicOperation.REMOVE,
      componentIds: operation.componentIds,
      changes: componentsToRemove,
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private async processModifyOperation(operation: AtomicModifyOperation, operationId: string): Promise<AtomicOperationResult> {
    const slideId = operation.context.slideId
    const slideComponents = this.components.get(slideId) || []
    
    // Find component to modify
    const componentIndex = slideComponents.findIndex(comp => comp.id === operation.componentId)
    if (componentIndex === -1) {
      throw new Error(`Component ${operation.componentId} not found`)
    }

    const originalComponent = slideComponents[componentIndex]
    const modifiedComponent = {
      ...originalComponent,
      ...operation.changes,
      metadata: {
        ...originalComponent.metadata,
        updatedAt: Date.now()
      }
    }

    // Validate modified component
    const validation = validateComponent(modifiedComponent)
    if (!validation.valid) {
      throw new Error(`Invalid modified component: ${validation.errors.join(', ')}`)
    }

    // Update component
    slideComponents[componentIndex] = modifiedComponent
    this.components.set(slideId, slideComponents)

    return {
      success: true,
      operationId,
      operation: AtomicOperation.MODIFY,
      componentIds: [operation.componentId],
      changes: [modifiedComponent],
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private async processCreateOperation(operation: AtomicCreateOperation, operationId: string): Promise<AtomicOperationResult> {
    // Implementation depends on create type
    switch (operation.createType) {
      case 'slide':
        // Create new slide logic
        break
      case 'template':
        // Create template logic
        break
      case 'group':
        // Create component group logic
        break
    }

    return {
      success: true,
      operationId,
      operation: AtomicOperation.CREATE,
      componentIds: [],
      changes: [],
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private async processDeleteOperation(operation: AtomicDeleteOperation, operationId: string): Promise<AtomicOperationResult> {
    // Similar to remove but with different semantics
    return this.processRemoveOperation({
      operation: AtomicOperation.REMOVE,
      componentIds: operation.targetIds,
      context: operation.context
    }, operationId)
  }

  private async processReorderOperation(operation: AtomicReorderOperation, operationId: string): Promise<AtomicOperationResult> {
    const slideId = operation.context.slideId
    const slideComponents = this.components.get(slideId) || []

    switch (operation.reorderType) {
      case 'components':
        // Reorder components based on new order
        const reorderData = operation.data as any
        if (reorderData.newOrder) {
          const reorderedComponents = reorderData.newOrder.map((id: string) => 
            slideComponents.find(comp => comp.id === id)
          ).filter(Boolean)
          this.components.set(slideId, reorderedComponents)
        }
        break
      case 'layers':
        // Update z-index of components
        const layerData = operation.data as any
        if (layerData.zIndexChanges) {
          slideComponents.forEach(comp => {
            if (layerData.zIndexChanges[comp.id] !== undefined) {
              comp.zIndex = layerData.zIndexChanges[comp.id]
            }
          })
          this.components.set(slideId, slideComponents)
        }
        break
    }

    return {
      success: true,
      operationId,
      operation: AtomicOperation.REORDER,
      componentIds: [],
      changes: slideComponents,
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private async processApplyOperation(operation: AtomicApplyOperation, operationId: string): Promise<AtomicOperationResult> {
    const slideId = operation.context.slideId
    const slideComponents = this.components.get(slideId) || []
    
    let targetComponents: VisualComponent[]
    
    if (operation.targets.includes('all')) {
      targetComponents = slideComponents
    } else {
      targetComponents = slideComponents.filter(comp => operation.targets.includes(comp.id))
    }

    // Apply changes based on apply type
    const modifiedComponents = targetComponents.map(comp => {
      switch (operation.applyType) {
        case 'theme':
          // Apply theme to component
          return this.applyThemeToComponent(comp, operation.data)
        case 'style':
          // Apply style to component
          return this.applyStyleToComponent(comp, operation.data)
        case 'animation':
          // Apply animation to component
          return this.applyAnimationToComponent(comp, operation.data)
        default:
          return comp
      }
    })

    // Update components
    modifiedComponents.forEach(modifiedComp => {
      const index = slideComponents.findIndex(comp => comp.id === modifiedComp.id)
      if (index !== -1) {
        slideComponents[index] = modifiedComp
      }
    })
    this.components.set(slideId, slideComponents)

    return {
      success: true,
      operationId,
      operation: AtomicOperation.APPLY,
      componentIds: modifiedComponents.map(comp => comp.id),
      changes: modifiedComponents,
      metadata: {
        timestamp: Date.now(),
        duration: 0,
        userId: operation.context.userId,
        sessionId: operation.context.sessionId
      }
    }
  }

  private createComponentFromData(type: ElementType, data: any, position: { x: number; y: number }): VisualComponent {
    const baseComponent = {
      id: createComponentId(),
      type,
      x: position.x,
      y: position.y,
      width: data.width || 100,
      height: data.height || 100,
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

    // Type-specific component creation
    switch (type) {
      case ElementType.TEXT:
        return {
          ...baseComponent,
          content: data.content || 'New Text',
          style: data.style || {
            fontSize: 16,
            fontFamily: 'Inter, sans-serif',
            fontWeight: 'normal',
            fontStyle: 'normal',
            color: '#000000',
            textAlign: 'left',
            verticalAlign: 'top',
            lineHeight: 1.4
          },
          editable: true
        } as any

      case ElementType.IMAGE:
        return {
          ...baseComponent,
          src: data.src || '',
          alt: data.alt || 'Image',
          style: data.style || {
            objectFit: 'cover',
            objectPosition: 'center'
          }
        } as any

      case ElementType.SHAPE:
        return {
          ...baseComponent,
          shape: data.shape || 'rectangle',
          style: data.style || {
            fill: '#3498db',
            stroke: '#2980b9',
            strokeWidth: 2
          }
        } as any

      case ElementType.CHART:
        return {
          ...baseComponent,
          chartType: data.chartType || 'bar',
          data: data.data || { labels: [], datasets: [] },
          options: data.options || {},
          style: data.style || {}
        } as any

      case ElementType.TABLE:
        return {
          ...baseComponent,
          data: data.data || { headers: [], rows: [] },
          style: data.style || { variant: 'modern' }
        } as any

      default:
        return baseComponent as any
    }
  }

  private applyThemeToComponent(component: VisualComponent, themeData: any): VisualComponent {
    // Theme application logic
    return {
      ...component,
      metadata: {
        ...component.metadata,
        updatedAt: Date.now()
      }
    }
  }

  private applyStyleToComponent(component: VisualComponent, styleData: any): VisualComponent {
    // Style application logic
    return {
      ...component,
      metadata: {
        ...component.metadata,
        updatedAt: Date.now()
      }
    }
  }

  private applyAnimationToComponent(component: VisualComponent, animationData: any): VisualComponent {
    // Animation application logic
    return {
      ...component,
      animation: animationData,
      metadata: {
        ...component.metadata,
        updatedAt: Date.now()
      }
    }
  }

  private recordInHistory(operation: AtomicComponentOperation, result: AtomicOperationResult) {
    const slideId = operation.context.slideId
    const history = this.history.get(slideId) || []
    
    const historyEntry: AtomicOperationHistory = {
      id: result.operationId,
      operation: operation.operation,
      componentType: (operation as any).componentType || 'unknown',
      componentId: result.componentIds[0] || '',
      beforeState: null, // Would need to track this
      afterState: result.changes[0] || null,
      timestamp: result.metadata.timestamp,
      userId: operation.context.userId,
      canUndo: true,
      canRedo: false
    }
    
    history.push(historyEntry)
    this.history.set(slideId, history)
  }

  getHistory(slideId: string): AtomicOperationHistory[] {
    return this.history.get(slideId) || []
  }

  clearHistory(slideId: string): void {
    this.history.delete(slideId)
  }
}

// Export singleton instance
export const atomicProcessor = new AtomicOperationProcessor()

// Utility functions
export function createOperationContext(
  slideId: string,
  slideIndex: number,
  canvasWidth: number,
  canvasHeight: number,
  zoom = 1,
  selectedComponents: string[] = [],
  userId?: string,
  sessionId?: string
): AtomicOperationContext {
  return {
    slideId,
    slideIndex,
    canvasWidth,
    canvasHeight,
    zoom,
    selectedComponents,
    clipboard: [],
    history: [],
    theme: 'default',
    userId,
    sessionId
  }
}

export function isOperationUndoable(operation: AtomicComponentOperation): boolean {
  // All operations except CREATE (slide) are undoable
  return !(operation.operation === AtomicOperation.CREATE && (operation as AtomicCreateOperation).createType === 'slide')
}

export function getOperationDescription(operation: AtomicComponentOperation): string {
  switch (operation.operation) {
    case AtomicOperation.ADD:
      const addOp = operation as AtomicAddOperation
      return `Add ${addOp.componentType} component`
    case AtomicOperation.REMOVE:
      const removeOp = operation as AtomicRemoveOperation
      return `Remove ${removeOp.componentIds.length} component(s)`
    case AtomicOperation.MODIFY:
      return 'Modify component'
    case AtomicOperation.CREATE:
      const createOp = operation as AtomicCreateOperation
      return `Create ${createOp.createType}`
    case AtomicOperation.DELETE:
      const deleteOp = operation as AtomicDeleteOperation
      return `Delete ${deleteOp.deleteType}`
    case AtomicOperation.REORDER:
      const reorderOp = operation as AtomicReorderOperation
      return `Reorder ${reorderOp.reorderType}`
    case AtomicOperation.APPLY:
      const applyOp = operation as AtomicApplyOperation
      return `Apply ${applyOp.applyType}`
    default:
      return 'Unknown operation'
  }
}