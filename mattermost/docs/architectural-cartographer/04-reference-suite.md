# Reference Suite

## Doc 1: Junior Onboarding Guide

Start with the product: Mattermost is a Go and React self-hosted collaboration platform backed by PostgreSQL (`README.md:1-3`). Then learn the front door: `root.tsx` sets webpack path and basename, `entry.tsx` sets CSRF/error behavior and mounts React, `App` provides Redux and routing, and `Root` loads config/me before routes (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`, `webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:231-247`).

Day-one setup is reconstructed from checked-in files: run `npm install` from `webapp/` because it owns npm workspaces (`webapp/README.md:5-23`); use `server/Makefile` targets for Docker, server, client, and combined run (`server/Makefile:247-255`, `server/Makefile:602-690`). Keep a note that complete local prerequisite and seed-user instructions are not fully checked in; the root README points to external developer setup docs (`README.md:33-37`).

## Doc 2: Mid-Level Architecture Guide

The architecture is a pipeline: React route shell to channel view to editor to submit hook to Redux thunk to `Client4` to Go API handler to app service to SQL store (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/actions/views/create_comment.tsx:40-123`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

For any feature, identify the contract at every boundary: TypeScript type (`webapp/platform/types/src/posts.ts:90-119`), client method (`webapp/platform/client/src/client4.ts:2420-2434`), API route (`server/channels/api4/post.go:23-57`), app method (`server/channels/app/post.go:162-488`), and persistence schema/store (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Doc 3: Senior Ownership Guide

Own the seams that fail silently: optimistic pending posts can diverge from server state (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`), post events can fail after persistence without failing the request (`server/channels/app/post.go:474-476`), and plugin hooks can reject or mutate messages (`server/channels/app/post.go:323-348`). Own migration debt: React 18 legacy mount must be retired before React 19 (`webapp/channels/src/entry.tsx:55-60`). Own security boundaries: session-required handlers, session-derived authorship, permission checks, and metadata sanitization (`server/channels/web/handlers.go:565-581`, `server/channels/api4/post.go:103-114`, `server/channels/app/post.go:483-488`).

## Doc 4: Code Review Guide

Review order:

1. Product behavior: does the change fit teams/channels/posts/plugins/notifications (`README.md:1-19`)?
2. Type contract: are shared TS types updated (`webapp/platform/types/src/posts.ts:90-119`)?
3. UI state: does optimistic behavior handle success and failure (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`)?
4. API boundary: does the endpoint use the right handler wrapper and avoid trusting browser identity (`server/channels/api4/post.go:23-57`, `server/channels/api4/post.go:103-105`)?
5. Business logic: are permission, plugin, metadata, event, and persistence behaviors in the right layer (`server/channels/app/post.go:162-488`)?
6. Database: are migrations, store validation, and counters consistent (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`, `server/channels/store/sqlstore/post_store.go:159-325`)?
7. Tests: does the package expose relevant test scripts (`webapp/channels/package.json:172-180`) and does server coverage exist near the changed feature (`server/channels/api4/post_test.go:126-168`)?

## Doc 5: Debugging Guide

For a failed send:

1. Check whether the editor blocked locally: uploads, post errors, empty draft, deleted root, duplicate submit, modal gates (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-421`).
2. Check whether `onSubmit` treated the message as reaction, slash command, scheduled post, or normal post (`webapp/channels/src/actions/views/create_comment.tsx:177-208`, `webapp/channels/src/actions/views/create_comment.tsx:100-123`).
3. Check pending post state: optimistic insert happens before HTTP returns (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-263`).
4. Check the network call: `Client4.createPost` posts JSON to the posts route (`webapp/platform/client/src/client4.ts:2420-2434`).
5. Check API rejection: decode, sanitize, session user, permission checks, and app error (`server/channels/api4/post.go:96-130`).
6. Check app-layer rejection: dedupe, parent post validation, plugin hooks, file attach, event handling (`server/channels/app/post.go:173-206`, `server/channels/app/post.go:275-348`, `server/channels/app/post.go:389-488`).
7. Check SQL: validation, transaction, insert, thread updates, channel counters (`server/channels/store/sqlstore/post_store.go:159-325`).

## Doc 6: Change Playbook

To add a feature end-to-end:

1. Start with user behavior in the channel UI (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`).
2. Add or modify focused UI components before touching the editor core (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`).
3. If submit behavior changes, update `useSubmit` and `create_comment.tsx` together (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-421`, `webapp/channels/src/actions/views/create_comment.tsx:40-123`).
4. Update shared actions and API client only when data crossing the server boundary changes (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`).
5. Add route, permission checks, and app-layer logic on the server (`server/channels/api4/post.go:23-181`, `server/channels/app/post.go:162-488`).
6. Update store and migrations for durable shape changes (`server/channels/store/sqlstore/post_store.go:159-325`, `server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).
7. Test the smallest changed unit, then the end-to-end path (`webapp/channels/package.json:172-180`, `server/Makefile:481-529`).

## Doc 7: Interview Walkthrough

"Mattermost is a self-hosted collaboration platform built in Go and React with PostgreSQL (`README.md:1-3`). The webapp bootstraps dynamic asset paths, mounts React, wraps the app in Redux and React Router, then the root component loads config, current user, products, and plugins before rendering routes (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`, `webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:108-119`). A channel screen renders the post list and composer; sending a message flows through an editor hook, Redux optimistic update, typed API client, Go API handler, app-layer validation/plugins/events, SQL persistence, and response reconciliation (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`)."

