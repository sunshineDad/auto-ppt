<template>
  <div class="visual-table" :class="tableClasses" :style="tableContainerStyle">
    <table class="table-element" :style="tableStyle">
      <!-- Table Header -->
      <thead v-if="component.data.headers.length > 0">
        <tr>
          <th
            v-for="(header, colIndex) in component.data.headers"
            :key="`header-${colIndex}`"
            :style="getHeaderCellStyle(colIndex)"
            :contenteditable="editing"
            @blur="handleHeaderEdit(colIndex, $event)"
            @keydown="handleKeydown"
          >
            {{ header }}
          </th>
        </tr>
      </thead>
      
      <!-- Table Body -->
      <tbody>
        <tr
          v-for="(row, rowIndex) in component.data.rows"
          :key="`row-${rowIndex}`"
          :class="getRowClass(rowIndex)"
        >
          <td
            v-for="(cell, colIndex) in row"
            :key="`cell-${rowIndex}-${colIndex}`"
            :style="getCellStyle(rowIndex, colIndex)"
            :contenteditable="editing"
            @blur="handleCellEdit(rowIndex, colIndex, $event)"
            @keydown="handleKeydown"
            @dblclick="startEditing"
          >
            {{ cell }}
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Table Controls (when selected) -->
    <div v-if="selected && !editing" class="table-controls">
      <button @click="addRow" class="control-button" title="Add Row">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
      <button @click="addColumn" class="control-button" title="Add Column">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
      </button>
      <button @click="removeRow" class="control-button" title="Remove Row" :disabled="component.data.rows.length <= 1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
      <button @click="removeColumn" class="control-button" title="Remove Column" :disabled="component.data.headers.length <= 1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="9" y1="9" x2="15" y2="15"></line>
          <line x1="15" y1="9" x2="9" y2="15"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TableComponent } from '../Types/ComponentTypes'

interface Props {
  component: TableComponent
  selected?: boolean
  editing?: boolean
}

interface Emits {
  (e: 'update', component: TableComponent, changes: Partial<TableComponent>): void
  (e: 'edit', component: TableComponent): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  editing: false
})

const emit = defineEmits<Emits>()

const isEditing = ref(false)

// Computed properties
const tableClasses = computed(() => ({
  'visual-table': true,
  'selected': props.selected,
  'editing': props.editing || isEditing.value,
  [`variant-${props.component.style.variant}`]: true
}))

const tableContainerStyle = computed(() => ({
  width: '100%',
  height: '100%',
  position: 'relative',
  overflow: 'auto',
  boxShadow: props.component.style.shadow ? buildShadowString(props.component.style.shadow) : 'none'
}))

const tableStyle = computed(() => ({
  width: '100%',
  height: '100%',
  borderCollapse: props.component.style.borderCollapse,
  borderSpacing: props.component.style.borderSpacing ? `${props.component.style.borderSpacing}px` : '0',
  fontFamily: 'inherit',
  fontSize: '14px'
}))

// Helper functions
function buildShadowString(shadow: NonNullable<TableComponent['style']['shadow']>) {
  return `${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.spreadRadius || 0}px ${shadow.color}${shadow.inset ? ' inset' : ''}`
}

function buildPaddingString(padding: NonNullable<TableComponent['style']['headerStyle']['padding']>) {
  return `${padding.top}px ${padding.right}px ${padding.bottom}px ${padding.left}px`
}

function buildBorderString(border: NonNullable<TableComponent['style']['headerStyle']['border']>) {
  return `${border.width}px ${border.style} ${border.color}`
}

function getRowClass(rowIndex: number) {
  return {
    'table-row': true,
    'alternate-row': props.component.style.alternateRowColor && rowIndex % 2 === 1
  }
}

function getHeaderCellStyle(colIndex: number) {
  const style = props.component.style.headerStyle
  const columnWidth = props.component.data.columnWidths?.[colIndex]
  
  return {
    backgroundColor: style.backgroundColor || '#f8f9fa',
    color: style.color || '#2c3e50',
    fontSize: style.fontSize ? `${style.fontSize}px` : '14px',
    fontWeight: style.fontWeight || 'bold',
    textAlign: style.textAlign || 'left',
    verticalAlign: style.verticalAlign || 'middle',
    padding: style.padding ? buildPaddingString(style.padding) : '12px 16px',
    border: style.border ? buildBorderString(style.border) : '1px solid #dee2e6',
    width: columnWidth ? `${columnWidth}px` : 'auto',
    minWidth: '80px',
    outline: 'none',
    cursor: props.editing || isEditing.value ? 'text' : 'default'
  }
}

function getCellStyle(rowIndex: number, colIndex: number) {
  const style = props.component.style.cellStyle
  const columnWidth = props.component.data.columnWidths?.[colIndex]
  const rowHeight = props.component.data.rowHeights?.[rowIndex]
  const isAlternateRow = props.component.style.alternateRowColor && rowIndex % 2 === 1
  
  return {
    backgroundColor: isAlternateRow ? 
      props.component.style.alternateRowColor : 
      (style.backgroundColor || '#ffffff'),
    color: style.color || '#2c3e50',
    fontSize: style.fontSize ? `${style.fontSize}px` : '14px',
    fontWeight: style.fontWeight || 'normal',
    textAlign: style.textAlign || 'left',
    verticalAlign: style.verticalAlign || 'middle',
    padding: style.padding ? buildPaddingString(style.padding) : '8px 16px',
    border: style.border ? buildBorderString(style.border) : '1px solid #dee2e6',
    width: columnWidth ? `${columnWidth}px` : 'auto',
    height: rowHeight ? `${rowHeight}px` : 'auto',
    minWidth: '80px',
    minHeight: '32px',
    outline: 'none',
    cursor: props.editing || isEditing.value ? 'text' : 'default',
    transition: 'background-color 0.2s ease'
  }
}

