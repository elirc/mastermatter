# Journal

## Mission Design Rationale

The missions move from orientation to traceability to judgment. The codebase is too large to memorize, so the training goal is to make the reader good at finding anchors: boot files, route files, action files, type files, and store files. The mission order follows the actual dependency chain: repo purpose (`README.md:1-19`), frontend boot (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`), React shell (`webapp/channels/src/components/app.tsx:17-27`), routes (`webapp/channels/src/components/root/root.tsx:305-470`), channel UI (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`), post submit (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-421`), Redux/API (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`), and backend persistence (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Why Missions Are Ordered This Way

Junior missions teach "where am I?" skills: app heartbeat, folders, types, components, route/controller basics, props, data entry, and navigation. Mid-level missions teach "how does behavior move?" skills: state ownership, hooks, side effects, API contracts, middleware, full-stack trace, diff reading, composition, and hidden TypeScript work. Senior missions teach "what can go wrong?" skills: architecture decisions, bug prediction, performance, security, missing tests, and code history interpretation.

## Code Paths Chosen

The message-posting path was chosen because it is central to Mattermost's domain and touches the most important layers (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/actions/views/create_comment.tsx:40-123`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`). The sidebar and channel header were chosen as approachable UI anchors because they show typed props, route navigation, unread state, direct/group channel display, and shared-channel indicators (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:38-84`, `webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:158-260`, `webapp/channels/src/components/channel_header/channel_header_title.tsx:32-121`).

## Skill Each Tier Develops

Junior: map reading and code annotation. Mid-level: contract tracing and change review. Senior: risk detection, technical debt analysis, security/performance reasoning, and ownership planning.

## What A Senior Engineer Would Do Differently

A senior would read comments as risk markers, not trivia. The React 18 legacy mount comment is a future migration warning (`webapp/channels/src/entry.tsx:55-60`). The channel view TODO about debouncing websocket scope is a performance clue (`webapp/channels/src/components/channel_view/channel_view.tsx:100-104`). The app layer's warning-only event handling after persistence is an availability-versus-consistency decision (`server/channels/app/post.go:474-476`).

