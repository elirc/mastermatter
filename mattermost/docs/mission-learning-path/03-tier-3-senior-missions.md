# Tier 3 Senior Missions

### Mission 18: Reverse-Engineer the Architecture Decisions
**Tier:** Senior
**Time Estimate:** 60 minutes
**Goal:** Infer why the system is layered the way it is.
**The Concept:** Architecture is the memory of old product constraints.
**Design Intent Before You Read the Code:** Read comments and boundaries as decisions: legacy React mount, API route maps, app-layer plugins, and SQL counters all encode history (`webapp/channels/src/entry.tsx:55-60`, `server/channels/api4/api.go:18-80`, `server/channels/app/post.go:323-348`, `server/channels/store/sqlstore/post_store.go:295-325`).
**Find It In The Code:** Open the referenced files.

```tsx
// webapp/channels/src/entry.tsx:55-60
ReactDOM.render(<App/>, document.getElementById('root')!);
// Decision: preserve behavior over adopting createRoot immediately.
```

**The Aha Moment:** A senior engineer asks "what risk was this design paying down?"
**Socratic Checkpoint:** Why keep legacy React mounting? Why centralize routes? Why allow plugin post replacement? Why store channel counters? Why split API/app/store?

How to self-grade: cite React mount debt (`webapp/channels/src/entry.tsx:55-60`), route map (`server/channels/api4/api.go:18-80`), plugin hooks (`server/channels/app/post.go:323-348`), counters (`server/channels/store/sqlstore/post_store.go:295-325`), and layers (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`).
**Connects To:** Mission 19 and Mission 24 because decisions predict bugs and history.

### Mission 19: Find the Bugs Before They Happen
**Tier:** Senior
**Time Estimate:** 55 minutes
**Goal:** Predict likely bugs from boundary complexity.
**The Concept:** Bugs gather where many users, channels, and side effects meet.
**Design Intent Before You Read the Code:** Watch duplicate sends, permission splits, plugin mutation, event failure, and metadata sanitization (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-326`, `server/channels/app/post.go:173-206`, `server/channels/app/post.go:323-348`, `server/channels/app/post.go:474-488`).
**Find It In The Code:** Open the referenced files.

```go
if err := a.handlePostEvents(...); err != nil {
    rctx.Logger().Warn("Failed to handle post events", mlog.Err(err))
}
// User-visible success can coexist with notification/event failure.
```

**The Aha Moment:** The best bug reports start as boundary hypotheses.
**Socratic Checkpoint:** Where can duplicate sends happen? Where can permissions be missed? Where can plugin output corrupt data? Where can persistence succeed but notifications fail? Where can metadata leak?

