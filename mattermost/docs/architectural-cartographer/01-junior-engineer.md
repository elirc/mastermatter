# Junior Engineer Guide

## Setup And Run

The repo describes Mattermost as Go plus React with PostgreSQL (`README.md:1-3`). The webapp uses npm workspaces and says to install dependencies from `webapp/` with `npm install` (`webapp/README.md:5-23`). The channel webapp package exposes scripts for `build`, `run`, `dev-server`, `test`, `check`, and `check-types` (`webapp/channels/package.json:172-180`). The server Makefile starts Docker for local development and skips it only in CI or when `MM_NO_DOCKER=true` (`server/Makefile:247-255`). The server development target runs setup, binaries, Go version validation, Docker, client symlink setup, then `go run` (`server/Makefile:602-609`). The client target delegates to the webapp Makefile and the combined target is `run: run-server run-client` (`server/Makefile:676-690`).

Reconstructed local procedure:

1. Install Go compatible with the server module and Node/npm compatible with the checked-in lockfiles; the server module declares Go `1.26.2` (`server/go.mod:1-3`), and the webapp is an npm workspace (`webapp/package.json` `"workspaces"`, L87+) with a single lockfile at `webapp/package-lock.json` — `webapp/channels/` has no lockfile of its own.
2. From `webapp/`, run `npm install`; the webapp README says workspace dependencies are installed from that folder (`webapp/README.md:5-23`).
3. From `server/`, run `make start-docker` to start local development containers unless intentionally using `MM_NO_DOCKER=true` (`server/Makefile:247-255`).
4. From `server/`, run `make run-server` for the Go server (`server/Makefile:602-609`).
5. From `server/`, run `make run-client` for the webapp watcher (`server/Makefile:676-679`).
6. Use `make run` when you want both server and client targets together (`server/Makefile:690`).

Environment gap: the repo points to external developer setup docs instead of a complete checked-in setup guide (`README.md:33-37`, `webapp/README.md:25-28`). The checked-in Makefile provides executable setup behavior, but local prerequisites and seed-account instructions are not fully documented in-repo.

## Folder Orientation

Frontend top level:

- `webapp/` owns the web application workspaces and package management (`webapp/README.md:1-23`).
- `webapp/channels/src/components/` owns React components such as root routing, channel view, header, sidebar, post view, and editor (`webapp/channels/src/components/root/root.tsx:51-80`, `webapp/channels/src/components/channel_view/channel_view.tsx:21-25`).
- `webapp/channels/src/actions/` owns app-specific thunks and view actions; `create_comment.tsx` turns a draft into a post or command (`webapp/channels/src/actions/views/create_comment.tsx:40-123`, `webapp/channels/src/actions/views/create_comment.tsx:177-208`).
- `webapp/channels/src/packages/mattermost-redux/` contains shared Redux actions/reducers/selectors used by the webapp; post creation there implements optimistic UI (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`).
- `webapp/platform/client/` contains typed HTTP client methods such as `createPost` (`webapp/platform/client/src/client4.ts:2420-2434`).
- `webapp/platform/types/` contains shared TypeScript domain types such as `Post` (`webapp/platform/types/src/posts.ts:90-119`).

Backend top level:

- `server/cmd/mattermost/` starts the binary and registers server commands (`server/cmd/mattermost/main.go:19-22`, `server/cmd/mattermost/commands/server.go:27-39`).
- `server/channels/api4/` registers HTTP API routes and handlers (`server/channels/api4/api.go:18-80`, `server/channels/api4/post.go:23-57`).
- `server/channels/web/` wraps handlers with session, MFA, compression, context, audit, and error behavior (`server/channels/web/handlers.go:68-83`, `server/channels/web/handlers.go:565-581`, `server/channels/web/context.go:19-26`).
- `server/channels/app/` owns business logic such as creating posts, invoking plugins, preparing posts, and sending events (`server/channels/app/post.go:162-488`).
- `server/channels/store/` defines store interfaces (`server/channels/store/store.go:699-760`).
- `server/channels/store/sqlstore/` implements SQL-backed stores, including posts (`server/channels/store/sqlstore/post_store.go:33-41`, `server/channels/store/sqlstore/post_store.go:159-325`).
- `server/channels/db/migrations/postgres/` defines PostgreSQL schema and indexes (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:1-34`).

