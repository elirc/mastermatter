# Mid-Level Engineer Guide

## Full-Stack Architecture Diagram

```text
Browser DOM
  -> webapp/channels/src/root.tsx sets webpack public path and basename
  -> webapp/channels/src/entry.tsx runs CSRF/error setup and mounts React
  -> App wraps Root in Redux Provider and react-router Router
  -> Root loads config/me/products/plugins and mounts routes
  -> ChannelView renders PostView and AdvancedCreatePost
  -> AdvancedTextEditor/useSubmit turns a draft into a submit action
  -> actions/views/create_comment.tsx builds Post and runs client hooks
  -> mattermost-redux/actions/posts.ts adds optimistic pending post
  -> Client4.createPost POSTs JSON to /api/v4/posts
  -> api4/post.go decodes, audits, checks permissions, binds session user
  -> app/post.go validates, deduplicates, runs plugins, saves, sends events
  -> sqlstore/post_store.go inserts into Posts and updates counts
  -> response returns created Post; websocket/event path updates other clients
```

Each arrow is backed by a file boundary: frontend bootstrap (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`), app shell (`webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:305-470`), composer path (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`), API client (`webapp/platform/client/src/client4.ts:2420-2434`), route and app layer (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`), and SQL store (`server/channels/store/sqlstore/post_store.go:159-325`).

## Type System Deep Dive

The frontend post contract is explicit: `Post` contains identity, timestamps, channel/thread IDs, message, type, props, hashtags, pending ID, reply count, optional file IDs, metadata, and client-only failure state (`webapp/platform/types/src/posts.ts:90-119`). `PostMetadata` carries embeds, emojis, files, images, reactions, priority, acknowledgements, translations, expiration, recipients, and redaction counts (`webapp/platform/types/src/posts.ts:76-88`). The app-level store type composes shared Mattermost state with webapp-specific `plugins`, `storage`, and `views` slices (`webapp/channels/src/types/store/index.ts:20-24`).

The backend post model defines post types, property keys, size constants, and priority metadata (`server/public/model/post.go:28-118`, `server/public/model/post.go:220-226`). The database migration persists matching core fields in `posts`, including IDs, timestamps, user/channel/root IDs, message, type, props, hashtags, filenames, file IDs, reaction flags, pin state, edit time, and remote ID (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).

The mid-level lesson: TypeScript protects the browser-facing shape, Go validates the server model, and SQL defines the durable subset. When changing post shape, inspect all three.

## State Management Deep Dive

State has two layers. The app store config combines webapp reducers with shared service reducers and persists some slices with localForage (`webapp/channels/src/store/index.ts:31-48`). Cross-tab changes rehydrate persisted state so multiple browser tabs stay coherent (`webapp/channels/src/store/index.ts:50-94`). Logout purges persisted state and redirects to the base path (`webapp/channels/src/store/index.ts:96-119`).

For posts, the high-value state behavior is optimistic creation. `mattermost-redux` checks whether a pending post ID is already sending, builds a local post with timestamps and `pending_post_id`, dispatches `RECEIVED_NEW_POST`, then asynchronously calls `Client4.createPost` (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-263`). On success it dispatches the real post and channel count updates (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:264-297`). On failure it either removes the post for known rejection cases or marks the pending post as failed (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:298-320`).

## API Contract Map

- `POST /api/v4/posts`: frontend `Client4.createPost` sends JSON to `getPostsRoute()` with `method: 'post'` (`webapp/platform/client/src/client4.ts:2420-2434`); backend `InitPost` registers `Posts.Handle("", APISessionRequired(createPost))` (`server/channels/api4/post.go:23-25`).
- `GET /api/v4/channels/{channel_id}/posts`: backend registers `PostsForChannel.Handle("", APISessionRequired(getPostsForChannel))` (`server/channels/api4/post.go:31-34`); `getPostsForChannel` handles `after`, `before`, `since`, collapsed threads, deleted-post permissions, etags, and prepared response lists (`server/channels/api4/post.go:239-355`).
- `POST /api/v4/posts/ephemeral`: backend registers and handles ephemeral posts separately from persistent posts (`server/channels/api4/post.go:27-28`, `server/channels/api4/post.go:183-237`).

## Component Interaction Map

