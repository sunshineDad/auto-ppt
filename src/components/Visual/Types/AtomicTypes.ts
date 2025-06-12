/**
 * Atomic Types - Integration with Atomic Operation System
 * 
 * Defines types for seamless integration with the 7 atomic operations
 */

import { AtomicOperation, ElementType } from '@/types/atoms'
import { VisualComponent, ComponentType } from './ComponentTypes'

// Atomic Operation Context
export interface AtomicOperationContext {
  slideId: string
  slideIndex: number
  canvasWidth: number
  canvasHeight: number
  zoom: number
  selectedComponents: string[]
  clipboard: VisualComponent[]
  history: AtomicOperationHistory[]
  theme: string
  userId?: string
  sessionId?: string
}

// Atomic Operation History
export interface AtomicOperationHistory {
  id: string
  operation: AtomicOperation
  componentType: ComponentType
  componentId: string
  beforeState: VisualComponent | null
  afterState: VisualComponent | null
  timestamp: number
  userId?: string
  canUndo: boolean
  canRedo: boolean
}

// ADD Operation Types
export interface AtomicAddOperation {
  operation: AtomicOperation.ADD
  componentType: ComponentType
  data: AddComponentData
  position: { x: number; y: number }
  context: AtomicOperationContext
}

export type AddComponentData = 
  | AddTextData
  | AddImageData
  | AddShapeData
  | AddChartData
  | AddTableData
  | AddIconData

export interface AddTextData {
  content: string
  style?: Partial<import('./ComponentTypes').TextStyle>
  width?: number
  height?: number
}

export interface AddImageData {
  src: string
  alt?: string
  style?: Partial<import('./ComponentTypes').ImageStyle>
  width?: number
  height?: number
}

export interface AddShapeData {
  shape: import('./ComponentTypes').ShapeType
  style?: Partial<import('./ComponentTypes').ShapeStyle>
  width?: number
  height?: number
}

export interface AddChartData {
  chartType: import('./ComponentTypes').ChartType
  data: import('./ComponentTypes').ChartData
  options?: Partial<import('./ComponentTypes').ChartOptions>
  style?: Partial<import('./ComponentTypes').ChartStyle>
  width?: number
  height?: number
}

export interface AddTableData {
  data: import('./ComponentTypes').TableData
  style?: Partial<import('./ComponentTypes').TableStyle>
  width?: number
  height?: number
}

export interface AddIconData {
  iconName: string
  iconSet: import('./ComponentTypes').IconComponent['iconSet']
  style?: Partial<import('./ComponentTypes').IconStyle>
  width?: number
  height?: number
}

// REMOVE Operation Types
export interface AtomicRemoveOperation {
  operation: AtomicOperation.REMOVE
  componentIds: string[]
  context: AtomicOperationContext
}

// MODIFY Operation Types
export interface AtomicModifyOperation {
  operation: AtomicOperation.MODIFY
  componentId: string
  changes: ModifyComponentData
  context: AtomicOperationContext
}

export interface ModifyComponentData {
  position?: { x: number; y: number }
  size?: { width: number; height: number }
  rotation?: number
  opacity?: number
  zIndex?: number
  style?: any
  content?: string
  data?: any
  animation?: import('./ComponentTypes').ComponentAnimation
  metadata?: Partial<import('./ComponentTypes').ComponentMetadata>
}

// CREATE Operation Types
export interface AtomicCreateOperation {
  operation: AtomicOperation.CREATE
  createType: 'slide' | 'template' | 'group'
  data: CreateOperationData
  context: AtomicOperationContext
}

export type CreateOperationData = 
  | CreateSlideData
  | CreateTemplateData
  | CreateGroupData

export interface CreateSlideData {
  layout: 'blank' | 'title' | 'title-content' | 'two-column' | 'comparison'
  template?: string
  components?: VisualComponent[]
  position?: 'before' | 'after' | 'end'
  targetSlideIndex?: number
}

export interface CreateTemplateData {
  name: string
  description?: string
  components: VisualComponent[]
  layout: string
  theme?: string
  tags?: string[]
}

export interface CreateGroupData {
  componentIds: string[]
  name?: string
  locked?: boolean
}

// DELETE Operation Types
export interface AtomicDeleteOperation {
  operation: AtomicOperation.DELETE
  deleteType: 'component' | 'slide' | 'group'
  targetIds: string[]
  context: AtomicOperationContext
}

// REORDER Operation Types
export interface AtomicReorderOperation {
  operation: AtomicOperation.REORDER
  reorderType: 'components' | 'slides' | 'layers'
  data: ReorderOperationData
  context: AtomicOperationContext
}

