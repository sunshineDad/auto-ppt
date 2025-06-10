<template>
  <div
    class="selection-box"
    :style="boxStyle"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  box: {
    x: number
    y: number
    width: number
    height: number
  }
}

const props = defineProps<Props>()

const boxStyle = computed(() => ({
  position: 'absolute',
  left: `${Math.min(props.box.x, props.box.x + props.box.width)}px`,
  top: `${Math.min(props.box.y, props.box.y + props.box.height)}px`,
  width: `${Math.abs(props.box.width)}px`,
  height: `${Math.abs(props.box.height)}px`,
  border: '1px dashed var(--primary)',
  backgroundColor: 'rgba(25, 118, 210, 0.1)',
  pointerEvents: 'none',
  zIndex: 1000
}))
</script>

<style scoped>
.selection-box {
  transition: none;
}
</style>