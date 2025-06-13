<template>
  <div
    class="visual-text"
    :class="textClasses"
    :style="textStyle"
    :contenteditable="editing"
    @blur="handleBlur"
    @input="handleInput"
    @keydown="handleKeydown"
    v-html="component.content"
  ></div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { TextComponent } from '../Types/ComponentTypes'

interface Props {
  component: TextComponent
  selected?: boolean
  editing?: boolean
}

interface Emits {
  (e: 'update', component: TextComponent, changes: Partial<TextComponent>): void
  (e: 'edit', component: TextComponent): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  editing: false
})

const emit = defineEmits<Emits>()

const textElement = ref<HTMLElement>()
const isEditing = ref(false)

// Computed classes
const textClasses = computed(() => ({
  'visual-text': true,
  'selected': props.selected,
  'editing': props.editing || isEditing.value,
  'editable': props.component.editable !== false
}))

// Computed styles
const textStyle = computed(() => {
  const style = props.component.style
  return {
    fontSize: `${style.fontSize}px`,
    fontFamily: style.fontFamily,
    fontWeight: style.fontWeight,
    fontStyle: style.fontStyle,
    color: style.color,
    backgroundColor: style.backgroundColor || 'transparent',
    textAlign: style.textAlign,
    lineHeight: style.lineHeight,
    letterSpacing: style.letterSpacing ? `${style.letterSpacing}px` : 'normal',
    textDecoration: style.textDecoration || 'none',
    textShadow: style.textShadow || 'none',
    padding: style.padding ? 
      `${style.padding.top}px ${style.padding.right}px ${style.padding.bottom}px ${style.padding.left}px` : 
      '8px',
    border: style.border ? 
      `${style.border.width}px ${style.border.style} ${style.border.color}` : 
      'none',
    borderRadius: style.border?.radius ? `${style.border.radius}px` : '0',
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: getVerticalAlignment(style.verticalAlign),
    justifyContent: getHorizontalAlignment(style.textAlign),
    outline: 'none',
    cursor: props.editing || isEditing.value ? 'text' : 'inherit',
    wordWrap: 'break-word',
    overflow: 'hidden'
  }
})

// Helper functions for alignment
function getVerticalAlignment(align: string) {
  switch (align) {
    case 'top': return 'flex-start'
    case 'middle': return 'center'
    case 'bottom': return 'flex-end'
    default: return 'flex-start'
  }
}

function getHorizontalAlignment(align: string) {
  switch (align) {
    case 'left': return 'flex-start'
    case 'center': return 'center'
    case 'right': return 'flex-end'
    case 'justify': return 'stretch'
    default: return 'flex-start'
  }
}

// Event handlers
function handleBlur(event: FocusEvent) {
  if (isEditing.value) {
    isEditing.value = false
    const target = event.target as HTMLElement
    const newContent = target.innerHTML
    
    if (newContent !== props.component.content) {
      emit('update', props.component, { content: newContent })
    }
  }
}

function handleInput(event: Event) {
  if (props.editing || isEditing.value) {
    const target = event.target as HTMLElement
    const newContent = target.innerHTML
    
    // Real-time update for better UX
    emit('update', props.component, { content: newContent })
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (props.editing || isEditing.value) {
    // Handle special keys
    if (event.key === 'Escape') {
      event.preventDefault()
      ;(event.target as HTMLElement).blur()
    } else if (event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault()
      ;(event.target as HTMLElement).blur()
    }
    
    // Allow text formatting shortcuts
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'b':
          event.preventDefault()
          document.execCommand('bold')
          break
        case 'i':
          event.preventDefault()
          document.execCommand('italic')
          break
        case 'u':
          event.preventDefault()
          document.execCommand('underline')
          break
      }
    }
  }
}

// Watch for editing prop changes
watch(() => props.editing, (newEditing) => {
  if (newEditing && textElement.value) {
    nextTick(() => {
      textElement.value?.focus()
      // Select all text when starting to edit
      const range = document.createRange()
      range.selectNodeContents(textElement.value!)
      const selection = window.getSelection()
      selection?.removeAllRanges()
      selection?.addRange(range)
    })
  }
})

// Expose methods
defineExpose({
  startEditing() {
    isEditing.value = true
    emit('edit', props.component)
  },
  stopEditing() {
    isEditing.value = false
    textElement.value?.blur()
  }
})
</script>

<style scoped>
.visual-text {
  width: 100%;
  height: 100%;
  min-height: 20px;
  position: relative;
  user-select: none;
  transition: all 0.2s ease;
}

.visual-text.editing {
  user-select: text;
  cursor: text !important;
}

.visual-text.editable:hover {
  outline: 1px dashed rgba(52, 152, 219, 0.5);
}

.visual-text.selected {
  outline: 1px solid rgba(52, 152, 219, 0.8);
}

.visual-text:focus {
  outline: 2px solid var(--primary, #3498db);
  outline-offset: 2px;
}

/* Rich text formatting */
.visual-text :deep(strong),
.visual-text :deep(b) {
  font-weight: bold;
}

.visual-text :deep(em),
.visual-text :deep(i) {
  font-style: italic;
}

.visual-text :deep(u) {
  text-decoration: underline;
}

.visual-text :deep(br) {
  line-height: inherit;
}

/* Prevent default browser styling */
.visual-text :deep(*) {
  margin: 0;
  padding: 0;
}

/* Placeholder styling */
.visual-text:empty::before {
  content: attr(data-placeholder);
  color: #999;
  font-style: italic;
  pointer-events: none;
}
</style>