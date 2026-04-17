# Vidyaan Realtime Socket.IO Architecture

## Overview

This document describes how realtime assignment comments are implemented in the Vidyaan app using Socket.IO on the frontend and Frappe realtime events on the backend.

## Key components

- Frontend socket client: `apps/vidyaan/frontend/composables/useRealtime.ts`
- Student assignment page: `apps/vidyaan/frontend/pages/academics/assignments/[id].vue`
- Teacher assignment page: `apps/vidyaan/frontend/pages/teacher/academics/assignments/[id].vue`
- Backend realtime publisher: `apps/vidyaan/vidyaan/api_folder/assignments.py`

## How it works

### 1. Socket initialization

The frontend creates a single shared Socket.IO connection in `useRealtime.ts`.

- `initSocket()` is called lazily on first use
- It builds the socket URL from the browser origin and port `9000`
- It uses:
  - `path: '/socket.io'`
  - `transports: ['websocket']`
  - `withCredentials: true`
  - `reconnection: true`

The socket instance is stored in a module-level `let socket: Socket | null` so the same connection is reused by all consumers.

### 2. Frappe document room subscription

The frontend uses Frappe's document subscription events:

- `docSubscribe(doctype, docname)`
- `docUnsubscribe(doctype, docname)`

For assignment pages, the app subscribes to:

- `docSubscribe('Assignment', assignmentId)`

This means the client joins the Frappe realtime room for that assignment document.

### 3. Listening for realtime events

The pages listen for the custom event:

- `vidyaan:assignment_message`

When an event arrives, `handleRealtimeMessage(data)` handles it.

Supported actions:

- `add`
- `update`
- `delete`

Each page updates its local `assignment.value.messages` list accordingly.

### 4. Duplicate prevention

When a comment is added locally, the page may receive the same message again from the realtime stream.

To prevent duplicates, both student and teacher pages check whether the message ID already exists before pushing it to the local list:

- `assignment.value.messages.find((m: any) => m.id === res.comment.id)`

This ensures the same comment is displayed once.

## Backend publishing

In `apps/vidyaan/vidyaan/api_folder/assignments.py`, realtime events are published after comment operations.

### Add comment

`add_assignment_comment()` builds the comment payload and calls `frappe.publish_realtime(...)`:

- event: `vidyaan:assignment_message`
- action: `add`
- room: `doc:Assignment/{assignment_name}`

The payload includes:

- `assignment`
- `student`
- `comment` metadata:
  - `id`
  - `content`
  - `author`
  - `author_email`
  - `creation`

### Update comment

`update_assignment_comment()` publishes:

- action: `update`
- comment_id
- content
- room: `doc:Assignment/{assignment_name}`

### Delete comment

`delete_assignment_comment()` publishes:

- action: `delete`
- comment_id
- room: `doc:Assignment/{assignment_name}`

## Assignment page flow

### Student page

File: `apps/vidyaan/frontend/pages/academics/assignments/[id].vue`

- subscribes to doc room on mount
- listens for `vidyaan:assignment_message`
- updates local comment list for add/update/delete
- unsubscribes on unmount
- sends comments through API and appends locally only if not duplicate

### Teacher page

File: `apps/vidyaan/frontend/pages/teacher/academics/assignments/[id].vue`

- same realtime flow as student page
- additionally filters realtime messages by selected student
- sends comments using teacher comment API with student context

## Important notes

- The current socket URL is built from `window.location.origin` and port `9000`.
- `apps/vidyaan/frontend/nuxt.config.ts` contains HTTP proxy settings, but the realtime socket connection bypasses those proxies because it uses a direct absolute socket URL.
- The site name is hardcoded in the socket composable as `school.localhost`, so if the deployment uses another hostname, that value must be updated or made dynamic.

## Recommendations

- Consider deriving the sitename dynamically from `window.location.hostname` or a config value.
- Keep realtime event names and room naming consistent with Frappe doc room conventions.
- Keep the duplicate-check logic to avoid showing the same comment twice.

## Useful file references

- `apps/vidyaan/frontend/composables/useRealtime.ts`
- `apps/vidyaan/frontend/pages/academics/assignments/[id].vue`
- `apps/vidyaan/frontend/pages/teacher/academics/assignments/[id].vue`
- `apps/vidyaan/vidyaan/api_folder/assignments.py`
- `apps/vidyaan/frontend/nuxt.config.ts`
