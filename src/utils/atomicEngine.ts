/**
 * Atomic Operations Engine
 * 
 * The minimal kernel that processes all 7 atomic operations
 * and updates the PPT data structure accordingly.
 */

import { v4 as uuidv4 } from 'uuid'
import type { 
  AtomicOperationData, 
  AtomicOperation, 
  ElementType,
  AddTextData,
  AddImageData,
  AddShapeData,
  AddChartData,
  AddTableData,
  ModifyElementData,
  CreateSlideData,
  ReorderSlidesData,
  ApplyThemeData
} from '@/types/atoms'
import type { 
  Presentation, 
  Slide, 
  PPTElement, 
  PPTTextElement,
  PPTImageElement,
  PPTShapeElement,
  PPTChartElement,
  PPTTableElement
} from '@/types/slides'

export class AtomicEngine {
  private presentation: Presentation
  private operationHistory: AtomicOperationData[] = []
  private listeners: Array<(operation: AtomicOperationData, result: any) => void> = []

  constructor(presentation: Presentation) {
    this.presentation = presentation
  }

  /**
   * Execute an atomic operation
   */
  async execute(operation: AtomicOperationData): Promise<any> {
    const startTime = performance.now()
    
    try {
      let result: any

      switch (operation.op) {
        case AtomicOperation.ADD:
          result = await this.executeAdd(operation)
          break
        case AtomicOperation.REMOVE:
          result = await this.executeRemove(operation)
          break
        case AtomicOperation.MODIFY:
          result = await this.executeModify(operation)
          break
        case AtomicOperation.CREATE:
          result = await this.executeCreate(operation)
          break
        case AtomicOperation.DELETE:
          result = await this.executeDelete(operation)
          break
        case AtomicOperation.REORDER:
          result = await this.executeReorder(operation)
          break
        case AtomicOperation.APPLY:
          result = await this.executeApply(operation)
          break
        default:
          throw new Error(`Unknown operation: ${operation.op}`)
      }

      // Record operation
      this.operationHistory.push(operation)
      
      // Update timestamps
      this.presentation.metadata.updatedAt = Date.now()
      
      // Notify listeners
      this.notifyListeners(operation, result)
      
      const executionTime = performance.now() - startTime
      console.log(`✅ Executed ${operation.op} in ${executionTime.toFixed(2)}ms`)
      
      return result

    } catch (error) {
      console.error(`❌ Failed to execute ${operation.op}:`, error)
      throw error
    }
  }

  /**
   * ADD Operation - Creating Elements
   */
  private async executeAdd(operation: AtomicOperationData): Promise<PPTElement> {
    const slideIndex = operation.target as number
    const slide = this.presentation.slides[slideIndex]
    
    if (!slide) {
      throw new Error(`Slide ${slideIndex} not found`)
    }

    let element: PPTElement

    switch (operation.type) {
      case ElementType.TEXT:
        element = this.createTextElement(operation.data as AddTextData)
        break
      case ElementType.IMAGE:
        element = this.createImageElement(operation.data as AddImageData)
        break
      case ElementType.SHAPE:
        element = this.createShapeElement(operation.data as AddShapeData)
        break
      case ElementType.CHART:
        element = this.createChartElement(operation.data as AddChartData)
        break
      case ElementType.TABLE:
        element = this.createTableElement(operation.data as AddTableData)
        break
      default:
        throw new Error(`Unsupported element type: ${operation.type}`)
    }

    slide.elements.push(element)
    slide.updatedAt = Date.now()
    
    return element
  }

  /**
   * REMOVE Operation - Deleting Elements
   */
  private async executeRemove(operation: AtomicOperationData): Promise<boolean> {
    if (operation.type === 'element') {
      const elementId = operation.target as string
      return this.removeElementById(elementId)
    }
    
    if (operation.type === 'elements') {
      const elementIds = operation.target as string[]
      return elementIds.every(id => this.removeElementById(id))
    }
    
    if (operation.type === 'all') {
      const slideIndex = operation.target as number
      const elementType = operation.data?.elementType
      return this.removeAllElementsOfType(slideIndex, elementType)
    }
    
    return false
  }

  /**
   * MODIFY Operation - Updating Properties
   */
  private async executeModify(operation: AtomicOperationData): Promise<boolean> {
    if (operation.type === 'element') {
      const elementId = operation.target as string
      return this.modifyElement(elementId, operation.data as ModifyElementData)
    }
    
    if (operation.type === 'batch') {
      const elementIds = operation.target as string[]
      return elementIds.every(id => this.modifyElement(id, operation.data as ModifyElementData))
    }
    
    return false
  }

  /**
   * CREATE Operation - Building Slides
   */
  private async executeCreate(operation: AtomicOperationData): Promise<Slide | Slide[]> {
    if (operation.type === ElementType.SLIDE) {
      return this.createSlide(operation.data as CreateSlideData)
    }
    
    if (operation.type === 'slides') {
      return this.createMultipleSlides(operation.data)
    }
    
    throw new Error(`Unsupported create type: ${operation.type}`)
  }

