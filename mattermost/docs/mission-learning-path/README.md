# Mission Learning Path

This suite is a training campaign. You are not reading passively; you are practicing how to trace, annotate, review, debug, and explain Mattermost code under pressure.

Recommended pacing:

1. Do one junior mission per session until you can navigate without panic.
2. Do one mid-level mission per session while drawing the flow yourself.
3. Do senior missions slowly, with a diff-review or debugging mindset.

Self-grade honestly. A strong answer cites files and line ranges, names the owning layer, and explains why that layer owns the responsibility. This suite is independent: it does not require the Architectural Cartographer or User Story Build Path suites.

The main training path uses Mattermost's post creation flow because it crosses the browser, React, Redux, API client, Go route, app service, SQL store, and websocket/event side effects (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`).

