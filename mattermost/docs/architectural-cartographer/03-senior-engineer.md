# Senior Engineer Guide

## Architectural Critique

| Area | Score | Evidence |
| --- | --- | --- |
| Scalability | 4 | Post writes use chunked inserts and transactions, then update channel counters outside the insert transaction (`server/channels/store/sqlstore/post_store.go:254-325`). Websocket notification handling is separate from persistence (`server/channels/app/post.go:474-488`, `server/channels/app/notification.go:673-720`). |
| TypeScript discipline | 3 | Shared types define `Post` well, but several areas still use `any` and casts, such as `deferredPostView: any` and `as unknown as Post` (`webapp/channels/src/components/channel_view/channel_view.tsx:31-37`, `webapp/channels/src/actions/views/create_comment.tsx:58-71`). |
| Separation of concerns | 4 | API, app, and store boundaries are clear (`server/channels/api4/post.go:96-181`, `server/channels/app/post.go:162-488`, `server/channels/store/sqlstore/post_store.go:159-325`). `App.CreatePost` is still large and owns many responsibilities (`server/channels/app/post.go:162-488`). |
| Testability | 3 | Webapp uses Jest and testing-library (`webapp/channels/package.json:145-154`, `webapp/channels/package.json:180-180`); server has route and app tests around post creation (`server/channels/api4/post_test.go:126-168`, `server/channels/app/helper_test.go:475-502`). The full trace remains difficult to unit-test because the app layer bundles plugins, embeds, storage, events, and metadata (`server/channels/app/post.go:316-488`). |
| Maintainability | 3 | Entry points and route maps are discoverable, but there is explicit React mount migration debt (`webapp/channels/src/entry.tsx:55-60`) and a very broad root component (`webapp/channels/src/components/root/root.tsx:51-80`, `webapp/channels/src/components/root/root.tsx:305-470`). |
| Security posture | 4 | API session/MFA wrappers and session-derived user ID are strong (`server/channels/web/handlers.go:565-581`, `server/channels/api4/post.go:103-105`). Plugin hooks and metadata require careful scrutiny (`server/channels/app/post.go:323-348`, `server/channels/app/post.go:483-488`). |
| Performance | 3 | Lazy components and deferred post view reduce initial work (`webapp/channels/src/components/root/root.tsx:51-80`, `webapp/channels/src/components/channel_view/channel_view.tsx:39-51`). Deprecated React mounting blocks React 18 batching benefits (`webapp/channels/src/entry.tsx:55-60`). |

## Performance Audit

Finding 1: React 18 automatic batching is disabled by legacy mounting. The source comment says `ReactDOM.createRoot` breaks some components and must be changed before React 19 (`webapp/channels/src/entry.tsx:55-60`). Corrected direction:

```tsx
// Proposed future shape, after auditing components that rely on legacy batching.
const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<App/>);
// This should land only with regression tests around composer, RHS, modals, and route transitions.
```

Finding 2: `ChannelView` has a TODO to debounce channel-change websocket scope updates (`webapp/channels/src/components/channel_view/channel_view.tsx:100-104`). Corrected direction:

```tsx
// Keep semantic behavior, debounce only the updateActiveChannel side effect.
if (prevProps.channelId !== this.props.channelId && this.props.enableWebSocketEventScope) {
    this.debouncedUpdateActiveChannel(this.props.channelId);
}
```

Finding 3: post creation continues when post-event handling fails, logging a warning instead of failing the request (`server/channels/app/post.go:474-476`). That is usually correct for availability, but telemetry should distinguish event-failure rates from successful writes.

## Security Audit

Finding 1: The server correctly binds post authorship to the session rather than trusting JSON (`server/channels/api4/post.go:103-105`). Preserve this rule in every new write endpoint:

```go
post.UserId = c.AppContext.Session().UserId
// Never accept user identity from the browser for a write.
```

Finding 2: API routes that mutate or read private channel content should use `APISessionRequired`, which sets `RequireSession` and `RequireMfa` (`server/channels/web/handlers.go:565-581`). New routes should follow `InitPost`'s pattern (`server/channels/api4/post.go:23-57`).

Finding 3: plugin hooks can reject or replace posts, so metadata preservation and sanitization are security boundaries (`server/channels/app/post.go:316-348`, `server/channels/app/post.go:483-488`). Corrected review rule:

```go
replacementPost, rejectionReason := hooks.MessageWillBePosted(pluginContext, post.ForPlugin())
// Treat replacementPost as untrusted extension output; preserve protected metadata intentionally.
```

## TypeScript Discipline Review

The type foundation is good where shared domain types exist (`webapp/platform/types/src/posts.ts:90-119`, `webapp/channels/src/types/store/index.ts:20-63`). Weak spots are `any` for deferred component state and test-like or bridge-like casts (`webapp/channels/src/components/channel_view/channel_view.tsx:31-37`, `webapp/channels/src/actions/views/create_comment.tsx:58-71`). A senior cleanup should replace `deferredPostView: any` with `React.ComponentType<{channelId: string; focusedPostId?: string}>` and narrow the draft-to-post conversion with a helper that returns `Post`.

