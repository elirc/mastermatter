# Tier 1 Junior Missions

### Mission 1: The App's Heartbeat
**Tier:** Junior
**Time Estimate:** 25 minutes
**Goal:** Trace how the browser starts the Mattermost webapp.
**The Concept:** App boot is like opening a channel before anyone speaks: first the room exists, then the participants and messages arrive.
**Design Intent Before You Read the Code:** `root.tsx` prepares asset paths, `entry.tsx` handles pre-render setup, and `App` connects Redux plus routing; breaking this path can blank the whole app (`webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`, `webapp/channels/src/components/app.tsx:17-27`).
**Find It In The Code:** Open `webapp/channels/src/root.tsx:8-23`, `webapp/channels/src/entry.tsx:31-78`, and `webapp/channels/src/components/app.tsx:17-27`.

```tsx
// webapp/channels/src/root.tsx:12-23
window.publicPath = process.env.PUBLIC_PATH || window.publicPath || '/static/';
// Choose where lazy chunks and static assets are loaded from.

__webpack_public_path__ = window.publicPath;
// Hand the path to webpack before any dynamic imports run.

window.basename = window.publicPath.substr(0, window.publicPath.length - '/static/'.length);
// Give the router the server subpath.

import('./entry');
// Start the real app only after path setup is complete.
```

**The Aha Moment:** Boot code is infrastructure code: tiny, early, and extremely high impact.
**Socratic Checkpoint:** Why is `entry` imported dynamically? What does `setCSRFFromCookie` prepare? Why does `App` wrap `Root` in `Provider`? What breaks if `window.basename` is wrong? Why does React mount happen after DOMContentLoaded?

How to self-grade: strong answers mention webpack chunk paths (`webapp/channels/src/root.tsx:8-23`), CSRF setup (`webapp/channels/src/entry.tsx:50-52`), Redux provider (`webapp/channels/src/components/app.tsx:17-23`), router basename/subpath (`webapp/channels/src/root.tsx:17-21`), and DOM readiness (`webapp/channels/src/entry.tsx:65-78`).
**Connects To:** Mission 2 and Mission 8 because folder navigation and routing make more sense after boot.

### Mission 2: The Folder Mental Map
**Tier:** Junior
**Time Estimate:** 30 minutes
**Goal:** Build a first map of frontend, backend, API, store, and types.
**The Concept:** A Mattermost channel has participants with roles; a codebase has folders with roles.
**Design Intent Before You Read the Code:** Frontend work usually begins under `webapp/channels/src`, shared client/types under `webapp/platform`, backend API under `server/channels/api4`, business logic under `server/channels/app`, and persistence under `server/channels/store/sqlstore` (`webapp/README.md:1-23`, `server/channels/api4/api.go:18-80`, `server/channels/app/server.go:90-120`, `server/channels/store/sqlstore/post_store.go:33-41`).
**Find It In The Code:** Open `webapp/README.md:1-23`, `server/channels/api4/api.go:18-80`, `server/channels/app/server.go:90-120`, and `server/channels/store/sqlstore/post_store.go:33-41`.

```go
// server/channels/api4/api.go:18-24
type Routes struct {
    Root *mux.Router
    APIRoot *mux.Router
    Users *mux.Router
    // The API layer is a map of named route groups.
}
```

**The Aha Moment:** Folder names become useful only when you attach ownership to them.
**Socratic Checkpoint:** Which folder owns HTTP routes? Which folder owns business behavior? Which folder owns SQL? Where are shared frontend types? Why is `webapp/README.md` important for package boundaries?

How to self-grade: cite `api4` routes (`server/channels/api4/api.go:18-80`), app server/service fields (`server/channels/app/server.go:90-120`), SQL store struct (`server/channels/store/sqlstore/post_store.go:33-41`), shared `Post` type (`webapp/platform/types/src/posts.ts:90-119`), and workspaces (`webapp/README.md:5-23`).
**Connects To:** Mission 3 and Mission 5 because types and routes depend on folder ownership.

