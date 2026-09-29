# Tier 2 Mid-Level Missions

### Mission 9: State Has a Home and a Reason
**Tier:** Mid-Level
**Time Estimate:** 40 minutes
**Goal:** Explain why Redux, localForage, and optimistic posts coexist.
**The Concept:** Mattermost is a busy channel: some state is live conversation, some is saved draft, some is cross-tab memory.
**Design Intent Before You Read the Code:** Store setup combines reducers, persists selected state, rehydrates across tabs, and purges after logout (`webapp/channels/src/store/index.ts:31-126`).
**Find It In The Code:** Open `webapp/channels/src/store/index.ts:31-126` and `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`.

```ts
persistStore(store, null, () => {
    store.dispatch({type: General.STORE_REHYDRATION_COMPLETE, complete: true});
    migratePersistedState(store, persistor);
});
// Persisted state is not "just cache"; the app announces when it is ready.
```

**The Aha Moment:** State belongs where its lifetime and synchronization needs belong.
**Socratic Checkpoint:** What state is persisted? What state is optimistic? What state is server-derived? Why rehydrate across tabs? Why purge on logout?

How to self-grade: cite persist/rehydrate (`webapp/channels/src/store/index.ts:40-94`), logout purge (`webapp/channels/src/store/index.ts:96-119`), and optimistic post lifecycle (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`).
**Connects To:** Mission 11 and Mission 14 because side effects and full traces rely on state ownership.

### Mission 10: The Custom Hook Ecosystem
**Tier:** Mid-Level
**Time Estimate:** 45 minutes
**Goal:** Compare a small utility hook with a domain-heavy hook.
**The Concept:** Hooks are reusable rituals: some are tiny timing rituals, others know channel policy.
**Design Intent Before You Read the Code:** Utility hooks should be generic; domain hooks may dispatch actions and know Mattermost rules (`webapp/channels/src/hooks/useDebounce.ts:4-35`, `webapp/channels/src/hooks/useChannelSystemPolicies.ts:25-103`).
**Find It In The Code:** Open `webapp/channels/src/hooks/useDebounce.ts:4-35` and `webapp/channels/src/hooks/useChannelSystemPolicies.ts:25-103`.

```ts
export function useDebounce<T extends(...args: never[]) => void>(callback: T, delay: number) {
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const callbackRef = useLatest(callback);
    // Generic hook: it knows time and callbacks, not Mattermost channels.
}
```

**The Aha Moment:** A hook's imports tell you whether it is generic infrastructure or domain logic.
**Socratic Checkpoint:** Which hook imports Redux? Which hook imports domain types? Why does `useDebounce` use `useLatest`? What does `useChannelSystemPolicies` fetch? What cleanup does `useDebounce` perform?

How to self-grade: cite generic hook imports and cleanup (`webapp/channels/src/hooks/useDebounce.ts:4-35`) and domain hook dispatch/effect behavior (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:25-103`).
**Connects To:** Mission 11 and Mission 23 because hooks are side effects and test targets.

### Mission 11: Side Effects Are Promises to the System
**Tier:** Mid-Level
**Time Estimate:** 45 minutes
**Goal:** Identify side effects in UI and backend post creation.
**The Concept:** Sending a message is not just writing text; it promises scroll, status, activity, events, counters, and notifications.
**Design Intent Before You Read the Code:** Side effects should be explicit and ordered after validation; failed side effects should be judged by whether they should fail the user action (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:236-249`, `server/channels/api4/post.go:147-152`, `server/channels/app/post.go:474-488`).
**Find It In The Code:** Open `webapp/channels/src/components/advanced_text_editor/use_submit.tsx:236-249`, `server/channels/api4/post.go:147-152`, and `server/channels/app/post.go:474-488`.

```go
if err := a.handlePostEvents(...); err != nil {
    rctx.Logger().Warn("Failed to handle post events", mlog.Err(err))
}
// Persistence succeeded; event failure is logged rather than returned to the user.
```

**The Aha Moment:** The ordering of side effects reveals product priorities.
**Socratic Checkpoint:** Which frontend side effect happens after successful send? Which API side effects update status/activity? Which app side effect is warning-only? Why might warning-only be correct? Which side effect would you make fatal?

How to self-grade: cite scroll/reset behavior (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:210-249`), online/activity updates (`server/channels/api4/post.go:147-152`), and event handling (`server/channels/app/post.go:474-488`).
**Connects To:** Mission 19 and Mission 21 because side effects are bug and performance hotspots.