## One Level Deeper: Important Frontend Folders

`components/root` is the route and shell layer. It waits for config/me, initializes products and plugins, then mounts routes and the main logged-in shell (`webapp/channels/src/components/root/root.tsx:108-119`, `webapp/channels/src/components/root/root.tsx:231-247`, `webapp/channels/src/components/root/root.tsx:305-470`).

`components/channel_view` is the channel workspace center. It renders header, banners, bookmarks, post list, and the create-post editor, with archived/deactivated/restricted states changing the composer (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`).

`components/advanced_text_editor` is the message composer. It coordinates draft changes, preview, labels, keyboard handling, file upload UI, send button, footer, and submit hook (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:355-459`, `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`).

## One Level Deeper: Important Backend Folders

`api4` maps domain route groups to handlers. `Routes` includes channel and post routers, and `InitPost` binds HTTP methods to post handlers (`server/channels/api4/api.go:18-80`, `server/channels/api4/api.go:234-238`, `server/channels/api4/post.go:23-57`).

`app` is the business layer. `CreatePost` performs shared-channel restrictions, burn-on-read checks, deduplication, parent validation, plugin hooks, embed generation, persistence, file attachment, notification/event handling, and metadata sanitization (`server/channels/app/post.go:162-488`).

`store/sqlstore` is the persistence implementation. `SqlPostStore` has a reusable `postsQuery`, validates posts, inserts them in chunks, updates threads, saves priority/persistent notification data, and updates channel counters (`server/channels/store/sqlstore/post_store.go:33-41`, `server/channels/store/sqlstore/post_store.go:159-325`).

## Frontend Entry Walkthrough

```tsx
// webapp/channels/src/root.tsx:8-23
window.publicPath = process.env.PUBLIC_PATH || window.publicPath || '/static/';
// The app chooses the webpack asset base before importing the rest of the app.

__webpack_public_path__ = window.publicPath;
// Webpack uses this global when resolving lazy-loaded chunks.

window.basename = window.publicPath.substr(0, window.publicPath.length - '/static/'.length);
// React Router needs the server subpath without waiting for Redux config.

import('./entry');
// The real React app is loaded after the public path is ready.
```

```tsx
// webapp/channels/src/entry.tsx:31-60
function preRenderSetup(onPreRenderSetupReady: () => void) {
    window.onerror = (...) => {
        store.dispatch(logError(...));
        // Global JS crashes become visible developer errors in the app.
    };

    setCSRFFromCookie();
    // The client prepares CSRF protection before API calls.

    onPreRenderSetupReady();
}

function renderReactRootComponent() {
    ReactDOM.render(<App/>, document.getElementById('root')!);
    // React 18 is intentionally mounted with the legacy API because automatic batching breaks some components.
}
```

```tsx
// webapp/channels/src/components/app.tsx:17-27
const App = () => (
    <Provider store={store}>
        {/* Redux state is available to every connected component and hook. */}
        <Router history={getHistory()}>
            {/* A shared history object drives react-router-dom v5 routing. */}
            <Root/>
        </Router>
    </Provider>
);
```

## Backend Entry Walkthrough

```go
// server/cmd/mattermost/main.go:19-22
func main() {
    if err := commands.Run(os.Args[1:]); err != nil {
        os.Exit(1)
    }
}
```

