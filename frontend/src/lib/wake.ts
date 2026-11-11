import { useSyncExternalStore } from 'react'

// Counts API calls that are taking long enough to suggest a Render cold start.
let slowRequests = 0
const listeners = new Set<() => void>()

function emit() {
  listeners.forEach((fn) => fn())
}

export const wake = {
  start() {
    slowRequests += 1
    emit()
  },
  end() {
    slowRequests = Math.max(0, slowRequests - 1)
    emit()
  },
}

export function useServerWaking() {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn)
      return () => listeners.delete(fn)
    },
    () => slowRequests > 0,
  )
}
