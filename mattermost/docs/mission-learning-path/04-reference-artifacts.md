# Mission 25: Write the Docs That Don't Exist
**Tier:** Senior
**Time Estimate:** 90 minutes
**Goal:** Turn code-reading skill into durable workflow references.
**The Concept:** A good internal doc is a channel post that future engineers can act on without asking the author.
**Design Intent Before You Read the Code:** Use workflow documents for action, not passive study; each reference below points to the code path it supports.
**Find It In The Code:** Use `README.md:1-37`, `webapp/README.md:1-35`, `server/Makefile:247-690`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-421`, `server/channels/api4/post.go:23-181`, and `server/channels/app/post.go:162-488`.

```text
Doc pattern:
Action -> owning file -> success signal -> risk check.
// Workflow docs should help someone do the work, not admire the architecture.
```

**The Aha Moment:** Documentation becomes engineering leverage when it names the next action.
**Socratic Checkpoint:** What action does this doc help with? Which files does it open first? What mistakes does it prevent? What test or command proves success? Who owns keeping it current?

How to self-grade: strong answers cite setup files (`README.md:33-37`, `webapp/README.md:5-23`, `server/Makefile:247-690`), post flow files (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-421`, `server/channels/api4/post.go:23-181`, `server/channels/app/post.go:162-488`), and test command files (`webapp/channels/package.json:172-180`).
**Connects To:** Mission 1 and Mission 24 because documentation should preserve both onboarding and history.

## Doc 1: Junior Onboarding Checklist

- Read the product and stack summary (`README.md:1-19`).
- Install webapp dependencies from `webapp/` (`webapp/README.md:5-23`).
- Use Makefile targets for Docker, server, and client (`server/Makefile:247-255`, `server/Makefile:602-690`).
- Trace frontend boot once before editing UI (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`).
- For your first PR, identify type, component, action, API, and test impact before coding (`webapp/platform/types/src/posts.ts:90-119`, `webapp/channels/package.json:172-180`).

## Doc 2: Architecture Guide For New Engineers

Navigate by ownership. Routes live in `api4` (`server/channels/api4/api.go:18-80`), business rules in `app` (`server/channels/app/post.go:162-488`), persistence in `store/sqlstore` (`server/channels/store/sqlstore/post_store.go:159-325`), UI shell in `components/root` (`webapp/channels/src/components/root/root.tsx:305-470`), and shared frontend contracts in `webapp/platform/types` (`webapp/platform/types/src/posts.ts:90-119`).

## Doc 3: Code Review Checklist

- Does the change respect optimistic post lifecycle (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-326`)?
- Does the route require session/MFA where needed (`server/channels/web/handlers.go:565-581`)?
- Does the server derive identity from session (`server/channels/api4/post.go:103-105`)?
- Does app logic preserve plugin and metadata invariants (`server/channels/app/post.go:316-348`)?
- Does persistence update durable schema and counters correctly (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`, `server/channels/store/sqlstore/post_store.go:295-325`)?

## Doc 4: Debugging Playbook

For post failures, inspect local submit gates (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`), command/reaction branching (`webapp/channels/src/actions/views/create_comment.tsx:177-208`), optimistic failure handling (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:298-320`), HTTP call (`webapp/platform/client/src/client4.ts:2420-2434`), API checks (`server/channels/api4/post.go:59-130`), app validation/plugins (`server/channels/app/post.go:173-348`), and SQL write (`server/channels/store/sqlstore/post_store.go:159-325`).

## Doc 5: Change Playbook

Branch, identify touched layers, update TypeScript contracts first, update UI/action path, update API client if HTTP shape changes, update Go handler/app/store if server behavior changes, add tests, then run focused checks. Relevant scripts: frontend `check`, `build`, `run`, `test`, and `check-types` (`webapp/channels/package.json:172-180`); server targets include test targets and run targets (`server/Makefile:481-529`, `server/Makefile:602-690`).

## Doc 6: Senior Ownership Notes

Monitor React mount migration debt (`webapp/channels/src/entry.tsx:55-60`), event failures after successful post persistence (`server/channels/app/post.go:474-476`), plugin post replacement and metadata preservation (`server/channels/app/post.go:316-348`), and SQL write/counter consistency (`server/channels/store/sqlstore/post_store.go:248-325`).

## Doc 7: Interview Walkthrough

Practice answer: "Mattermost is a Go/React/PostgreSQL collaboration platform (`README.md:1-3`). The browser bootstraps webpack paths, mounts React, wraps Redux/router, and loads the root route shell (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`, `webapp/channels/src/components/app.tsx:17-27`, `webapp/channels/src/components/root/root.tsx:305-470`). Sending a message flows through channel UI, editor submit hook, Redux optimistic action, typed API client, Go API route, app service, SQL store, and response/event handling (`webapp/channels/src/components/channel_view/channel_view.tsx:203-233`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`, `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`, `webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`)."