// Event handlers
function handleHeaderEdit(colIndex: number, event: Event) {
  const target = event.target as HTMLElement
  const newValue = target.textContent || ''
  
  const newHeaders = [...props.component.data.headers]
  newHeaders[colIndex] = newValue
  
  emit('update', props.component, {
    data: {
      ...props.component.data,
      headers: newHeaders
    }
  })
}

function handleCellEdit(rowIndex: number, colIndex: number, event: Event) {
  const target = event.target as HTMLElement
  const newValue = target.textContent || ''
  
  const newRows = [...props.component.data.rows]
  newRows[rowIndex] = [...newRows[rowIndex]]
  newRows[rowIndex][colIndex] = newValue
  
  emit('update', props.component, {
    data: {
      ...props.component.data,
      rows: newRows
    }
  })
}

function handleKeydown(event: KeyboardEvent) {
  if (props.editing || isEditing.value) {
    if (event.key === 'Escape') {
      event.preventDefault()
      ;(event.target as HTMLElement).blur()
    } else if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      ;(event.target as HTMLElement).blur()
    }
  }
}

function startEditing() {
  if (!props.editing) {
    isEditing.value = true
    emit('edit', props.component)
  }
}

// Table manipulation functions
function addRow() {
  const newRow = new Array(props.component.data.headers.length).fill('New Cell')
  const newRows = [...props.component.data.rows, newRow]
  
  emit('update', props.component, {
    data: {
      ...props.component.data,
      rows: newRows
    }
  })
}

function addColumn() {
  const newHeaders = [...props.component.data.headers, 'New Column']
  const newRows = props.component.data.rows.map(row => [...row, 'New Cell'])
  
  emit('update', props.component, {
    data: {
      ...props.component.data,
      headers: newHeaders,
      rows: newRows
    }
  })
}

function removeRow() {
  if (props.component.data.rows.length > 1) {
    const newRows = props.component.data.rows.slice(0, -1)
    
    emit('update', props.component, {
      data: {
        ...props.component.data,
        rows: newRows
      }
    })
  }
}

function removeColumn() {
  if (props.component.data.headers.length > 1) {
    const newHeaders = props.component.data.headers.slice(0, -1)
    const newRows = props.component.data.rows.map(row => row.slice(0, -1))
    
    emit('update', props.component, {
      data: {
        ...props.component.data,
        headers: newHeaders,
        rows: newRows
      }
    })
  }
}

// Expose methods
defineExpose({
  addRow,
  addColumn,
  removeRow,
  removeColumn,
  startEditing
})
</script>

<style scoped>
.visual-table {
  width: 100%;
  height: 100%;
  position: relative;
  font-family: inherit;
}

.visual-table.selected {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

.table-element {
  border-collapse: collapse;
  width: 100%;
  height: 100%;
}

.table-element th,
.table-element td {
  border: 1px solid #dee2e6;
  text-align: left;
  vertical-align: middle;
  word-wrap: break-word;
  overflow: hidden;
}

.table-element th {
  background-color: #f8f9fa;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.table-element td:focus,
.table-element th:focus {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: -2px;
  background-color: rgba(52, 152, 219, 0.1);
}

/* Table variants */
.variant-modern .table-element {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.variant-modern .table-element th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.variant-modern .table-element td {
  border: 1px solid #e9ecef;
}

.variant-classic .table-element {
  border: 2px solid #2c3e50;
}

.variant-classic .table-element th {
  background-color: #34495e;
  color: white;
  border: 1px solid #2c3e50;
}

.variant-minimal .table-element {
  border: none;
}

.variant-minimal .table-element th,
.variant-minimal .table-element td {
  border: none;
  border-bottom: 1px solid #e9ecef;
}

.variant-striped .table-element tbody tr:nth-child(odd) {
  background-color: #f8f9fa;
}

.variant-bordered .table-element,
.variant-bordered .table-element th,
.variant-bordered .table-element td {
  border: 1px solid #dee2e6;
}

/* Table controls */
.table-controls {
  position: absolute;
  top: -40px;
  right: 0;
  display: flex;
  gap: 4px;
  background: white;
  padding: 4px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 20;
}

.control-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s ease;
}

.control-button:hover:not(:disabled) {
  background: var(--primary, #3498db);
  color: white;
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Hover effects */
.visual-table:hover {
  transform: scale(1.01);
  transition: transform 0.2s ease;
}

.visual-table.selected:hover {
  transform: scale(1.02);
}

/* Responsive */
@media (max-width: 768px) {
  .table-element {
    font-size: 12px;
  }
  
  .table-element th,
  .table-element td {
    padding: 6px 8px;
  }
}
</style>