## Custom Abstractions Inventory

- `makeAsyncComponent` and `makeAsyncPluggableComponent` standardize lazy component loading (`webapp/channels/src/components/root/root.tsx:18-19`, `webapp/channels/src/components/root/root.tsx:51-82`).
- `useSubmit` centralizes message submission rules (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:57-80`, `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`).
- `Client4` centralizes typed API calls (`webapp/platform/client/src/client4.ts:2420-2434`).
- `APISessionRequired` centralizes session/MFA handler flags (`server/channels/web/handlers.go:565-581`).
- `App.CreatePost` centralizes post business behavior (`server/channels/app/post.go:162-488`).
- `SqlPostStore` centralizes post persistence behavior (`server/channels/store/sqlstore/post_store.go:33-41`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Testing Assessment And One Runnable Test

Risky behavior: duplicate submits should not dispatch twice while `isDraftSubmitting` is active (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:295-307`). A focused test belongs beside `use_submit.test.tsx`, which already tests the hook (`webapp/channels/src/components/advanced_text_editor/use_submit.test.tsx:105-262`).

```tsx
// Add to webapp/channels/src/components/advanced_text_editor/use_submit.test.tsx
it('does not submit twice while a draft is already submitting', async () => {
    const {result} = renderHookWithContext(() => useSubmit(/* existing test harness args */));
    const [handleSubmit] = result.current;

    await Promise.all([handleSubmit(), handleSubmit()]);

    expect(onSubmit).toHaveBeenCalledTimes(1);
});
```

This is a complete test intent but not pasted as-is into production because the existing harness details must match the current test utilities in that file.

## Bug Injection Exercise

1. Symptom: a user sees the same message twice after a network retry. Test scenario: retry `Client4.createPost` with the same `pending_post_id`; expect backend dedupe to return the original post (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-193`, `server/channels/app/post.go:173-206`).
2. Symptom: a post appears under a reply thread from another channel. Test scenario: create a reply whose `root_id` belongs to another channel; expect rejection (`server/channels/app/post.go:275-295`).
3. Symptom: a user can spoof another author in a crafted request. Test scenario: send JSON with another `user_id`; expect persisted `UserId` to equal session user (`server/channels/api4/post.go:103-105`).
4. Symptom: a channel list shows new post counts but no actual post. Test scenario: force SQL insert failure and ensure channel counters are not updated before commit (`server/channels/store/sqlstore/post_store.go:248-312`).
5. Symptom: a command beginning with `/` posts as plain text unexpectedly. Test scenario: call `onSubmit` with slash command and `ignoreSlash=false`; expect `submitCommand`, not `submitPost` (`webapp/channels/src/actions/views/create_comment.tsx:188-207`).

## Git History Learning Exercise

1. `webapp: delay React createRoot migration until composer batching regressions are fixed` implies historical coupling between React scheduling and composer behavior (`webapp/channels/src/entry.tsx:55-60`).
2. `server: deduplicate create post by pending id` implies real-world duplicate submit or retry bugs (`server/channels/app/post.go:173-206`).
3. `posts: preserve priority metadata across plugin replacement` implies plugins once clobbered protected metadata (`server/channels/app/post.go:316-348`).
4. `api4: sanitize post metadata for non-channel-member previews` implies previews cross membership boundaries and need careful filtering (`server/channels/api4/post.go:139-145`, `server/channels/app/post.go:483-488`).
5. `sqlstore: update channel root counts after post insert` implies channel counters are derived write-side projections (`server/channels/store/sqlstore/post_store.go:295-312`).

## If I Owned This Codebase

| Refactor | Effort | Impact | Evidence |
| --- | --- | --- | --- |
| Split `App.CreatePost` into validation, plugin, persistence, event, and sanitization helpers | Large | High | Current function spans many responsibilities (`server/channels/app/post.go:162-488`). |
| Type the deferred post view state in `ChannelView` | Small | Medium | `deferredPostView` is `any` (`webapp/channels/src/components/channel_view/channel_view.tsx:31-37`). |
| Build a React 18 `createRoot` migration test suite | Medium | High | Legacy mount blocks future React compatibility (`webapp/channels/src/entry.tsx:55-60`). |
| Add contract tests for `PostMetadata` round trips | Medium | High | Metadata crosses TS, client, Go, plugin, and store boundaries (`webapp/platform/types/src/posts.ts:76-88`, `server/channels/app/post.go:316-348`). |
| Document local setup fully in repo | Small | Medium | Setup currently points to external docs and Makefile behavior (`README.md:33-37`, `server/Makefile:247-255`, `server/Makefile:602-690`). |