### Mission 3: TypeScript Is a Contract
**Tier:** Junior
**Time Estimate:** 30 minutes
**Goal:** Read the `Post` type as a cross-layer promise.
**The Concept:** A post type is the envelope Mattermost passes through the channel mail system.
**Design Intent Before You Read the Code:** The browser needs enough fields to render, send, retry, and reconcile posts; the server and database have parallel but not identical shapes (`webapp/platform/types/src/posts.ts:76-119`, `server/public/model/post.go:28-118`, `server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).
**Find It In The Code:** Open `webapp/platform/types/src/posts.ts:76-119`.

```ts
// webapp/platform/types/src/posts.ts:90-119
export type Post = {
    id: string;              // Stable server identity after creation.
    channel_id: string;      // Which conversation owns the message.
    root_id: string;         // Empty for root posts, set for replies.
    message: string;         // User-visible content.
    pending_post_id: string; // Temporary client identity during optimistic send.
    metadata: PostMetadata;  // Embeds, files, reactions, priority, translations.
    failed?: boolean;        // Client-side failure display state.
};
```

**The Aha Moment:** Types are not paperwork; they are a map of system promises.
**Socratic Checkpoint:** Which fields identify the post? Which fields place it in a channel/thread? Which field supports optimistic UI? Which field carries rich generated data? Which field is client-only failure state?

How to self-grade: cite identity, channel/thread, pending, metadata, and failed fields from `Post` (`webapp/platform/types/src/posts.ts:90-119`).
**Connects To:** Mission 6 and Mission 17 because props and hidden type work build on contracts.

### Mission 4: Your First React Component
**Tier:** Junior
**Time Estimate:** 25 minutes
**Goal:** Understand a tiny component that connects Redux state to UI.
**The Concept:** `AdvancedCreatePost` is a channel desk clerk: it checks which room you are in, then hands you the right message form.
**Design Intent Before You Read the Code:** It should not own editor behavior; it only finds the current channel and renders the editor (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`).
**Find It In The Code:** Open `webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`.

```tsx
const AdvancedCreatePost = () => {
    const currentChannelId = useSelector(getCurrentChannelId);
    // Read the current channel from Redux.

    if (!currentChannelId) {
        return null;
        // No active channel means no post composer.
    }

    return <AdvancedTextEditor location={Locations.CENTER} rootId={''} channelId={currentChannelId}/>;
    // Delegate all editing/submission behavior.
};
```

**The Aha Moment:** Good small components often translate state into props and then get out of the way.
**Socratic Checkpoint:** What state does this component read? What does it render? What does `rootId=''` imply? Why is `React.memo` used? What would be a bad responsibility to add here?

How to self-grade: cite selector use, null guard, editor props, and memo export (`webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31`).
**Connects To:** Mission 6 and Mission 9 because props and state ownership start here.

### Mission 5: Your First Node.js Route
**Tier:** Junior
**Time Estimate:** 30 minutes
**Goal:** Correct the mental model: this app's main backend routes are Go, not Node.js.
**The Concept:** The webapp uses Node tooling, but the request desk is a Go API router.
**Design Intent Before You Read the Code:** If a prompt asks for a Node route, note the gap and map the equivalent Go route/controller pattern (`webapp/channels/package.json:172-180`, `server/channels/api4/post.go:23-57`).
**Find It In The Code:** Open `server/channels/api4/post.go:23-57`.

```go
func (api *API) InitPost() {
    api.BaseRoutes.Posts.Handle("", api.APISessionRequired(createPost)).Methods(http.MethodPost)
    // This is the route for creating a post.

    api.BaseRoutes.PostsForChannel.Handle("", api.APISessionRequired(getPostsForChannel)).Methods(http.MethodGet)
    // This is the route for reading channel posts.
}
```

**The Aha Moment:** In this repo, Node builds the frontend; Go serves the product API.
**Socratic Checkpoint:** What evidence shows Node is used for frontend scripts? What evidence shows Go owns API routes? What does `APISessionRequired` imply? What is the route path for creating posts? What would a Node route look like if this were an Express app?

How to self-grade: cite npm scripts (`webapp/channels/package.json:172-180`), Go route registration (`server/channels/api4/post.go:23-57`), and session wrapper implementation (`server/channels/web/handlers.go:565-581`).
**Connects To:** Mission 12 and Mission 13 because API contracts and middleware are next.

