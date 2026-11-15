import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useViewerStore = defineStore('viewer', () => {
  const viewer = ref(null)

  const setViewer = (newViewer) => {
    viewer.value = newViewer
  }

  const destroyViewer = () => {
    if (viewer.value) {
      viewer.value.destroy()
      viewer.value = null
    }
  }

  return {
    viewer,
    setViewer,
    destroyViewer
  }
})
