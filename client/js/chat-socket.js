import { tokenService } from '@/core/cms/js/tokenService.js'

function buildWsUrl(workId) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = import.meta.env.VITE_API_HOST || window.location.hostname
  const port = import.meta.env.VITE_API_PORT ? `:${import.meta.env.VITE_API_PORT}` : ''
  const token = tokenService.getAccess() || ''
  return `${protocol}://${host}${port}/ws/science_publishing/works/${workId}/chat/?token=${encodeURIComponent(token)}`
}

export function createChatSocket(workId, { onMessage, onError, onOpen } = {}) {
  const url = buildWsUrl(workId)
  let socket = new WebSocket(url)

  socket.onopen = () => {
    if (typeof onOpen === 'function') onOpen()
  }

  socket.onerror = (ev) => {
    if (typeof onError === 'function') onError(ev)
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (typeof onMessage === 'function') {
        onMessage(data)
      }
    } catch (e) {
      console.warn('WS parse error', e)
    }
  }

  function sendMessage(payload) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload))
    } else {
      throw new Error('WebSocket is not connected')
    }
  }

  function close() {
    if (socket) {
      socket.close()
    }
    socket = null
  }

  return {
    sendMessage,
    close,
    raw: () => socket
  }
}
