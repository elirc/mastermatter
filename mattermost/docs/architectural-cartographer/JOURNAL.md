# Journal

## First-Pass Mental Model

Mattermost is a Go server plus React/TypeScript webapp, released from one core repo, with PostgreSQL as the persistence layer (`README.md:1-3`). The server starts from `server/cmd/mattermost/main.go`, delegates command execution to Cobra, and the default command runs the server (`server/cmd/mattermost/main.go:19-22`, `server/cmd/mattermost/commands/server.go:27-39`). The webapp starts through `webapp/channels/src/root.tsx`, sets the dynamic asset base path, and imports `entry.tsx` (`webapp/channels/src/root.tsx:8-23`).

The most useful teaching flow is "send a message." It crosses a small channel UI (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`), a focused create-post wrapper (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`), a complex editor (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:355-459`, `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`), a submission hook (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`), Redux thunks (`webapp/channels/src/actions/views/create_comment.tsx:40-123`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`), the typed HTTP client (`webapp/platform/client/src/client4.ts:2420-2434`), Go API routes (`server/channels/api4/post.go:23-57`), server permission checks (`server/channels/api4/post.go:59-94`), app-layer business logic (`server/channels/app/post.go:162-488`), and SQL persistence (`server/channels/store/sqlstore/post_store.go:159-325`, `server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).

## Important Discoveries

The frontend still uses `ReactDOM.render` even though it is on React 18, because `createRoot` automatic batching breaks some components; that is a concrete architectural debt item noted in source comments (`webapp/channels/src/entry.tsx:55-60`). Routing uses `react-router-dom` v5 style `Router`, `Switch`, `Route`, and `Redirect` (`webapp/channels/src/components/app.tsx:4-23`, `webapp/channels/src/components/root/root.tsx:315-428`). State is Redux plus redux-persist/localForage, with cross-tab rehydration and logout cleanup (`webapp/channels/src/store/index.ts:31-126`).

The server API is organized around `Routes` fields that point to `gorilla/mux` subrouters (`server/channels/api4/api.go:18-80`). Session-required API endpoints are wrapped with a handler that marks `RequireSession` and `RequireMfa` true (`server/channels/web/handlers.go:565-581`). The request context carries the app, request context, route params, logger, and error slot (`server/channels/web/context.go:19-26`).

## Why These Files Were Chosen

`webapp/channels/src/entry.tsx`, `components/app.tsx`, and `components/root/root.tsx` show the front door from DOM to Redux to routes (`webapp/channels/src/entry.tsx:31-60`, `webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:305-428`). `ChannelView`, `AdvancedCreatePost`, `AdvancedTextEditor`, and `useSubmit` show how a user-visible channel becomes an actual post submission (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`). `server/channels/api4/post.go`, `server/channels/app/post.go`, and `server/channels/store/sqlstore/post_store.go` show the backend route, business logic, and database write (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Where A Junior Might Get Confused

A junior may expect one frontend "app file," but the app has a bootstrap layer, root route layer, product/plugin layer, and feature components (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:55-78`, `webapp/channels/src/components/root/root.tsx:429-470`). A junior may also expect a post submission to wait for the server before updating the UI, but the Redux action creates a pending post optimistically before the `Client4.createPost` request completes (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-258`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:260-326`).

## Where A Mid-Level Engineer Should Slow Down

Slow down around boundaries: the app-specific `actions/post_actions.ts` wrapper clears drafts and records recent emojis, while the lower `mattermost-redux` action manages pending IDs, optimistic state, server success, and failure (`webapp/channels/src/actions/post_actions.ts:140-161`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`). On the server, the API layer owns request decoding, session identity, audit, and HTTP response, while `App.CreatePost` owns deduplication, validation, plugins, embeds, persistence, notifications, and metadata sanitization (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`).

## Where A Senior Engineer Should Be Skeptical

Be skeptical where comments reveal migration debt or concurrency boundaries: React 18 is intentionally started through deprecated `ReactDOM.render` (`webapp/channels/src/entry.tsx:55-60`), post creation uses optimistic UI plus async server reconciliation (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`), and the Go app layer performs persistence before websocket/event handling, logging but not failing the whole request if post events fail (`server/channels/app/post.go:474-476`). Security review should focus on permission checks, session enforcement, metadata sanitization, and plugin hooks (`server/channels/api4/post.go:59-94`, `server/channels/web/context.go:130-141`, `server/channels/app/post.go:323-348`, `server/channels/app/post.go:483-488`).

## How To Use Checkpoints

Answer from memory, then reopen the cited files. A strong answer names a boundary, the owning file, and the data shape crossing that boundary. For example, "the browser sends a JSON `Post` through `Client4.createPost` to `/api/v4/posts`; the Go API decodes it into `model.Post`, assigns the session user, then calls `CreatePostAsUser`" is strong because it cites both frontend and backend ownership (`webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-130`).