```go
// server/cmd/mattermost/commands/server.go:39-104
func serverCmdF(command *cobra.Command, args []string) error {
    configStore, err := config.NewStoreFromDSN(...)
    // Server boot starts by loading config from the configured DSN.

    return runServer(configStore, interruptChan)
}

func runServer(configStore *config.Store, interruptChan chan os.Signal) error {
    server, err := app.NewServer(options...)
    // The app server owns routers, services, jobs, store, and platform services.

    _, err = api4.Init(server)
    // HTTP API routes are registered before the server starts.

    wsapi.Init(server)
    web.New(server)
    err = server.Start()
    // Websocket API, static/web handlers, and HTTP listener all attach here.
}
```

## TypeScript Orientation

Mattermost uses shared domain types. A frontend post has IDs, timestamps, channel/thread fields, message, type, props, metadata, pending ID, reply count, and optional file IDs (`webapp/platform/types/src/posts.ts:90-119`). The app's `GlobalState` extends shared Mattermost Redux state with webapp-specific `plugins`, `storage`, and `views` slices (`webapp/channels/src/types/store/index.ts:20-24`). Thunk types are specialized so app actions and shared Redux actions can coexist (`webapp/channels/src/types/store/index.ts:44-63`).

## Three React Component Anatomies

```tsx
// Simple component: webapp/channels/src/components/advanced_create_post/advanced_create_post.tsx:15-31
const AdvancedCreatePost = () => {
    const currentChannelId = useSelector(getCurrentChannelId);
    // The component reads one fact from Redux: which channel is active.

    if (!currentChannelId) {
        return null;
        // No channel means no composer.
    }

    return <AdvancedTextEditor location={Locations.CENTER} rootId={''} channelId={currentChannelId}/>;
    // It delegates the real editor behavior to AdvancedTextEditor.
};
```

```tsx
// Medium component: webapp/channels/src/components/channel_header/channel_header_title.tsx:32-121
const ChannelHeaderTitle = ({dmUser, gmMembers, remoteNames}: Props) => {
    const channel = useSelector(getCurrentChannel);
    // The title follows the current channel, not a parent prop.

    if (!channel) {
        return null;
    }

    const isDirect = (channel.type === Constants.DM_CHANNEL);
    const isGroup = (channel.type === Constants.GM_CHANNEL);
    // Mattermost channel display rules differ for normal channels, DMs, and GMs.

    let channelTitle: ReactNode = channel.display_name;
    if (isDirect) {
        channelTitle = <ChannelHeaderTitleDirect dmUser={dmUser}/>;
    } else if (isGroup) {
        channelTitle = <ChannelHeaderTitleGroup gmMembers={gmMembers}/>;
    }

    return <ChannelHeaderMenu dmUser={dmUser} gmMembers={gmMembers} sharedIcon={sharedIcon} archivedIcon={archivedIcon}/>;
    // The menu owns the visible dropdown title assembly.
};
```

```tsx
// Complex component: webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:355-459
const [handleSubmit, errorClass] = useSubmit(...);
// The editor delegates submission policy to a hook instead of keeping all rules inline.

const handleSubmitWithErrorHandling = useCallback((submittingDraft, schedulingInfo, options) => {
    handleSubmit(submittingDraft, schedulingInfo, options);
    // The hook decides whether to create, edit, schedule, or block.
}, [errorClass, handleSubmit]);

const handleSubmitWithEvent = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    handleSubmitWithErrorHandling();
}, [handleSubmitWithErrorHandling]);
// The form submit path and keyboard/send-button path converge on the same handler.
```

## Three Backend Route/Controller Anatomies

```go
// Route registration: server/channels/api4/post.go:23-57
func (api *API) InitPost() {
    api.BaseRoutes.Posts.Handle("", api.APISessionRequired(createPost)).Methods(http.MethodPost)
    // POST /api/v4/posts requires a session and calls createPost.

    api.BaseRoutes.PostsForChannel.Handle("", api.APISessionRequired(getPostsForChannel)).Methods(http.MethodGet)
    // GET /api/v4/channels/{channel_id}/posts returns channel history.
}
```