### Mission 12: The Full API Contract
**Tier:** Mid-Level
**Time Estimate:** 50 minutes
**Goal:** Map the post API from client function to Go route.
**The Concept:** An API contract is the channel protocol: who can speak, what shape they speak in, and what answer returns.
**Design Intent Before You Read the Code:** The client method, route registration, session wrapper, handler decode, and response encode must agree (`webapp/platform/client/src/client4.ts:2420-2434`, `server/channels/api4/post.go:23-57`, `server/channels/api4/post.go:96-181`).
**Find It In The Code:** Open the three files above.

```ts
createPost = async (post) => {
    const result = await this.doFetch<Post>(
        `${this.getPostsRoute()}`,
        {method: 'post', body: JSON.stringify(post)},
    );
    return result;
};
```

**The Aha Moment:** The route is not one file; it is a handshake across client, router, handler, and model.
**Socratic Checkpoint:** What URL does the client call? What HTTP method does the server register? What wrapper enforces session? What status code does create return? What type does the client expect?

How to self-grade: cite client call (`webapp/platform/client/src/client4.ts:2420-2434`), route registration (`server/channels/api4/post.go:23-57`), session wrapper (`server/channels/web/handlers.go:565-581`), and response status/body (`server/channels/api4/post.go:154-181`).
**Connects To:** Mission 13 and Mission 14 because middleware and full-stack tracing extend API contracts.

### Mission 13: The Middleware Chain
**Tier:** Mid-Level
**Time Estimate:** 45 minutes
**Goal:** Understand how API handlers become session-aware HTTP handlers.
**The Concept:** Middleware is the channel door policy: it decides who can enter before the conversation starts.
**Design Intent Before You Read the Code:** `APISessionRequired` marks handler requirements, and `Context.SessionRequired` turns missing/invalid sessions into errors (`server/channels/web/handlers.go:565-581`, `server/channels/web/context.go:130-141`).
**Find It In The Code:** Open `server/channels/web/handlers.go:565-581` and `server/channels/web/context.go:130-141`.

```go
func (w *Web) APISessionRequired(h func(*Context, http.ResponseWriter, *http.Request)) http.Handler {
    handler := &Handler{RequireSession: true, RequireMfa: true}
    // Route registration attaches security requirements to the handler object.
    return handler
}
```

**The Aha Moment:** Middleware turns a plain function into a policy-enforced endpoint.
**Socratic Checkpoint:** Which flags are set for session-required APIs? What does `SessionRequired` check? Why is MFA attached here? How does this relate to `InitPost`? What risk appears if a route uses `APIHandler` instead?

How to self-grade: cite handler flags (`server/channels/web/handlers.go:565-581`), session checks (`server/channels/web/context.go:130-141`), and route use (`server/channels/api4/post.go:23-57`).
**Connects To:** Mission 22 because middleware is a security audit anchor.

### Mission 14: End-to-End Feature Trace
**Tier:** Mid-Level
**Time Estimate:** 70 minutes
**Goal:** Trace message creation from UI to database and back.
**The Concept:** A posted message is like an incident update moving from a user's text box to the team's permanent timeline.
**Design Intent Before You Read the Code:** Each layer should own one translation: UI intent, submit policy, domain object, optimistic state, HTTP request, permission/audit, business behavior, SQL write, and reconciliation.
**Find It In The Code:** Open `channel_view.tsx:203-233`, `advanced_create_post.tsx:15-31`, `use_submit.tsx:151-249`, `create_comment.tsx:40-123`, `posts.ts:179-326`, `client4.ts:2420-2434`, `api4/post.go:96-181`, `app/post.go:162-488`, `post_store.go:159-325`.

```text
ChannelView -> AdvancedCreatePost -> AdvancedTextEditor/useSubmit
-> create_comment.submitPost -> mattermost-redux.createPost
-> Client4.createPost -> api4.createPost -> App.CreatePost
-> SqlPostStore.SaveMultiple -> response/actions/websocket
```

**The Aha Moment:** End-to-end tracing is boundary tracing, not file memorization.
**Socratic Checkpoint:** What is the first file where a draft becomes a `Post`? Where is optimistic UI created? Where is HTTP sent? Where is session user enforced? Where is the SQL insert? What happens after persistence? Where is UI reconciled?

How to self-grade: cite draft conversion (`webapp/channels/src/actions/views/create_comment.tsx:40-123`), optimistic action (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:248-326`), HTTP (`webapp/platform/client/src/client4.ts:2420-2434`), session (`server/channels/api4/post.go:103-105`), SQL (`server/channels/store/sqlstore/post_store.go:254-263`), events (`server/channels/app/post.go:474-488`), and success dispatch (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:264-297`).
**Connects To:** Mission 15 and Mission 19 because diff review and bug prediction need this trace.

