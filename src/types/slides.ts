/**
 * Unified PPT Data Structure
 * Based on PPTist architecture with atomic operation support
 */

export enum ElementTypes {
  TEXT = 'text',
  IMAGE = 'image',
  SHAPE = 'shape',
  LINE = 'line',
  CHART = 'chart',
  TABLE = 'table',
  VIDEO = 'video',
  AUDIO = 'audio'
}

/**
 * Element Base Properties
 */
export interface PPTBaseElement {
  id: string
  left: number
  top: number
  width: number
  height: number
  rotate: number
  lock?: boolean
  groupId?: string
  name?: string
  zIndex?: number
}

/**
 * Text Element
 */
export interface PPTTextElement extends PPTBaseElement {
  type: 'text'
  content: string
  defaultFontName: string
  defaultColor: string
  fontSize?: number
  fontFamily?: string
  bold?: boolean
  italic?: boolean
  underline?: boolean
  align?: 'left' | 'center' | 'right'
  lineHeight?: number
  opacity?: number
  shadow?: boolean
  fill?: string
  outline?: {
    width: number
    color: string
    style: 'solid' | 'dashed'
  }
}

/**
 * Image Element
 */
export interface PPTImageElement extends PPTBaseElement {
  type: 'image'
  src: string
  fit?: 'contain' | 'cover' | 'fill'
  flipH?: boolean
  flipV?: boolean
  shadow?: boolean
  borderRadius?: number
  filter?: string
  brightness?: number
  contrast?: number
  opacity?: number
}

/**
 * Shape Element
 */
export interface PPTShapeElement extends PPTBaseElement {
  type: 'shape'
  shape: string
  fill?: string
  stroke?: string
  strokeWidth?: number
  opacity?: number
  flipH?: boolean
  flipV?: boolean
  path?: string
  viewBox?: string
}

/**
 * Chart Element
 */
export interface PPTChartElement extends PPTBaseElement {
  type: 'chart'
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
  options?: Record<string, any>
  theme?: string
}

/**
 * Table Element
 */
export interface PPTTableElement extends PPTBaseElement {
  type: 'table'
  data: string[][]
  colWidths: number[]
  rowHeights: number[]
  style?: {
    borderColor?: string
    borderWidth?: number
    headerBg?: string
    headerColor?: string
    cellPadding?: number
  }
  theme?: string
}

/**
 * Video Element
 */
export interface PPTVideoElement extends PPTBaseElement {
  type: 'video'
  src: string
  poster?: string
  autoplay?: boolean
  loop?: boolean
  controls?: boolean
}

/**
 * Audio Element
 */
export interface PPTAudioElement extends PPTBaseElement {
  type: 'audio'
  src: string
  autoplay?: boolean
  loop?: boolean
  iconColor?: string
}

/**
 * Union type for all elements
 */
export type PPTElement = 
  | PPTTextElement 
  | PPTImageElement 
  | PPTShapeElement 
  | PPTChartElement 
  | PPTTableElement 
  | PPTVideoElement 
  | PPTAudioElement

/**
 * Slide Background
 */
export interface SlideBackground {
  type: 'solid' | 'gradient' | 'image'
  color?: string
  gradient?: {
    type: 'linear' | 'radial'
    colors: Array<{ pos: number; color: string }>
    rotate?: number
  }
  image?: {
    src: string
    size: 'cover' | 'contain' | 'repeat'
    position: string
  }
}

/**
 * Slide Animation
 */
export interface SlideAnimation {
  type: 'fade' | 'slide' | 'zoom' | 'flip' | 'cube'
  duration: number
  direction?: 'left' | 'right' | 'up' | 'down'
}

/**
 * Slide Definition
 */
export interface Slide {
  id: string
  elements: PPTElement[]
  background?: SlideBackground
  animation?: SlideAnimation
  notes?: string
  layout?: string
  template?: string
  createdAt: number
  updatedAt: number
}

/**
 * Presentation Theme
 */
export interface PresentationTheme {
  id: string
  name: string
  colors: {
    primary: string
    secondary: string
    background: string
    text: string
    accent: string
  }
  fonts: {
    heading: string
    body: string
  }
  layouts: Record<string, any>
  templates: Record<string, any>
}

/**
 * Presentation Definition
 */
export interface Presentation {
  id: string
  title: string
  slides: Slide[]
  theme: PresentationTheme
  settings: {
    width: number
    height: number
    ratio: string
  }
  metadata: {
    author: string
    createdAt: number
    updatedAt: number
    version: string
    tags: string[]
  }
}

/**
 * Canvas State
 */
export interface CanvasState {
  zoom: number
  offsetX: number
  offsetY: number
  selectedElements: string[]
  activeSlide: number
  gridVisible: boolean
  guidesVisible: boolean
  snapToGrid: boolean
}

/**
 * Editor State
 */
export interface EditorState {
  presentation: Presentation
  canvas: CanvasState
  history: {
    past: any[]
    present: any
    future: any[]
  }
  clipboard: PPTElement[]
  isPlaying: boolean
  isFullscreen: boolean
}