/**
 * The 7 Atomic Operations for PPT Generation
 * 
 * These primitives form the foundation of all presentation operations.
 * Complex presentations emerge from sequences of these simple atoms.
 */

export enum AtomicOperation {
  ADD = 'ADD',
  REMOVE = 'REMOVE', 
  MODIFY = 'MODIFY',
  CREATE = 'CREATE',
  DELETE = 'DELETE',
  REORDER = 'REORDER',
  APPLY = 'APPLY'
}

export enum ElementType {
  TEXT = 'text',
  IMAGE = 'image',
  SHAPE = 'shape',
  CHART = 'chart',
  TABLE = 'table',
  VIDEO = 'video',
  AUDIO = 'audio',
  SLIDE = 'slide',
  THEME = 'theme',
  TEMPLATE = 'template',
  ANIMATION = 'animation'
}

/**
 * Unified Atom Format - Mathematical structure for all operations
 */
export interface AtomicOperationData {
  op: AtomicOperation
  type: ElementType | string
  target: string | number | string[] | number[]
  data?: Record<string, any>
  timestamp: number
  userId?: string
  sessionId?: string
}

/**
 * ADD Operation Data Structures
 */
export interface AddTextData {
  content: string
  x: number
  y: number
  width?: number
  height?: number
  style?: 'heading' | 'subtitle' | 'bullet' | 'caption' | 'body'
  fontSize?: number
  fontFamily?: string
  color?: string
  align?: 'left' | 'center' | 'right'
  bold?: boolean
  italic?: boolean
  underline?: boolean
  lineHeight?: number
  indent?: number
}

export interface AddImageData {
  src: string
  x: number
  y: number
  width: number
  height: number
  fit?: 'contain' | 'cover' | 'fill'
  shadow?: boolean
  borderRadius?: number
  filter?: string
  brightness?: number
  contrast?: number
  crop?: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface AddShapeData {
  shape: 'rectangle' | 'circle' | 'triangle' | 'arrow' | 'star' | 'polygon'
  x: number
  y: number
  width: number
  height: number
  fill?: string
  stroke?: string
  strokeWidth?: number
  cornerRadius?: number
  opacity?: number
}

export interface AddChartData {
  chartType: 'bar' | 'line' | 'pie' | 'doughnut' | 'scatter' | 'area'
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor?: string | string[]
      borderColor?: string | string[]
      borderWidth?: number
    }>
  }
  x: number
  y: number
  width: number
  height: number
  options?: Record<string, any>
}

export interface AddTableData {
  rows: number
  columns: number
  data: string[][]
  x: number
  y: number
  width?: number
  height?: number
  style?: 'modern' | 'classic' | 'minimal'
  headerStyle?: {
    backgroundColor?: string
    color?: string
    bold?: boolean
  }
  cellStyle?: {
    padding?: number
    borderColor?: string
    borderWidth?: number
  }
}

/**
 * MODIFY Operation Data Structures
 */
export interface ModifyElementData {
  content?: string
  x?: number
  y?: number
  width?: number
  height?: number
  rotation?: number
  opacity?: number
  fontSize?: number
  color?: string
  backgroundColor?: string
  bold?: boolean
  italic?: boolean
  underline?: boolean
  align?: 'left' | 'center' | 'right'
  animation?: {
    type: 'fadeIn' | 'slideIn' | 'zoomIn' | 'bounceIn'
    duration: number
    delay: number
  }
}

export interface BatchModifyData {
  targets: string[]
  changes: ModifyElementData
  align?: 'left' | 'center' | 'right'
  verticalAlign?: 'top' | 'middle' | 'bottom'
  spacing?: number
}

/**
 * CREATE Operation Data Structures
 */
export interface CreateSlideData {
  after?: number | 'end'
  layout?: 'blank' | 'title' | 'title-content' | 'two-column' | 'comparison'
  template?: string
  variables?: Record<string, string>
  elements?: Array<{
    type: ElementType
    content?: string
    style?: string
    x: number
    y: number
    width?: number
    height?: number
  }>
}

export interface CreateMultipleSlidesData {
  count: number
  layout: string
  after: number | 'end'
}

/**
 * DELETE Operation Data Structures
 */
export interface DeleteSlideRangeData {
  from: number
  to: number
}

/**
 * REORDER Operation Data Structures
 */
export interface ReorderSlidesData {
  order?: number[]
  sortBy?: 'title' | 'date' | 'template' | 'custom'
  direction?: 'ascending' | 'descending'
}

export interface ReorderElementsData {
  slideIndex: number
  order: string[]
  arrangement: 'z-index' | 'horizontal' | 'vertical'
}

/**
 * APPLY Operation Data Structures
 */
export interface ApplyThemeData {
  name: string
  colorScheme: {
    primary: string
    secondary: string
    background: string
    text: string
    accent?: string
  }
  fonts?: {
    heading: string
    body: string
  }
}

export interface ApplyTransitionsData {
  slideTransition: 'fade' | 'slide' | 'zoom' | 'flip' | 'cube'
  duration: number
  applyTo: 'all' | number[]
}

export interface ApplyLayoutData {
  grid: {
    columns: number
    gutter: number
    margin: number
  }
  guides: boolean
  snap: boolean
}

export interface ApplyAnimationsData {
  scheme: 'professional' | 'smooth-fade' | 'dynamic' | 'minimal'
  timing: {
    text: { duration: number; delay: number }
    images: { duration: number; delay: number }
    shapes: { duration: number; delay: number }
  }
}

export interface ApplyBrandData {
  logo?: string
  fonts: {
    heading: string
    body: string
  }
  footer?: string
  watermark?: {
    enabled: boolean
    opacity: number
    text?: string
  }
}

/**
 * Operation Sequence for Complex Presentations
 */
export interface OperationSequence {
  id: string
  name: string
  description: string
  atoms: AtomicOperationData[]
  createdAt: number
  tags: string[]
}

/**
 * AI Learning Context
 */
export interface AIContext {
  currentSlide: {
    index: number
    elements: any[]
    layout: string
  }
  presentation: {
    totalSlides: number
    theme: string
    purpose: string
  }
  userBehavior: {
    recentOperations: AtomicOperationData[]
    patterns: string[]
    preferences: Record<string, any>
  }
}

/**
 * Atom Prediction Result
 */
export interface AtomPrediction {
  atom: AtomicOperationData
  confidence: number
  reasoning: string
  alternatives: AtomicOperationData[]
}