import { io, Socket } from 'socket.io-client'
import { ref, onMounted, onUnmounted } from 'vue'

let socket: Socket | null = null

export const useRealtime = () => {
  const connected = ref(false)

  const initSocket = () => {
    if (!process.client) return null
    if (socket) return socket

    // Connect directly to the socket server on the same hostname as the page.
    // Frappe realtime validates the origin hostname, so the socket host must match.
    const sitename = 'mysite.local'
    const socketOrigin = new URL(window.location.origin)
    socketOrigin.port = '9000'
    const socketUrl = `${socketOrigin.origin}/${sitename}`

    console.log(`Connecting directly to Socket.io at ${socketUrl}...`)

    // Using full URL to avoid interaction with Nuxt's dev server router
    socket = io(socketUrl, {
      path: '/socket.io',
      transports: ['websocket'],
      withCredentials: true,
      reconnection: true,
    })

    socket.on('connect', () => {
      console.log('Socket.io connected')
      connected.value = true
    })

    socket.on('disconnect', () => {
      console.log('Socket.io disconnected')
      connected.value = false
    })

    socket.on('connect_error', (error) => {
      console.error('Socket.io connection error:', error)
    })

    socket.onAny((eventName, ...args) => {
      console.log(`[Socket Debug] Event: ${eventName}`, args)
    })

    return socket
  }

  const on = (event: string, callback: (data: any) => void) => {
    const s = initSocket()
    if (s) s.on(event, callback)
  }

  const off = (event: string, callback?: (data: any) => void) => {
    if (socket) {
      socket.off(event, callback)
    }
  }

  const emit = (event: string, ...args: any[]) => {
    const s = initSocket()
    if (s) s.emit(event, ...args)
  }

  const subscribe = (room: string) => {
    console.log(`[Socket] Subscribing to room: ${room}`)
    emit('subscribe', { room })
  }

  const docSubscribe = (doctype: string, docname: string) => {
    console.log(`[Socket] Doc subscribing to ${doctype}/${docname}`)
    emit('doc_subscribe', doctype, docname)
  }

  const docUnsubscribe = (doctype: string, docname: string) => {
    console.log(`[Socket] Doc unsubscribing from ${doctype}/${docname}`)
    emit('doc_unsubscribe', doctype, docname)
  }

  return {
    connected,
    on,
    off,
    emit,
    subscribe,
    docSubscribe,
    docUnsubscribe,
    initSocket
  }
}