export type ReorderOperationData = 
  | ReorderComponentsData
  | ReorderSlidesData
  | ReorderLayersData

export interface ReorderComponentsData {
  componentIds: string[]
  newOrder: string[]
  arrangement: 'horizontal' | 'vertical' | 'grid' | 'custom'
}

export interface ReorderSlidesData {
  slideIds: string[]
  newOrder: string[]
}

export interface ReorderLayersData {
  componentIds: string[]
  zIndexChanges: Record<string, number>
}

// APPLY Operation Types
export interface AtomicApplyOperation {
  operation: AtomicOperation.APPLY
  applyType: 'theme' | 'style' | 'animation' | 'layout' | 'template'
  data: ApplyOperationData
  targets: string[] // component IDs or 'all'
  context: AtomicOperationContext
}

export type ApplyOperationData = 
  | ApplyThemeData
  | ApplyStyleData
  | ApplyAnimationData
  | ApplyLayoutData
  | ApplyTemplateData

export interface ApplyThemeData {
  theme: import('./ComponentTypes').ComponentTheme
  preserveContent: boolean
  preserveLayout: boolean
}

export interface ApplyStyleData {
  styleType: 'text' | 'shape' | 'image' | 'chart' | 'table' | 'icon'
  style: any
  merge: boolean
}

export interface ApplyAnimationData {
  animations: import('./ComponentTypes').ComponentAnimation[]
  timing: 'sequential' | 'parallel' | 'staggered'
  staggerDelay?: number
}

export interface ApplyLayoutData {
  layout: 'grid' | 'flex' | 'absolute' | 'flow'
  parameters: any
  preserveContent: boolean
}

export interface ApplyTemplateData {
  templateId: string
  variables?: Record<string, any>
  preserveContent: boolean
}

// Operation Results
export interface AtomicOperationResult {
  success: boolean
  operationId: string
  operation: AtomicOperation
  componentIds: string[]
  changes: VisualComponent[]
  error?: string
  warnings?: string[]
  metadata: {
    timestamp: number
    duration: number
    userId?: string
    sessionId?: string
  }
}

// Operation Validation
export interface OperationValidation {
  valid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

export interface ValidationError {
  code: string
  message: string
  field?: string
  value?: any
}

export interface ValidationWarning {
  code: string
  message: string
  suggestion?: string
}

// Operation Batch
export interface AtomicOperationBatch {
  id: string
  operations: AtomicComponentOperation[]
  context: AtomicOperationContext
  atomic: boolean // all operations must succeed or all fail
  parallel: boolean // operations can be executed in parallel
}

export type AtomicComponentOperation = 
  | AtomicAddOperation
  | AtomicRemoveOperation
  | AtomicModifyOperation
  | AtomicCreateOperation
  | AtomicDeleteOperation
  | AtomicReorderOperation
  | AtomicApplyOperation

// Operation Processor
export interface AtomicOperationProcessor {
  process: (operation: AtomicComponentOperation) => Promise<AtomicOperationResult>
  processBatch: (batch: AtomicOperationBatch) => Promise<AtomicOperationResult[]>
  validate: (operation: AtomicComponentOperation) => OperationValidation
  undo: (operationId: string) => Promise<AtomicOperationResult>
  redo: (operationId: string) => Promise<AtomicOperationResult>
  getHistory: (slideId: string) => AtomicOperationHistory[]
  clearHistory: (slideId: string) => void
}

// Operation Events
export interface AtomicOperationEvents {
  onOperationStart: (operation: AtomicComponentOperation) => void
  onOperationComplete: (result: AtomicOperationResult) => void
  onOperationError: (operation: AtomicComponentOperation, error: Error) => void
  onBatchStart: (batch: AtomicOperationBatch) => void
  onBatchComplete: (results: AtomicOperationResult[]) => void
  onBatchError: (batch: AtomicOperationBatch, error: Error) => void
  onUndo: (operationId: string) => void
  onRedo: (operationId: string) => void
}

// Operation Middleware
export interface OperationMiddleware {
  name: string
  priority: number
  beforeOperation?: (operation: AtomicComponentOperation) => AtomicComponentOperation | null
  afterOperation?: (operation: AtomicComponentOperation, result: AtomicOperationResult) => AtomicOperationResult
  onError?: (operation: AtomicComponentOperation, error: Error) => Error | null
}

// Operation Configuration
export interface AtomicOperationConfig {
  enableHistory: boolean
  maxHistorySize: number
  enableValidation: boolean
  enableMiddleware: boolean
  enableBatching: boolean
  enableParallelProcessing: boolean
  defaultTimeout: number
  retryAttempts: number
  retryDelay: number
}