### Mission 15: Read the Diff Like an Engineer
**Tier:** Mid-Level
**Time Estimate:** 50 minutes
**Goal:** Practice reviewing a hypothetical post-feature diff.
**The Concept:** Reviewing a diff is like checking a channel announcement before it notifies everyone: validate content, audience, timing, and rollback.
**Design Intent Before You Read the Code:** A change to post metadata must be checked in TypeScript, submit assembly, client, Go handler, app hooks, store, and tests (`webapp/platform/types/src/posts.ts:76-119`, `webapp/channels/src/actions/views/create_comment.tsx:58-123`, `server/channels/app/post.go:316-348`).
**Find It In The Code:** Use the referenced files as a review checklist.

```tsx
metadata: {
    ...(draft.metadata?.priority && {priority: draft.metadata.priority}),
}
// If a diff adds metadata, this construction site must be reviewed.
```

**The Aha Moment:** Good review follows data ownership, not the order of files in the PR.
**Socratic Checkpoint:** What frontend type changes? What draft conversion changes? What client method changes? What server model or validation changes? What tests prove round trip?

How to self-grade: cite type (`webapp/platform/types/src/posts.ts:76-119`), draft conversion (`webapp/channels/src/actions/views/create_comment.tsx:58-123`), client (`webapp/platform/client/src/client4.ts:2420-2434`), app hook preservation (`server/channels/app/post.go:316-348`), and store schema (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).
**Connects To:** Mission 18 and Mission 23 because architecture decisions and tests follow review.

### Mission 16: Composition Over Inheritance
**Tier:** Mid-Level
**Time Estimate:** 40 minutes
**Goal:** Identify how the UI builds complex screens from focused components.
**The Concept:** A Mattermost channel screen is a composed workspace: header, banner, bookmarks, post list, and composer each own a job.
**Design Intent Before You Read the Code:** `ChannelView` composes lazy pieces and conditional UI instead of inheriting screen variants (`webapp/channels/src/components/channel_view/channel_view.tsx:21-25`, `webapp/channels/src/components/channel_view/channel_view.tsx:216-234`).
**Find It In The Code:** Open `webapp/channels/src/components/channel_view/channel_view.tsx:21-25` and `216-234`.

```tsx
<ChannelHeader/>
<ChannelBanner channelId={this.props.channelId}/>
{this.props.isChannelBookmarksEnabled && <ChannelBookmarks channelId={this.props.channelId}/>}
<DeferredPostView channelId={this.props.channelId} focusedPostId={this.state.focusedPostId}/>
{createPost}
// The screen is assembled from specialized parts.
```

**The Aha Moment:** Composition lets product states change without multiplying screen classes.
**Socratic Checkpoint:** Which child owns the header? Which child owns the post list? Which child owns the composer? Which part is conditional? Why is `DeferredPostView` useful?

How to self-grade: cite lazy imports (`webapp/channels/src/components/channel_view/channel_view.tsx:21-25`), deferred post view (`webapp/channels/src/components/channel_view/channel_view.tsx:39-51`), and render composition (`webapp/channels/src/components/channel_view/channel_view.tsx:216-234`).
**Connects To:** Mission 21 because composition also affects performance.

### Mission 17: TypeScript's Hidden Work
**Tier:** Mid-Level
**Time Estimate:** 45 minutes
**Goal:** See where TypeScript helps and where casts weaken guarantees.
**The Concept:** TypeScript is a channel contract checker, but `any` and casts are side doors.
**Design Intent Before You Read the Code:** Types should express component and action contracts; casts should be rare and reviewed (`webapp/channels/src/types/store/index.ts:20-63`, `webapp/channels/src/components/channel_view/channel_view.tsx:31-37`, `webapp/channels/src/actions/views/create_comment.tsx:58-71`).
**Find It In The Code:** Open the files above.

```ts
export type GlobalState = BaseGlobalState & {
    plugins: PluginsState;
    storage: StorageState;
    views: ViewsState;
};
// Local app state is explicitly layered onto shared state.
```

**The Aha Moment:** The best TypeScript tells future engineers where the system boundary is.
**Socratic Checkpoint:** What does `GlobalState` extend? What are webapp-only slices? Where does `any` appear? Where does a cast hide draft-to-post conversion? What type would you add?

How to self-grade: cite global state (`webapp/channels/src/types/store/index.ts:20-24`), thunk types (`webapp/channels/src/types/store/index.ts:44-63`), `any` in `ChannelView` (`webapp/channels/src/components/channel_view/channel_view.tsx:31-37`), and `as unknown as Post` (`webapp/channels/src/actions/views/create_comment.tsx:58-71`).
**Connects To:** Mission 23 because missing tests often live where types are weak.