How to self-grade: cite duplicate controls (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-307`, `server/channels/app/post.go:173-206`), permissions (`server/channels/api4/post.go:59-94`), plugin mutation (`server/channels/app/post.go:323-348`), event warning (`server/channels/app/post.go:474-476`), and metadata sanitization (`server/channels/app/post.go:483-488`).
**Connects To:** Mission 20 and Mission 22 because bug injection and security audit use the same instincts.

### Mission 20: The Bug Injection Challenge
**Tier:** Senior
**Time Estimate:** 60 minutes
**Goal:** Design tests from user-visible symptoms without editing production code.
**The Concept:** You are staging controlled incidents in the team timeline.
**Design Intent Before You Read the Code:** Use symptoms to target the boundary most likely responsible.
**Find It In The Code:** Use `use_submit.tsx:295-421`, `posts.ts:298-320`, `api4/post.go:103-130`, `app/post.go:275-348`, and `post_store.go:248-312`.

```text
Symptom: "My failed post stays as if it sent."
Target: mattermost-redux failure path.
Evidence: failure either removes or marks pending post failed.
Reference: webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:298-320
```

**The Aha Moment:** A good test names the boundary that should have stopped the bug.
**Socratic Checkpoint:** Which symptom points to local validation? Which points to server permission? Which points to SQL? Which points to websocket/event failure? Which points to optimistic reconciliation?

How to self-grade: map each symptom to one cited layer: local submit (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`), optimistic failure (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:298-320`), API identity (`server/channels/api4/post.go:103-130`), app validation (`server/channels/app/post.go:275-348`), SQL transaction/counters (`server/channels/store/sqlstore/post_store.go:248-312`).
**Connects To:** Mission 23 because every injected bug should become a missing-test candidate.

### Mission 21: Performance X-Ray
**Tier:** Senior
**Time Estimate:** 50 minutes
**Goal:** Identify performance-sensitive choices in boot, rendering, and post writes.
**The Concept:** Performance is channel flow: avoid blocking entry, avoid re-render storms, avoid expensive writes.
**Design Intent Before You Read the Code:** Look for lazy loading, deferred rendering, TODOs, batching limitations, chunked inserts, and counter updates (`webapp/channels/src/components/root/root.tsx:51-80`, `webapp/channels/src/components/channel_view/channel_view.tsx:39-51`, `webapp/channels/src/components/channel_view/channel_view.tsx:100-104`, `server/channels/store/sqlstore/post_store.go:254-325`).
**Find It In The Code:** Open the referenced files.

```tsx
const ChannelHeader = makeAsyncComponent('ChannelHeader', lazy(() => import('components/channel_header')));
// Heavy UI pieces are loaded lazily.
```

**The Aha Moment:** Performance decisions are often encoded as loading boundaries and TODO comments.
**Socratic Checkpoint:** Which components are lazy? What is deferred in `ChannelView`? What side effect has a debounce TODO? Why chunk SQL inserts? What does legacy React mount cost?

How to self-grade: cite lazy root/channel pieces (`webapp/channels/src/components/root/root.tsx:51-80`, `webapp/channels/src/components/channel_view/channel_view.tsx:21-25`), deferred post view (`webapp/channels/src/components/channel_view/channel_view.tsx:39-51`), TODO (`webapp/channels/src/components/channel_view/channel_view.tsx:100-104`), chunks (`server/channels/store/sqlstore/post_store.go:254-263`), and React mount debt (`webapp/channels/src/entry.tsx:55-60`).
**Connects To:** Mission 18 because performance choices are architecture decisions.

### Mission 22: The Security Audit
**Tier:** Senior
**Time Estimate:** 60 minutes
**Goal:** Audit post creation for authentication, authorization, identity, and data exposure.
**The Concept:** Security in Mattermost is channel membership: who may speak, who may read, and what metadata they may see.
**Design Intent Before You Read the Code:** Check session wrapper, session-required context, permission checks, session-bound user ID, and metadata sanitization (`server/channels/web/handlers.go:565-581`, `server/channels/web/context.go:130-141`, `server/channels/api4/post.go:59-181`, `server/channels/app/post.go:483-488`).
**Find It In The Code:** Open the referenced files.

```go
post.UserId = c.AppContext.Session().UserId
// Identity is server-derived, not browser-supplied.
```

**The Aha Moment:** The most important security line in a write endpoint may be an assignment.
**Socratic Checkpoint:** Where is login required? Where is MFA required? Where is author identity enforced? Where is create permission checked? Where is metadata sanitized?

How to self-grade: cite session/MFA (`server/channels/web/handlers.go:565-581`), session check (`server/channels/web/context.go:130-141`), identity (`server/channels/api4/post.go:103-105`), permission (`server/channels/api4/post.go:59-94`), and sanitization (`server/channels/app/post.go:483-488`).
**Connects To:** Mission 23 because security claims need tests.

### Mission 23: Write the Test That Doesn't Exist
**Tier:** Senior
**Time Estimate:** 70 minutes
**Goal:** Convert risk into a test plan.
**The Concept:** Tests are incident drills for future maintainers.
**Design Intent Before You Read the Code:** Choose a behavior where a small regression would harm users: duplicate submit, spoofed author, cross-channel reply, or plugin metadata preservation (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-307`, `server/channels/api4/post.go:103-105`, `server/channels/app/post.go:275-348`).
**Find It In The Code:** Open the referenced files and nearby tests such as `webapp/channels/src/components/advanced_text_editor/use_submit.test.tsx:105-262` and `server/channels/api4/post_test.go:126-168`.

```tsx
await Promise.all([handleSubmit(), handleSubmit()]);
expect(onSubmit).toHaveBeenCalledTimes(1);
// Test intent: duplicate user action should not duplicate submit.
```

**The Aha Moment:** A useful test protects a boundary, not an implementation detail.
**Socratic Checkpoint:** Which risk is highest impact? Which existing test harness is closest? What should be mocked? What should be real? What assertion proves behavior?

How to self-grade: cite risk lines (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-307`, `server/channels/api4/post.go:103-105`, `server/channels/app/post.go:275-348`) and existing test anchors (`webapp/channels/src/components/advanced_text_editor/use_submit.test.tsx:105-262`, `server/channels/api4/post_test.go:126-168`).
**Connects To:** Mission 20 because injected bugs become tests.

### Mission 24: The Git History Tells a Story
**Tier:** Senior
**Time Estimate:** 45 minutes
**Goal:** Infer evolution from code shape and comments.
**The Concept:** Git history is the channel archive for architecture decisions.
**Design Intent Before You Read the Code:** Even without running `git log`, code comments and shapes imply past migrations: React 18 mount, pending post dedupe, plugin metadata preservation, shared-channel indicators, burn-on-read storage (`webapp/channels/src/entry.tsx:55-60`, `server/channels/app/post.go:173-206`, `server/channels/app/post.go:316-348`, `webapp/channels/src/components/channel_header/channel_header_title.tsx:58-67`, `server/channels/store/sqlstore/post_store.go:179-199`).
**Find It In The Code:** Open each referenced range.

```go
// server/channels/app/post.go:189-206
// If we fail below, remove pending id from cache; if we succeed, map pending id to saved post id.
// This tells a story about duplicate requests and retry behavior.
```

**The Aha Moment:** Mature code has scars; senior engineers learn from them before adding new ones.
**Socratic Checkpoint:** What historical bug does pending ID dedupe imply? What migration does React mount imply? What product expansion does shared-channel UI imply? What compliance/privacy feature does burn-on-read imply? What plugin ecosystem risk does metadata preservation imply?

How to self-grade: cite each inferred story from source (`webapp/channels/src/entry.tsx:55-60`, `server/channels/app/post.go:173-206`, `webapp/channels/src/components/channel_header/channel_header_title.tsx:58-67`, `server/channels/store/sqlstore/post_store.go:179-199`, `server/channels/app/post.go:316-348`).
**Connects To:** Mission 18 because architecture decisions and history are the same study from different angles.

