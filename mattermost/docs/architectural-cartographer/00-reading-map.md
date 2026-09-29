# Reading Map

## Mental Model

Mattermost is a channel-based collaboration app where React renders the workspace, Redux stores local and server-derived state, typed client functions send HTTP requests, Go API handlers enforce sessions and permissions, app-layer services apply collaboration rules and plugins, and SQL stores persist posts, channels, users, and related metadata. The repo README names the high-level stack as Go, React, and PostgreSQL (`README.md:1-3`); the message-posting path proves the architecture from UI to database and back (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Top 10 Files To Read In Order

1. `README.md` - read first to anchor product and stack; explain afterwards why Mattermost is both a product and a platform (`README.md:1-19`).
2. `webapp/README.md` - read to understand workspaces and dependency review expectations; explain how `webapp/channels` fits the former standalone webapp (`webapp/README.md:1-28`, `webapp/README.md:30-35`).
3. `webapp/channels/src/root.tsx` - read to understand asset path bootstrapping; explain why `window.publicPath` and `window.basename` exist before Redux loads (`webapp/channels/src/root.tsx:8-23`).
4. `webapp/channels/src/entry.tsx` - read to understand pre-render setup, CSRF setup, global JS error handling, and React mounting (`webapp/channels/src/entry.tsx:31-60`).
5. `webapp/channels/src/components/app.tsx` - read to understand Redux `Provider`, router history, and lazy root loading (`webapp/channels/src/components/app.tsx:17-27`).
6. `webapp/channels/src/components/root/root.tsx` - read to understand route gating, config/me loading, product/plugin routes, and logged-in layout (`webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:231-247`, `webapp/channels/src/components/root/root.tsx:305-470`).
7. `webapp/channels/src/components/channel_view/channel_view.tsx` - read to understand the central channel screen and how it decides whether the post composer is available (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`).
8. `webapp/channels/src/components/advanced_text_editor/use_submit.tsx` - read to understand the submit decision tree, validation gates, slash-command exceptions, and draft reset (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-421`).
9. `server/channels/api4/post.go` - read to understand route registration, permission checks, request decoding, audit, response encoding, and post-list reads (`server/channels/api4/post.go:23-57`, `server/channels/api4/post.go:59-181`, `server/channels/api4/post.go:239-355`).
10. `server/channels/app/post.go` and `server/channels/store/sqlstore/post_store.go` - read to understand app-level post creation and SQL persistence; explain why `App.CreatePost` is more than a database insert (`server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Three Most Important Data Flows

1. Message creation: `AdvancedTextEditor` form submit calls `useSubmit`, which calls `onSubmit`, which builds a `Post`, runs hooks, dispatches `createPost`, sends `Client4.createPost`, reaches `POST /api/v4/posts`, calls `App.CreatePost`, saves through `SqlPostStore`, emits events, and returns the created post (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/actions/views/create_comment.tsx:40-123`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).
2. Route and layout flow: `root.tsx` sets public paths, `entry.tsx` mounts React, `App` provides Redux and router, and `Root` gates routes until config/me and product/plugin initialization finish (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:55-78`, `webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:305-470`).
3. Channel reading flow: `ChannelView` renders `PostView` for a channel, while server-side `getPostsForChannel` validates pagination parameters, permissions, etags, and returns a prepared post list (`webapp/channels/src/components/channel_view/channel_view.tsx:214-233`, `server/channels/api4/post.go:239-355`).

## Pre-Reading Checklist

1. Can I explain the product domain: teams, channels, posts, replies, files, plugins, notifications (`README.md:1-19`)?
2. Can I identify the frontend bootstrap files (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`)?
3. Can I identify the server bootstrap files (`server/cmd/mattermost/main.go:19-22`, `server/cmd/mattermost/commands/server.go:39-104`)?
4. Can I say where React routing is defined (`webapp/channels/src/components/root/root.tsx:315-428`)?
5. Can I say where Redux store setup lives (`webapp/channels/src/store/index.ts:31-126`)?
6. Can I find the typed post model on the frontend (`webapp/platform/types/src/posts.ts:90-119`)?
7. Can I find the post model constants on the backend (`server/public/model/post.go:28-118`)?
8. Can I find the API route for creating a post (`server/channels/api4/post.go:23-33`, `server/channels/api4/post.go:96-181`)?
9. Can I find the database schema for posts (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`)?
10. Can I distinguish app-specific actions from shared `mattermost-redux` actions (`webapp/channels/src/actions/post_actions.ts:140-161`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`)?

## Red Flags Checklist

1. A frontend change bypasses the typed `Client4` methods instead of using the established API client (`webapp/platform/client/src/client4.ts:2420-2434`).
2. A post-related server change skips `APISessionRequired` or permission checks (`server/channels/api4/post.go:23-33`, `server/channels/api4/post.go:59-94`).
3. A change trusts client-provided `user_id`; the server sets `post.UserId` from the session (`server/channels/api4/post.go:103-105`).
4. A change mutates persisted post shape without updating migrations and TypeScript types (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`, `webapp/platform/types/src/posts.ts:90-119`).
5. A change ignores pending post IDs, optimistic UI, or duplicate submission protection (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-258`, `server/channels/app/post.go:173-206`).
6. A route returns raw posts without preparing/sanitizing metadata (`server/channels/api4/post.go:331-343`, `server/channels/app/post.go:483-488`).
7. A plugin hook is added in a way that can reject or mutate posts without preserving protected metadata (`server/channels/app/post.go:316-348`).
8. A React submit change allows duplicate submission while `isDraftSubmitting` is true (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-307`).
9. A dependency change lacks review of duplicates, licenses, or peer conflicts (`webapp/README.md:30-35`, `webapp/channels/package.json:145-165`).
10. A setup change assumes Docker can be skipped even though the Makefile starts Docker for local development unless `MM_NO_DOCKER=true` (`server/Makefile:247-255`).