### Mission 6: Props Are a Typed Contract
**Tier:** Junior
**Time Estimate:** 30 minutes
**Goal:** Read component props as an agreement between parent, component, and user behavior.
**The Concept:** Props are like channel permissions: explicit inputs decide what the component may show or do.
**Design Intent Before You Read the Code:** `SidebarChannelLink` receives channel data, unread data, RHS state, and action callbacks; the component should not fetch everything itself (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:38-84`).
**Find It In The Code:** Open `webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:38-84` and `158-260`.

```tsx
type Props = WrappedComponentProps & {
    channel: Channel;       // Domain object for this row.
    link: string;           // Route destination.
    unreadMentions: number; // Badge/accessibility state.
    actions: {
        clearChannelSelection: () => void;
        closeRightHandSide: () => void;
        // Parent/container injects behavior.
    };
};
```

**The Aha Moment:** A prop list tells you what the component knows and what it refuses to own.
**Socratic Checkpoint:** Which props are data? Which props are behavior? Which props affect accessibility? Which props affect routing? Which action closes RHS?

How to self-grade: cite data props and action props (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:38-84`), aria behavior (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:132-156`), and click behavior (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:158-184`).
**Connects To:** Mission 8 and Mission 16 because navigation and composition are prop-driven.

### Mission 7: Following Data Into the App
**Tier:** Junior
**Time Estimate:** 35 minutes
**Goal:** Follow a draft message until it becomes a post object.
**The Concept:** A draft is a message in the lobby; `submitPost` gives it a badge, channel, author, timestamp, and metadata so it can enter the system.
**Design Intent Before You Read the Code:** Draft-to-post conversion should happen once, near submission, before API calls and after local validation (`webapp/channels/src/actions/views/create_comment.tsx:40-123`).
**Find It In The Code:** Open `webapp/channels/src/actions/views/create_comment.tsx:40-123`.

```tsx
let post = {
    file_ids: [],
    message: draft.message,
    channel_id: channelId,
    root_id: rootId,
    pending_post_id: `${userId}:${time}`,
    user_id: userId,
    create_at: time,
} as unknown as Post;
// The draft becomes the transport object used by Redux and the API client.
```

**The Aha Moment:** Data tracing is easiest when you watch names change: draft -> post -> pending post -> created post.
**Socratic Checkpoint:** Which function builds the post? Where does the user ID come from on the client? Where is pending ID created? What permissions affect mentions? Where do plugin hooks run?

How to self-grade: cite post construction (`webapp/channels/src/actions/views/create_comment.tsx:40-71`), mention checks (`webapp/channels/src/actions/views/create_comment.tsx:73-91`), hooks (`webapp/channels/src/actions/views/create_comment.tsx:93-99`), and dispatch (`webapp/channels/src/actions/views/create_comment.tsx:100-123`).
**Connects To:** Mission 14 because this is the first third of the full-stack trace.

### Mission 8: Navigation Is the App's Skeleton
**Tier:** Junior
**Time Estimate:** 35 minutes
**Goal:** Understand where routes and the logged-in shell are assembled.
**The Concept:** Routes are Mattermost's hallway map: login, admin, team channels, popouts, and product routes all branch from one skeleton.
**Design Intent Before You Read the Code:** `Root` should not render main routes until config, user, products, and plugins are ready (`webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:305-470`).
**Find It In The Code:** Open `webapp/channels/src/components/root/root.tsx:305-470`.

```tsx
if (!this.state.shouldMountAppRoutes) {
    return <div/>;
    // Avoid rendering the app shell before config/products/plugins are ready.
}

<Switch>
    <Route path={'/login'} component={Login}/>
    <LoggedInRoute path={'/terms_of_service'} component={TermsOfService}/>
    // Public, guarded, and product routes live together here.
</Switch>
```

**The Aha Moment:** Routing is not just URLs; it is when the app decides what data and shell must exist first.
**Socratic Checkpoint:** What sets `shouldMountAppRoutes`? Which routes are public? Which routes are logged-in? Where are product routes mounted? What components are always in the logged-in shell?

How to self-grade: cite initialization (`webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:231-247`), route switch (`webapp/channels/src/components/root/root.tsx:315-428`), and product routes (`webapp/channels/src/components/root/root.tsx:429-470`).
**Connects To:** Mission 9 because route state and global state shape interact.

