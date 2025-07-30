# Chat API Endpoints

This document describes the HTTP endpoints used to work with the chat system.

## `/api/chat/send`
`POST` request for sending a message and receiving the full response.

Example request body:
```json
{
  "session_id": "123e4567",
  "message": "Hello there"
}
```
Response will contain a `ChatResponse` object with the model reply.

## `/api/chat/stream`
`POST` endpoint that streams the assistant reply as chunks. Clients should issue the same body as `/api/chat/send` but read the response as a stream (`text/event-stream` or chunked text).

## `/api/chat/sessions`
- `GET` – list existing chat sessions.
- `POST` – create a new session.

Create request example:
```json
{
  "title": "New Chat",
  "model_id": "default"
}
```

## `/api/chat/sessions/{session_id}`
- `GET` – fetch details for one session.
- `PUT` – update session properties (e.g. title).
- `DELETE` – remove the session and its messages.

Update example:
```json
{
  "title": "Renamed session"
}
```

Streaming behaviour is only supported by `/api/chat/stream` and returns incremental text chunks until the model finishes responding.

## Streaming with SSE

The `/api/chat/stream` endpoint can also be consumed using **Server Sent Events** (SSE).  When called, the server responds with the `text/event-stream` content type and sends chunks of text as the model generates them.

Example request using `curl`:

```bash
curl -N -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id": "123e4567", "message": "Hello"}'
```

Read each event until you receive `[DONE]` which signals the end of the stream.  A typical sequence looks like:

```
data: Hello

data:  there

data:  friend

data: [DONE]
```

If an error occurs the server will send an `event: error` block containing details so clients should listen for that event as well.