`Root` owns application readiness and route shell (`webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:305-470`). `ChannelView` owns the center channel layout and composer availability (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`). `AdvancedCreatePost` binds the current channel ID from Redux to `AdvancedTextEditor` (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`). `AdvancedTextEditor` wires `useSubmit`, keyboard handling, file UI, formatting UI, textbox props, and footer (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:355-459`, `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`).

## Full-Stack Feature Trace: Send A Message

1. User is in a channel. `ChannelView` renders `AdvancedCreatePost` unless the channel is archived, deactivated, restricted, or waiting for loader state (`webapp/channels/src/components/channel_view/channel_view.tsx:112-211`).
2. `AdvancedCreatePost` reads `currentChannelId` and passes it to `AdvancedTextEditor` (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`).
3. `AdvancedTextEditor` submits through a form handler and `useSubmit` (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:355-459`, `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`).
4. `useSubmit` blocks in-progress uploads, post errors, empty drafts, deleted roots, duplicate submissions, and special modal cases before calling `onSubmit` (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-421`).
5. `submitPost` builds a `Post` with message, channel ID, root ID, pending post ID, user ID, timestamps, type, metadata, and props; it validates channel permissions for mentions and runs message hooks (`webapp/channels/src/actions/views/create_comment.tsx:40-123`).
6. `PostActions.createPost` clears drafts and delegates to shared `mattermost-redux` post creation (`webapp/channels/src/actions/post_actions.ts:140-161`).
7. `mattermost-redux` creates an optimistic pending post, then calls `Client4.createPost` (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-263`).
8. `Client4.createPost` POSTs the serialized post and returns the created post (`webapp/platform/client/src/client4.ts:2420-2434`).
9. `api4.createPost` decodes JSON, sanitizes input, sets `UserId` from session, audits, runs API checks, calls app creation, updates status/activity, writes HTTP 201, and encodes the result (`server/channels/api4/post.go:96-181`).
10. `App.CreatePost` deduplicates pending IDs, validates replies, runs plugin hooks, fetches embeds/images, saves through the store, attaches files, runs post hooks, prepares metadata, sends post events, and sanitizes the result for the requester (`server/channels/app/post.go:162-488`).
11. `SqlPostStore.SaveMultiple` validates, inserts into `Posts`, updates threads, saves priority/persistent-notification rows, commits, and updates channel counters (`server/channels/store/sqlstore/post_store.go:159-325`).
12. Frontend success dispatches the real post and count updates; failure dispatches removal or failed pending state (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:264-320`).

## Diff Reading Exercise

Hypothetical change: "Add a new post metadata field called `sensitivity_label`."

Review in this order:

1. Type: does `PostMetadata` include the field with correct optionality (`webapp/platform/types/src/posts.ts:76-88`)?
2. Draft creation: does `submitPost` populate metadata from the draft (`webapp/channels/src/actions/views/create_comment.tsx:58-71`)?
3. Client: does `Client4.createPost` serialize it without stripping it (`webapp/platform/client/src/client4.ts:2420-2434`)?
4. API: does backend decoding and `SanitizeInput` preserve safe metadata (`server/channels/api4/post.go:96-105`)?
5. App: do plugin replacement and metadata preservation keep it (`server/channels/app/post.go:316-348`)?
6. Store: does `Post` validation and props/metadata storage support it, or does schema/marshal code need a migration (`server/channels/store/sqlstore/post_store.go:159-177`, `server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`)?
7. Response/UI: does success state use returned metadata, and is failure state still meaningful (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:264-320`)?

## Non-Obvious Architectural Patterns

Optimistic UI is deliberate: the app shows a pending post before the server responds (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-258`). The server has its own deduplication for pending post IDs, because clients can retry or duplicate requests (`server/channels/app/post.go:173-206`, `server/channels/app/post.go:379-383`). API handlers own session and audit concerns, while the app layer owns domain behavior (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`). Plugins can participate on both client and server message-posting paths (`webapp/channels/src/actions/views/create_comment.tsx:93-99`, `server/channels/app/post.go:323-348`, `server/channels/app/post.go:403-414`).

## Mid-Level Socratic Checkpoint

1. Why does post creation need both frontend optimistic pending IDs and backend deduplication?
2. Which layer should reject a user without `PermissionCreatePost`, and which layer should validate reply parent/root relationships?
3. Why should a route handler set `post.UserId` from the session?
4. What happens when `Client4.createPost` succeeds after an optimistic pending post is already in state?
5. Why does `App.CreatePost` call plugin hooks before and after persistence?
6. Why is `getPostsForChannel` more than a simple SQL select?
7. What three files must you inspect for a post shape change?
8. How would you detect whether a failed post is a server rejection or a client validation block?

### How To Self-Grade

Strong answers cite optimistic state and dedupe (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-326`, `server/channels/app/post.go:173-206`), permission split (`server/channels/api4/post.go:59-94`, `server/channels/app/post.go:275-295`), session identity (`server/channels/api4/post.go:103-105`), success reconciliation (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:264-297`), plugin timing (`server/channels/app/post.go:323-348`, `server/channels/app/post.go:403-414`), post-list concerns (`server/channels/api4/post.go:239-355`), type/schema files (`webapp/platform/types/src/posts.ts:90-119`, `server/public/model/post.go:28-118`, `server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`), and submit blocking paths (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:298-320`).