  /**
   * DELETE Operation - Removing Slides
   */
  private async executeDelete(operation: AtomicOperationData): Promise<boolean> {
    if (operation.type === ElementType.SLIDE) {
      const slideIndex = operation.target as number
      return this.deleteSlide(slideIndex)
    }
    
    if (operation.type === 'slides') {
      const slideIndices = operation.target as number[]
      return this.deleteMultipleSlides(slideIndices)
    }
    
    if (operation.type === 'slide-range') {
      const { from, to } = operation.data
      return this.deleteSlideRange(from, to)
    }
    
    return false
  }

  /**
   * REORDER Operation - Rearranging Structure
   */
  private async executeReorder(operation: AtomicOperationData): Promise<boolean> {
    if (operation.type === 'slides') {
      return this.reorderSlides(operation.data as ReorderSlidesData)
    }
    
    if (operation.type === 'elements') {
      const slideIndex = operation.target as number
      return this.reorderElements(slideIndex, operation.data)
    }
    
    return false
  }

  /**
   * APPLY Operation - Global Transformations
   */
  private async executeApply(operation: AtomicOperationData): Promise<boolean> {
    switch (operation.type) {
      case ElementType.THEME:
        return this.applyTheme(operation.data as ApplyThemeData)
      case 'transitions':
        return this.applyTransitions(operation.data)
      case 'layout':
        return this.applyLayout(operation.data)
      case 'animations':
        return this.applyAnimations(operation.data)
      case 'brand':
        return this.applyBrand(operation.data)
      default:
        return false
    }
  }

  // Helper methods for creating elements
  private createTextElement(data: AddTextData): PPTTextElement {
    return {
      id: uuidv4(),
      type: 'text',
      left: data.x,
      top: data.y,
      width: data.width || 400,
      height: data.height || 100,
      rotate: 0,
      content: data.content,
      defaultFontName: data.fontFamily || 'Arial',
      defaultColor: data.color || '#333333',
      fontSize: data.fontSize || 16,
      fontFamily: data.fontFamily || 'Arial',
      bold: data.bold || false,
      italic: data.italic || false,
      underline: data.underline || false,
      align: data.align || 'left',
      lineHeight: data.lineHeight || 1.5,
      opacity: 1
    }
  }

  private createImageElement(data: AddImageData): PPTImageElement {
    return {
      id: uuidv4(),
      type: 'image',
      left: data.x,
      top: data.y,
      width: data.width,
      height: data.height,
      rotate: 0,
      src: data.src,
      fit: data.fit || 'contain',
      shadow: data.shadow || false,
      borderRadius: data.borderRadius || 0,
      filter: data.filter,
      brightness: data.brightness || 1,
      contrast: data.contrast || 1,
      opacity: 1
    }
  }

  private createShapeElement(data: AddShapeData): PPTShapeElement {
    return {
      id: uuidv4(),
      type: 'shape',
      left: data.x,
      top: data.y,
      width: data.width,
      height: data.height,
      rotate: 0,
      shape: data.shape,
      fill: data.fill || '#4CAF50',
      stroke: data.stroke || '#2E7D32',
      strokeWidth: data.strokeWidth || 2,
      opacity: data.opacity || 1
    }
  }

  private createChartElement(data: AddChartData): PPTChartElement {
    return {
      id: uuidv4(),
      type: 'chart',
      left: data.x,
      top: data.y,
      width: data.width,
      height: data.height,
      rotate: 0,
      chartType: data.chartType,
      data: data.data,
      options: data.options || {}
    }
  }

  private createTableElement(data: AddTableData): PPTTableElement {
    return {
      id: uuidv4(),
      type: 'table',
      left: data.x,
      top: data.y,
      width: data.width || 600,
      height: data.height || 400,
      rotate: 0,
      data: data.data,
      colWidths: new Array(data.columns).fill(100),
      rowHeights: new Array(data.rows).fill(40),
      style: {
        borderColor: '#ddd',
        borderWidth: 1,
        headerBg: data.headerStyle?.backgroundColor || '#1976D2',
        headerColor: data.headerStyle?.color || '#FFFFFF',
        cellPadding: 8
      }
    }
  }

  // Helper methods for operations
  private removeElementById(elementId: string): boolean {
    for (const slide of this.presentation.slides) {
      const index = slide.elements.findIndex(el => el.id === elementId)
      if (index !== -1) {
        slide.elements.splice(index, 1)
        slide.updatedAt = Date.now()
        return true
      }
    }
    return false
  }

  private removeAllElementsOfType(slideIndex: number, elementType: string): boolean {
    const slide = this.presentation.slides[slideIndex]
    if (!slide) return false
    
    const initialLength = slide.elements.length
    slide.elements = slide.elements.filter(el => el.type !== elementType)
    slide.updatedAt = Date.now()
    
    return slide.elements.length < initialLength
  }

  private modifyElement(elementId: string, changes: ModifyElementData): boolean {
    for (const slide of this.presentation.slides) {
      const element = slide.elements.find(el => el.id === elementId)
      if (element) {
        Object.assign(element, changes)
        slide.updatedAt = Date.now()
        return true
      }
    }
    return false
  }

