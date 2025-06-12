/**
 * Visual Component System - Comprehensive Component Library
 * 
 * This module provides a standardized, atomic-operation-compatible
 * visual component system for the AI-PPT application.
 */

// Core Visual Components
export { default as VisualChart } from './Charts/VisualChart.vue'
export { default as VisualShape } from './Shapes/VisualShape.vue'
export { default as VisualTable } from './Tables/VisualTable.vue'
export { default as VisualText } from './Text/VisualText.vue'
export { default as VisualImage } from './Images/VisualImage.vue'
export { default as VisualIcon } from './Icons/VisualIcon.vue'

// Component Factories
export { default as ComponentFactory } from './Core/ComponentFactory.vue'
export { default as AtomicRenderer } from './Core/AtomicRenderer.vue'

// Drag & Drop System
export { default as DragDropManager } from './DragDrop/DragDropManager.vue'
export { default as DropZone } from './DragDrop/DropZone.vue'
export { default as DragHandle } from './DragDrop/DragHandle.vue'

// Style System
export * from './Styles/ComponentStyles'
export * from './Styles/ThemeSystem'

// Types and Interfaces
export * from './Types/ComponentTypes'
export * from './Types/AtomicTypes'

// Utilities
export * from './Utils/ComponentUtils'
export * from './Utils/AtomicOperations'