```go
// Simple route logic: server/channels/api4/post.go:96-130
func createPost(c *Context, w http.ResponseWriter, r *http.Request) {
    var post model.Post
    json.NewDecoder(r.Body).Decode(&post)
    // Decode JSON from the frontend into the backend model.

    post.SanitizeInput()
    post.UserId = c.AppContext.Session().UserId
    // Never trust the browser's user_id; bind the post to the authenticated session.

    createPostChecks("Api4.createPost", c, &post)
    // Permission and feature checks happen before app-layer creation.

    rp, isMemberForPreviews, err := c.App.CreatePostAsUser(...)
    // Business logic is delegated to the app layer.
}
```

```go
// Store controller: server/channels/store/sqlstore/post_store.go:159-325
func (s *SqlPostStore) SaveMultiple(rctx request.CTX, posts []*model.Post) ([]*model.Post, int, error) {
    for idx, post := range posts {
        post.PreSave()
        post.IsValid(maxPostSize)
        post.ValidateProps(rctx.Logger())
        // The store validates before writing.
    }

    transaction, err := s.GetMaster().Begin()
    // Post insert, thread updates, priority rows, and counters are grouped around a transaction.

    builder := s.getQueryBuilder().Insert("Posts").Columns(postSliceColumns()...)
    transaction.ExecBuilder(builder)
}
```

## Domain Glossary

- Team: a workspace grouping channels and users; routes include `/api/v4/teams` and team-scoped channels (`server/channels/api4/api.go:31-49`, `server/channels/api4/api.go:206-225`).
- Channel: a conversation space; API routes include channels, channel members, bookmarks, views, and channel posts (`server/channels/api4/api.go:42-57`, `server/channels/api4/api.go:217-238`).
- Post: a message or system event persisted in `Posts`; frontend type fields include `id`, `channel_id`, `root_id`, `message`, `type`, `props`, `metadata`, and `pending_post_id` (`webapp/platform/types/src/posts.ts:90-119`).
- Root post: a top-level post with empty `root_id`; replies have a non-empty `root_id`, and server creation validates parent/root relationships (`server/channels/app/post.go:275-295`).
- Pending post: optimistic client-side post ID used before the server returns the real ID (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-258`).
- Ephemeral post: a server-generated temporary message sent to a user, with route support at `/posts/ephemeral` (`server/channels/api4/post.go:27-28`, `server/channels/api4/post.go:183-237`).
- Burn-on-read post: a post type with special temporary storage and read restrictions (`server/public/model/post.go:61-63`, `server/channels/store/sqlstore/post_store.go:179-199`).
- Plugin hook: extension point that can inspect, replace, reject, or react to messages (`webapp/channels/src/actions/views/create_comment.tsx:93-99`, `server/channels/app/post.go:323-348`, `server/channels/app/post.go:403-414`).
- ETag: cache validator used for post-list reads (`server/channels/api4/post.go:291-319`, `server/channels/store/sqlstore/post_store.go:951-968`).

## Junior Socratic Checkpoint

1. Why does the webapp set `window.publicPath` before importing `entry.tsx`?
2. Which file mounts React, and why is the mount API notable?
3. Which component decides whether the create-post composer is shown?
4. Where is the frontend `Post` type defined?
5. Why does the server overwrite `post.UserId`?
6. Which backend layer writes to the `Posts` table?
7. What is a pending post ID?

### How To Self-Grade

Strong answers cite the exact files: public path in `root.tsx` (`webapp/channels/src/root.tsx:8-23`), React mount in `entry.tsx` (`webapp/channels/src/entry.tsx:55-60`), composer gating in `ChannelView` (`webapp/channels/src/components/channel_view/channel_view.tsx:112-234`), type definition in `posts.ts` (`webapp/platform/types/src/posts.ts:90-119`), session-bound user ID in `api4/post.go` (`server/channels/api4/post.go:103-105`), SQL write in `SqlPostStore` (`server/channels/store/sqlstore/post_store.go:159-325`), and optimistic pending IDs in Redux (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-258`).