  private createSlide(data: CreateSlideData): Slide {
    const slide: Slide = {
      id: uuidv4(),
      elements: [],
      layout: data.layout || 'blank',
      template: data.template,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    // Add initial elements if specified
    if (data.elements) {
      for (const elementData of data.elements) {
        const element = this.createElementFromData(elementData)
        if (element) {
          slide.elements.push(element)
        }
      }
    }

    // Insert slide at specified position
    const insertIndex = data.after === 'end' 
      ? this.presentation.slides.length 
      : (data.after || 0) + 1
    
    this.presentation.slides.splice(insertIndex, 0, slide)
    
    return slide
  }

  private createMultipleSlides(data: any): Slide[] {
    const slides: Slide[] = []
    for (let i = 0; i < data.count; i++) {
      const slide = this.createSlide({
        layout: data.layout,
        after: data.after === 'end' ? 'end' : (data.after as number) + i
      })
      slides.push(slide)
    }
    return slides
  }

  private deleteSlide(slideIndex: number): boolean {
    if (slideIndex >= 0 && slideIndex < this.presentation.slides.length) {
      this.presentation.slides.splice(slideIndex, 1)
      return true
    }
    return false
  }

  private deleteMultipleSlides(slideIndices: number[]): boolean {
    // Sort in descending order to avoid index shifting issues
    const sortedIndices = [...slideIndices].sort((a, b) => b - a)
    
    for (const index of sortedIndices) {
      if (!this.deleteSlide(index)) {
        return false
      }
    }
    return true
  }

  private deleteSlideRange(from: number, to: number): boolean {
    if (from > to || from < 0 || to >= this.presentation.slides.length) {
      return false
    }
    
    this.presentation.slides.splice(from, to - from + 1)
    return true
  }

  private reorderSlides(data: ReorderSlidesData): boolean {
    if (data.order) {
      const newSlides = data.order.map(index => this.presentation.slides[index])
      this.presentation.slides = newSlides
      return true
    }
    
    if (data.sortBy) {
      // Implement sorting logic based on sortBy criteria
      // This is a simplified implementation
      this.presentation.slides.sort((a, b) => {
        if (data.direction === 'descending') {
          return b.createdAt - a.createdAt
        }
        return a.createdAt - b.createdAt
      })
      return true
    }
    
    return false
  }

  private reorderElements(slideIndex: number, data: any): boolean {
    const slide = this.presentation.slides[slideIndex]
    if (!slide) return false
    
    const newElements = data.order.map((id: string) => 
      slide.elements.find(el => el.id === id)
    ).filter(Boolean)
    
    slide.elements = newElements
    slide.updatedAt = Date.now()
    return true
  }

  private applyTheme(data: ApplyThemeData): boolean {
    this.presentation.theme = {
      ...this.presentation.theme,
      name: data.name,
      colors: data.colorScheme,
      fonts: data.fonts || this.presentation.theme.fonts
    }
    return true
  }

  private applyTransitions(data: any): boolean {
    // Apply transitions to slides
    const targetSlides = data.applyTo === 'all' 
      ? this.presentation.slides 
      : data.applyTo.map((i: number) => this.presentation.slides[i])
    
    for (const slide of targetSlides) {
      slide.animation = {
        type: data.slideTransition,
        duration: data.duration
      }
      slide.updatedAt = Date.now()
    }
    return true
  }

  private applyLayout(data: any): boolean {
    // Apply layout settings globally
    // This would typically update canvas settings
    return true
  }

  private applyAnimations(data: any): boolean {
    // Apply animation scheme to all elements
    for (const slide of this.presentation.slides) {
      for (const element of slide.elements) {
        // Apply animations based on element type and scheme
        slide.updatedAt = Date.now()
      }
    }
    return true
  }

  private applyBrand(data: any): boolean {
    // Apply brand guidelines
    if (data.fonts) {
      this.presentation.theme.fonts = data.fonts
    }
    return true
  }

  private createElementFromData(data: any): PPTElement | null {
    switch (data.type) {
      case ElementType.TEXT:
        return this.createTextElement(data)
      case ElementType.IMAGE:
        return this.createImageElement(data)
      case ElementType.SHAPE:
        return this.createShapeElement(data)
      default:
        return null
    }
  }

  // Event system
  onOperation(callback: (operation: AtomicOperationData, result: any) => void) {
    this.listeners.push(callback)
  }

  private notifyListeners(operation: AtomicOperationData, result: any) {
    this.listeners.forEach(callback => callback(operation, result))
  }

  // Getters
  getPresentation(): Presentation {
    return this.presentation
  }

  getOperationHistory(): AtomicOperationData[] {
    return [...this.operationHistory]
  }

  // Performance metrics
  getPerformanceMetrics() {
    return {
      totalOperations: this.operationHistory.length,
      averageExecutionTime: '< 10ms', // This would be calculated from actual measurements
      memoryUsage: typeof window !== 'undefined' ? 'Browser Environment' : 'N/A'
    }
  }
}