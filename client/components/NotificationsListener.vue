<template>
  <!-- Компонент без UI: держит websocket-подписку на уведомления модуля -->
  <span style="display: none" aria-hidden="true"></span>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotifications } from '@/js/utils/useNotifications'
import { createNotificationsSocket } from '@/modules/science_publishing/client/js/notifications-socket.js'

const { showNotification } = useNotifications()
const router = useRouter()

let socketInstance = null
const seenNotifications = new Set()
const MAX_SEEN = 200

function goToPayloadRoute(payload) {
  if (!payload || !payload.route_name) return
  try {
    router.push({
      name: payload.route_name,
      params: payload.route_params || {},
      query: payload.route_query || {},
    })
  } catch (e) {
    console.warn('Notification navigation error', e)
  }
}

function handleNotification(payload) {
  if (!payload) return
  if (payload.id && seenNotifications.has(payload.id)) {
    return
  }
  if (payload.id) {
    seenNotifications.add(payload.id)
    if (seenNotifications.size > MAX_SEEN) {
      const first = seenNotifications.values().next().value
      seenNotifications.delete(first)
    }
  }

  const type = payload.type || 'info'
  const workTitle = payload.work_title || payload.workTitle || ''
  const author = payload.author || payload.author_username || ''
  const contentText = (payload.message || payload.content || '').trim()

  let message = payload.message
  if (!message) {
    if (type === 'work_published') {
      message = workTitle ? `Работа "${workTitle}" опубликована.` : 'Работа опубликована.'
    } else if (type === 'editor_task') {
      message = workTitle ? `Новая задача: "${workTitle}".` : 'Новая задача редактора.'
    } else if (type === 'chat_message') {
      const snippet = contentText ? `"${contentText}"` : 'Новое сообщение'
      const prefix = author ? `${author}: ` : ''
      message = workTitle
        ? `${prefix}${snippet} — в задаче по статье "${workTitle}"`
        : `${prefix}${snippet} в задаче по статье`
    } else {
      message = 'Новое уведомление.'
    }
  }

  showNotification({
    message,
    type: type === 'chat_message' ? 'info' : 'success',
    duration: 8000,
    onClick: () => goToPayloadRoute(payload),
  })
}

onMounted(() => {
  socketInstance = createNotificationsSocket({
    onMessage: handleNotification,
  })
})

onBeforeUnmount(() => {
  if (socketInstance && typeof socketInstance.close === 'function') {
    socketInstance.close()
  }
  socketInstance = null
})
</script>
