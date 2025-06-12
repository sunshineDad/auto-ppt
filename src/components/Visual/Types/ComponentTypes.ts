/**
 * Visual Component Types - Comprehensive Type Definitions
 * 
 * Defines all types for the visual component system with atomic operation support
 */

import { AtomicOperation, ElementType } from '@/types/atoms'

// Base Component Interface
export interface BaseComponent {
  id: string
  type: ElementType
  x: number
  y: number
  width: number
  height: number
  rotation?: number
  opacity?: number
  zIndex?: number
  locked?: boolean
  visible?: boolean
  animation?: ComponentAnimation
  metadata?: ComponentMetadata
}

// Component Animation
export interface ComponentAnimation {
  type: 'fadeIn' | 'slideIn' | 'zoomIn' | 'bounceIn' | 'flipIn' | 'rotateIn'
  duration: number
  delay: number
  easing?: 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'linear'
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse'
  iterations?: number | 'infinite'
}

// Component Metadata
export interface ComponentMetadata {
  createdAt: number
  updatedAt: number
  version: string
  author?: string
  tags?: string[]
  description?: string
}

// Text Component
export interface TextComponent extends BaseComponent {
  type: ElementType.TEXT
  content: string
  style: TextStyle
  editable?: boolean
}

export interface TextStyle {
  fontSize: number
  fontFamily: string
  fontWeight: 'normal' | 'bold' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900'
  fontStyle: 'normal' | 'italic' | 'oblique'
  color: string
  backgroundColor?: string
  textAlign: 'left' | 'center' | 'right' | 'justify'
  verticalAlign: 'top' | 'middle' | 'bottom'
  lineHeight: number
  letterSpacing?: number
  textDecoration?: 'none' | 'underline' | 'overline' | 'line-through'
  textShadow?: string
  padding?: Padding
  border?: Border
}

// Image Component
export interface ImageComponent extends BaseComponent {
  type: ElementType.IMAGE
  src: string
  alt?: string
  style: ImageStyle
}

export interface ImageStyle {
  objectFit: 'contain' | 'cover' | 'fill' | 'scale-down' | 'none'
  objectPosition: string
  borderRadius?: number
  filter?: string
  brightness?: number
  contrast?: number
  saturation?: number
  blur?: number
  shadow?: BoxShadow
  border?: Border
  overlay?: {
    color: string
    opacity: number
    blendMode: string
  }
}

// Shape Component
export interface ShapeComponent extends BaseComponent {
  type: ElementType.SHAPE
  shape: ShapeType
  style: ShapeStyle
}

export type ShapeType = 
  | 'rectangle' 
  | 'circle' 
  | 'ellipse'
  | 'triangle' 
  | 'polygon'
  | 'star'
  | 'arrow'
  | 'diamond'
  | 'hexagon'
  | 'heart'
  | 'cloud'
  | 'speech-bubble'

export interface ShapeStyle {
  fill: string
  stroke?: string
  strokeWidth?: number
  strokeDasharray?: string
  cornerRadius?: number
  gradient?: Gradient
  shadow?: BoxShadow
  pattern?: Pattern
}

// Chart Component
export interface ChartComponent extends BaseComponent {
  type: ElementType.CHART
  chartType: ChartType
  data: ChartData
  options: ChartOptions
  style: ChartStyle
}

export type ChartType = 
  | 'bar' 
  | 'line' 
  | 'pie' 
  | 'doughnut' 
  | 'scatter' 
  | 'area'
  | 'radar'
  | 'bubble'
  | 'polar'
  | 'histogram'

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
  fill?: boolean
  tension?: number
  pointStyle?: string
  pointRadius?: number
}

export interface ChartOptions {
  responsive: boolean
  maintainAspectRatio: boolean
  plugins?: {
    legend?: {
      display: boolean
      position: 'top' | 'bottom' | 'left' | 'right'
      labels?: any
    }
    title?: {
      display: boolean
      text: string
      font?: any
    }
    tooltip?: any
  }
  scales?: any
  animation?: any
}

export interface ChartStyle {
  backgroundColor?: string
  borderRadius?: number
  padding?: Padding
  shadow?: BoxShadow
  border?: Border
}

// Table Component
export interface TableComponent extends BaseComponent {
  type: ElementType.TABLE
  data: TableData
  style: TableStyle
}

export interface TableData {
  headers: string[]
  rows: string[][]
  columnWidths?: number[]
  rowHeights?: number[]
}

export interface TableStyle {
  variant: 'modern' | 'classic' | 'minimal' | 'striped' | 'bordered'
  headerStyle: CellStyle
  cellStyle: CellStyle
  alternateRowColor?: string
  borderCollapse: 'separate' | 'collapse'
  borderSpacing?: number
  shadow?: BoxShadow
}

export interface CellStyle {
  backgroundColor?: string
  color?: string
  fontSize?: number
  fontWeight?: string
  textAlign?: 'left' | 'center' | 'right'
  verticalAlign?: 'top' | 'middle' | 'bottom'
  padding?: Padding
  border?: Border
}

// Icon Component
export interface IconComponent extends BaseComponent {
  type: 'icon'
  iconName: string
  iconSet: 'material' | 'feather' | 'heroicons' | 'lucide' | 'custom'
  style: IconStyle
}

export interface IconStyle {
  color: string
  size: number
  strokeWidth?: number
  fill?: boolean
  gradient?: Gradient
  shadow?: BoxShadow
  rotation?: number
}

// Common Style Interfaces
export interface Padding {
  top: number
  right: number
  bottom: number
  left: number
}

export interface Border {
  width: number
  style: 'solid' | 'dashed' | 'dotted' | 'double' | 'groove' | 'ridge' | 'inset' | 'outset'
  color: string
  radius?: number
}

export interface BoxShadow {
  offsetX: number
  offsetY: number
  blurRadius: number
  spreadRadius?: number
  color: string
  inset?: boolean
}

export interface Gradient {
  type: 'linear' | 'radial' | 'conic'
  direction?: number | string
  stops: GradientStop[]
}

export interface GradientStop {
  color: string
  position: number // 0-100
}

export interface Pattern {
  type: 'dots' | 'lines' | 'grid' | 'diagonal' | 'custom'
  color: string
  size: number
  spacing: number
  rotation?: number
}

// Component State
export interface ComponentState {
  selected: boolean
  editing: boolean
  dragging: boolean
  resizing: boolean
  rotating: boolean
  hovered: boolean
  focused: boolean
  loading: boolean
  error?: string
}

// Component Events
export interface ComponentEvents {
  onSelect: (component: BaseComponent) => void
  onDeselect: (component: BaseComponent) => void
  onEdit: (component: BaseComponent) => void
  onUpdate: (component: BaseComponent, changes: Partial<BaseComponent>) => void
  onDelete: (component: BaseComponent) => void
  onDuplicate: (component: BaseComponent) => void
  onMove: (component: BaseComponent, x: number, y: number) => void
  onResize: (component: BaseComponent, width: number, height: number) => void
  onRotate: (component: BaseComponent, rotation: number) => void
  onZIndexChange: (component: BaseComponent, zIndex: number) => void
}

// Component Factory Types
export interface ComponentFactory {
  createText: (options: Partial<TextComponent>) => TextComponent
  createImage: (options: Partial<ImageComponent>) => ImageComponent
  createShape: (options: Partial<ShapeComponent>) => ShapeComponent
  createChart: (options: Partial<ChartComponent>) => ChartComponent
  createTable: (options: Partial<TableComponent>) => TableComponent
  createIcon: (options: Partial<IconComponent>) => IconComponent
}

// Component Registry
export interface ComponentRegistry {
  register: (type: string, component: any) => void
  unregister: (type: string) => void
  get: (type: string) => any
  getAll: () => Record<string, any>
  has: (type: string) => boolean
}

// Component Theme
export interface ComponentTheme {
  name: string
  colors: {
    primary: string
    secondary: string
    accent: string
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
    shadow: string
  }
  fonts: {
    primary: string
    secondary: string
    monospace: string
  }
  spacing: {
    xs: number
    sm: number
    md: number
    lg: number
    xl: number
  }
  borderRadius: {
    sm: number
    md: number
    lg: number
    full: number
  }
  shadows: {
    sm: string
    md: string
    lg: string
    xl: string
  }
}

// Union Types
export type VisualComponent = 
  | TextComponent 
  | ImageComponent 
  | ShapeComponent 
  | ChartComponent 
  | TableComponent 
  | IconComponent

export type ComponentType = VisualComponent['type']

// Atomic Operation Integration
export interface AtomicComponentOperation {
  operation: AtomicOperation
  componentId: string
  componentType: ComponentType
  data: any
  timestamp: number
  userId?: string
}

export interface ComponentOperationResult {
  success: boolean
  component?: VisualComponent
  error?: string
  changes?: Partial<VisualComponent>
}