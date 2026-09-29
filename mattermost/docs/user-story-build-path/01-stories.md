# User Stories

## Story 1: Rename The Archived Channel Empty-State Action
**Difficulty:** Easy
**Estimated Time:** 1 hour
**Skills You'll Practice:** reading JSX branches, i18n message awareness, conditional rendering
**The Story:** As a channel member, I want the archived-channel action text to be clearer so that I understand I am leaving the archived view, not deleting or restoring the channel.
**Acceptance Criteria:**
- [ ] The archived channel message still appears when `channelIsArchived` is true.
- [ ] The button text is updated only for archived/deactivated channel composer-blocking states.
- [ ] No active channel composer text changes.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/channel_view/channel_view.tsx` - owns archived/deactivated/restricted composer branches (`webapp/channels/src/components/channel_view/channel_view.tsx:112-211`).
- `webapp/channels/src/i18n/en.json` - contains extracted message strings when i18n extraction is run; after editing it, repo instructions require `make i18n-extract` from server context if this file changes (`server/AGENTS.md:1-3`).
**High-Level Implementation Plan:**
1. In `ChannelView.render`, find the archived and deactivated branches around the `FormattedMessage` button labels (`webapp/channels/src/components/channel_view/channel_view.tsx:130-169`).
2. Update only the `defaultMessage` and message ID if product wording requires a new string.
3. If `i18n/en.json` changes, run the required extraction command from `server/`.
**Tips:**
- Keep the branch structure intact; this story is wording, not behavior (`webapp/channels/src/components/channel_view/channel_view.tsx:112-211`).
- Check both deactivated archived and archived branches because they render similar buttons (`webapp/channels/src/components/channel_view/channel_view.tsx:114-172`).
- Do not touch the normal composer branch that renders `AdvancedCreatePost` (`webapp/channels/src/components/channel_view/channel_view.tsx:200-211`).
**What Could Go Wrong:**
- You update only one archived branch and the other still says the old text.
- You edit extracted i18n output manually and forget extraction ordering.
**Stretch Goal:** Add a focused component test that verifies archived channel button text.
**Connects To:** Story 2 because both are small UI changes in channel-facing components.

## Story 2: Add A Shared-Channel Label To The Sidebar Row
**Difficulty:** Easy
**Estimated Time:** 1.5 hours
**Skills You'll Practice:** props, conditional rendering, accessibility labels
**The Story:** As a user in shared channels, I want the sidebar row to expose shared-channel context more clearly so that I can distinguish local and remote conversations.
**Acceptance Criteria:**
- [ ] Shared channels display an additional accessible label or tooltip cue.
- [ ] Non-shared channels render exactly as before.
- [ ] The existing shared-channel icon still renders.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx` - owns sidebar channel row props, shared indicator, aria label, and render (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:38-84`, `webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:132-260`).
**High-Level Implementation Plan:**
1. Extend `getAriaLabel` to append shared-channel wording when `isSharedChannel` is true (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:132-156`).
2. Leave existing `SharedChannelIndicator` rendering intact (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:246-252`).
3. Verify click behavior still delegates to `handleSelectChannel` (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:158-184`).
**Tips:**
- Use `intl.formatMessage` as existing aria code does (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:141-152`).
- Do not fetch remote names in render; fetch behavior already exists in lifecycle methods (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:105-123`).
- Keep the label lowercase if you append to `getAriaLabel`, because the method lowercases the final string (`webapp/channels/src/components/sidebar/sidebar_channel/sidebar_channel_link/sidebar_channel_link.tsx:155-156`).
**What Could Go Wrong:**
- Adding visible text may overcrowd the sidebar row.
- Changing click markup can break modifier-key multi-select behavior.
**Stretch Goal:** Add a test for shared-channel aria text.
**Connects To:** Story 3 because both require careful UI changes without touching backend behavior.

## Story 3: Show A Small "Archived" Cue In The Channel Header Title
**Difficulty:** Easy
**Estimated Time:** 2 hours
**Skills You'll Practice:** component composition, conditional icons, direct/group channel display
**The Story:** As a channel member viewing an archived channel, I want the header title to make archive state obvious so that I do not try to post in a locked conversation.
**Acceptance Criteria:**
- [ ] Archived channels show an archive cue in the header.
- [ ] Direct messages, group messages, and regular channels keep their correct title behavior.
- [ ] Bot DM header layout still works.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/channel_header/channel_header_title.tsx` - owns archived icon, direct/group title choice, bot DM layout, and shared-channel icon (`webapp/channels/src/components/channel_header/channel_header_title.tsx:32-121`).
**High-Level Implementation Plan:**
1. Inspect existing `channelIsArchived` and `archivedIcon` logic (`webapp/channels/src/components/channel_header/channel_header_title.tsx:43-56`).
2. Add the cue near existing title/menu rendering without changing direct/group title selection (`webapp/channels/src/components/channel_header/channel_header_title.tsx:69-74`, `webapp/channels/src/components/channel_header/channel_header_title.tsx:101-117`).
3. Verify bot DM branch still includes archived icon (`webapp/channels/src/components/channel_header/channel_header_title.tsx:76-99`).
**Tips:**
- Reuse `getArchiveIconComponent`; do not introduce a new icon source for the same concept (`webapp/channels/src/components/channel_header/channel_header_title.tsx:17-19`, `webapp/channels/src/components/channel_header/channel_header_title.tsx:47-56`).
- Keep shared-channel indicator behavior separate (`webapp/channels/src/components/channel_header/channel_header_title.tsx:58-67`).
- Avoid changing `ChannelHeaderMenu` props unless the menu owns the final visible title in your chosen UI location (`webapp/channels/src/components/channel_header/channel_header_title.tsx:111-116`).
**What Could Go Wrong:**
- The cue appears twice because archived icon is already passed into `ChannelHeaderMenu`.
- Bot DM header loses profile picture or bot tag due to branch edits.
**Stretch Goal:** Add a tooltip explaining that archived channels cannot receive new posts.
**Connects To:** Story 4 because channel header work prepares you for reading richer existing data.

## Story 4: Add A File Count Hint To The Composer When Attachments Are Present
**Difficulty:** Medium
**Estimated Time:** 3 hours
**Skills You'll Practice:** existing draft data, editor UI composition, conditional UI
**The Story:** As a user composing a message with uploads, I want to see how many files are attached so that I can confirm I am sending the right payload.
**Acceptance Criteria:**
- [ ] The composer shows a count when `draft.fileInfos.length > 0`.
- [ ] The count disappears when all files are removed.
- [ ] Scheduled, normal, and RHS comment editors do not break.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx` - owns editor body, attachments, labels, textbox, actions, footer (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:767-910`).
- `webapp/channels/src/components/advanced_text_editor/footer.tsx` - may be a better surface if the count belongs near submit/footer (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:896-904`).
- `webapp/channels/src/components/advanced_text_editor/use_submit.tsx` - shows how files become `file_ids` during submit (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:271-280`).
**High-Level Implementation Plan:**
1. Locate where `attachmentPreview` and footer render in `AdvancedTextEditor` (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:853-904`).
2. Add a small conditional count using `draft.fileInfos.length`.
3. Ensure the UI is hidden for zero files and does not block existing `FileLimitStickyBanner` behavior (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:774-776`).
4. Add or update a focused editor test if one already covers attachments.
**Tips:**
- `draft.fileInfos` is already used for submit file IDs (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:271-280`).
- Do not compute from uploaded DOM elements; use draft state.
- Keep the wording compact; the composer is dense.
**What Could Go Wrong:**
- Count includes uploads still in progress when the story only asks for attached files.
- UI appears in edit mode where file behavior differs.
**Stretch Goal:** Show separate counts for uploaded files and uploads in progress.
**Connects To:** Story 5 because both use existing data without new APIs.

## Story 5: Show Channel Policy Status In The Header
**Difficulty:** Medium
**Estimated Time:** 4 hours
**Skills You'll Practice:** custom hooks, existing API actions, loading/error states
**The Story:** As a user in policy-enforced channels, I want the channel header to show policy status so that I know restrictions may apply.
**Acceptance Criteria:**
- [ ] Policy-enforced channels show a discreet policy indicator.
- [ ] Channels without policy enforcement show nothing.
- [ ] Loading and error states do not block normal header rendering.
**Files You'll Likely Touch:**
- `webapp/channels/src/hooks/useChannelSystemPolicies.ts` - fetches system policies for a channel (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:25-103`).
- `webapp/channels/src/components/channel_header/channel_header.tsx` - owns header lifecycle and rendered header controls (`webapp/channels/src/components/channel_header/channel_header.tsx:40-160`).
- `webapp/channels/src/components/channel_header/channel_header_title.tsx` - may own the title-adjacent placement (`webapp/channels/src/components/channel_header/channel_header_title.tsx:32-121`).
**High-Level Implementation Plan:**
1. Decide whether the indicator belongs in `ChannelHeader` or `ChannelHeaderTitle`.
2. Use `useChannelSystemPolicies` from a function component or add a small child component under the header (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:25-103`).
3. Render only when policies exist or `channel.policy_enforced` is true (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:31-52`).
4. Keep error state quiet but inspectable through tooltip or console-free UI.
**Tips:**
- Do not call hooks inside class components; wrap the hook in a function child if needed.
- The hook already returns `{policies, loading, error}` (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:14-18`, `webapp/channels/src/hooks/useChannelSystemPolicies.ts:103-103`).
- Avoid adding a new API until existing `getAccessControlPolicy` path proves insufficient (`webapp/channels/src/hooks/useChannelSystemPolicies.ts:10-12`, `webapp/channels/src/hooks/useChannelSystemPolicies.ts:52-70`).
**What Could Go Wrong:**
- Calling a hook from `ChannelHeader` directly fails because it is a class component.
- Fetching on every render causes repeated network calls.
**Stretch Goal:** Tooltip lists inherited parent policy names.
**Connects To:** Story 6 because policy display prepares you for new state/API work.

## Story 6: Add A Client-Side "Retry Failed Post" Action
**Difficulty:** Medium
**Estimated Time:** 5 hours
**Skills You'll Practice:** optimistic state, failed state, Redux thunks, UI actions
**The Story:** As a user whose message failed to send, I want to retry it from the failed post UI so that I do not have to copy and paste my message.
**Acceptance Criteria:**
- [ ] Failed pending posts show a retry action.
- [ ] Retry reuses the existing post creation path.
- [ ] Known server rejection cases still remove the failed post when appropriate.
- [ ] Duplicate retry clicks do not create duplicate posts.
**Files You'll Likely Touch:**
- `webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts` - owns optimistic create, success, and failure paths (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:179-326`).
- `webapp/channels/src/actions/post_actions.ts` - app wrapper for post creation and draft cleanup (`webapp/channels/src/actions/post_actions.ts:140-161`).
- `webapp/channels/src/components/post_view/failed_post_options` - likely owns failed post UI; inspect this folder before editing.
- `webapp/platform/client/src/client4.ts` - existing `createPost` client call (`webapp/platform/client/src/client4.ts:2420-2434`).
**High-Level Implementation Plan:**
1. Inspect failed post rendering under `post_view/failed_post_options`.
2. Add a retry UI action that dispatches existing `createPost` with the failed post payload.
3. Ensure pending ID behavior prevents duplicate sends (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:188-193`).
4. Preserve failure handling for root-deleted/read-only/plugin-dismiss cases (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:307-320`).
5. Add a focused test around duplicate retry prevention.
**Tips:**
- Reuse `PostActions.createPost`; do not write a parallel API call.
- Preserve `file_ids` retry logic for posts with files (`webapp/channels/src/packages/mattermost-redux/src/actions/posts.ts:223-246`).
- Watch `pending_post_id`; it is both UI identity and backend dedupe input (`server/channels/app/post.go:173-206`).
**What Could Go Wrong:**
- Retry creates a new pending ID and duplicates the failed row.
- Retry loses file attachments.
- Retry bypasses known rejection cleanup.
**Stretch Goal:** Add "edit and retry" that returns the failed message to the composer.
**Connects To:** Story 7 because both modify post state behavior.

## Story 7: Add A Lightweight "Send Later" State Before Scheduled Post Creation
**Difficulty:** Medium
**Estimated Time:** 6 hours
**Skills You'll Practice:** scheduling data, submit branching, UI state
**The Story:** As a user composing a message, I want a visible "send later selected" state before confirming schedule so that I do not accidentally schedule the wrong message.
**Acceptance Criteria:**
- [ ] Selecting scheduling info shows a visible state in the composer.
- [ ] Normal send path remains unchanged when no scheduling info exists.
- [ ] Scheduled submit still calls the existing scheduled-post creation path.
- [ ] Clearing the draft clears the send-later state.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/advanced_text_editor/send_button/send_button.tsx` - owns send button scheduling interaction (`webapp/channels/src/components/advanced_text_editor/send_button/send_button.tsx:24-37`, `webapp/channels/src/components/advanced_text_editor/send_button/send_button.tsx:88-88`).
- `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx` - owns send button and footer rendering (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:598-620`, `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:867-904`).
- `webapp/channels/src/components/advanced_text_editor/use_submit.tsx` - passes scheduling info into `onSubmit` (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:151-249`).
- `webapp/channels/src/actions/views/create_comment.tsx` - converts post to scheduled post when scheduling info exists (`webapp/channels/src/actions/views/create_comment.tsx:100-123`).
**High-Level Implementation Plan:**
1. Inspect how `SendButton` receives and passes `SchedulingInfo`.
2. Add local composer state for selected scheduling info.
3. Render a compact indicator near send controls.
4. Pass scheduling info to existing submit path.
5. Clear the state when `handleDraftChange` resets the draft (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:210-219`).
**Tips:**
- Scheduling is already supported in `submitPost`; use that branch (`webapp/channels/src/actions/views/create_comment.tsx:100-123`).
- Keep send button API small; avoid turning it into the owner of draft state.
- Treat edit mode separately because edit submit uses `editPost` (`webapp/channels/src/components/advanced_text_editor/use_submit.tsx:198-205`).
**What Could Go Wrong:**
- Normal send accidentally schedules because stale scheduling info remains.
- Indicator remains after a successful scheduled post.
**Stretch Goal:** Add a "clear scheduled time" icon button.
**Connects To:** Story 8 because scheduling touches frontend state and server-backed behavior.

## Story 8: Add A Post Metadata Field For "Needs Follow-Up"
**Difficulty:** Hard
**Estimated Time:** 10 hours
**Skills You'll Practice:** TypeScript contracts, API payloads, Go model review, metadata persistence, UI display
**The Story:** As a channel user, I want to mark a new post as needing follow-up so that teammates can scan important unresolved messages.
**Acceptance Criteria:**
- [ ] Composer can mark a post as needing follow-up.
- [ ] The field is sent in post metadata.
- [ ] Created posts display a follow-up marker.
- [ ] The marker survives refresh and post list fetch.
- [ ] Existing post priority behavior is not broken.
**Files You'll Likely Touch:**
- `webapp/platform/types/src/posts.ts` - add metadata type field (`webapp/platform/types/src/posts.ts:76-119`).
- `webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx` - add composer control (`webapp/channels/src/components/advanced_text_editor/advanced_text_editor.tsx:867-904`).
- `webapp/channels/src/actions/views/create_comment.tsx` - include metadata in post construction (`webapp/channels/src/actions/views/create_comment.tsx:58-71`).
- `webapp/platform/client/src/client4.ts` - confirm `createPost` serializes the field (`webapp/platform/client/src/client4.ts:2420-2434`).
- `server/channels/api4/post.go` - confirm decode/sanitize path preserves safe metadata (`server/channels/api4/post.go:96-181`).
- `server/channels/app/post.go` - confirm plugin replacement preserves protected metadata or decide where this field belongs (`server/channels/app/post.go:316-348`).
- `server/channels/store/sqlstore/post_store.go` - confirm post save handles metadata through model serialization (`server/channels/store/sqlstore/post_store.go:159-325`).
**High-Level Implementation Plan:**
1. Add the metadata type field in `PostMetadata`.
2. Add a composer toggle that writes the field into draft metadata.
3. Add field propagation in `submitPost`.
4. Verify `Client4.createPost` needs no custom serialization change.
5. Inspect backend model serialization and plugin replacement path.
6. Add display marker in post rendering after finding the post message component.
7. Add tests for submit payload and post display.
**Tips:**
- Use the existing priority metadata pattern as a guide (`webapp/platform/types/src/posts.ts:62-83`, `webapp/channels/src/actions/views/create_comment.tsx:67-69`).
- Be careful with plugin replacement metadata preservation (`server/channels/app/post.go:316-348`).
- Confirm whether metadata persists in existing `Props`/metadata serialization before adding a DB column.
**What Could Go Wrong:**
- Marker appears optimistically but disappears after server response.
- Plugin replacement drops the field.
- Field is added to TypeScript but not Go/model serialization.
**Stretch Goal:** Add a channel filter for follow-up posts.
**Connects To:** Story 9 because both require durable full-stack behavior.

## Story 9: Add A Channel-Level "Default Follow-Up" Setting
**Difficulty:** Hard
**Estimated Time:** 14 hours
**Skills You'll Practice:** new API endpoint, permissions, store update, frontend state, settings UI
**The Story:** As a channel admin, I want a channel setting that marks new posts as needing follow-up by default so that high-signal channels keep action items visible.
**Acceptance Criteria:**
- [ ] Channel admins can enable or disable the setting.
- [ ] Non-admin users cannot change it.
- [ ] New posts in the channel inherit the default unless the composer overrides it.
- [ ] The setting persists across server restart.
- [ ] API errors are shown in the UI.
**Files You'll Likely Touch:**
- `server/channels/api4/api.go` - route group patterns for channels/posts (`server/channels/api4/api.go:42-61`, `server/channels/api4/api.go:217-238`).
- `server/channels/api4/channel.go` - likely place for channel setting endpoints; inspect before editing.
- `server/channels/app/channel.go` - likely app-layer channel setting ownership; inspect before editing.
- `server/channels/store/store.go` - store interface updates if persistence changes (`server/channels/store/store.go:699-760` shows interface pattern).
- `server/channels/store/sqlstore` and migrations - add persistence if no existing channel property fits.
- `webapp/platform/client/src/client4.ts` - add typed client method near channel route methods.
- `webapp/channels/src/components/channel_settings_modal` - likely UI surface for channel settings.
- `webapp/channels/src/actions/views/create_comment.tsx` - apply default during post construction (`webapp/channels/src/actions/views/create_comment.tsx:58-123`).
**High-Level Implementation Plan:**
1. Search for existing channel setting persistence before adding schema.
2. Add backend route with `APISessionRequired` and permission checks following API patterns (`server/channels/web/handlers.go:565-581`).
3. Add app-layer getter/setter.
4. Add store interface and SQL implementation or reuse an existing channel field if appropriate.
5. Add migration if needed.
6. Add client method and Redux/action plumbing.
7. Add settings modal UI.
8. Apply default in post creation when draft lacks explicit follow-up metadata.
9. Add API and UI tests.
**Tips:**
- Do not trust frontend admin checks; backend must enforce permission (`server/channels/api4/post.go:59-94` shows check style).
- Keep post metadata override explicit so users can unmark a default.
- Follow route grouping patterns instead of adding ad hoc paths (`server/channels/api4/api.go:217-238`).
**What Could Go Wrong:**
- Setting updates in UI but not persisted.
- Non-admin can modify setting by direct API call.
- Default overrides a user's explicit composer choice.
**Stretch Goal:** Add an audit record when the setting changes, following post audit patterns (`server/channels/api4/post.go:106-108`, `server/channels/api4/post.go:135-145`).
**Connects To:** Story 10 because this adds a domain concept that may need caching/performance review.

## Story 10: Add A Cached "Action Items" Channel View
**Difficulty:** Expert
**Estimated Time:** 24+ hours
**Skills You'll Practice:** architecture design, caching, new API, permissions, query performance, frontend route/state
**The Story:** As a user in busy channels, I want an Action Items view that shows posts needing follow-up so that I can review unresolved work without scanning the entire timeline.
**Acceptance Criteria:**
- [ ] Users can open an Action Items view from a channel.
- [ ] The view lists only posts visible to the current user.
- [ ] Query performance is acceptable in large channels.
- [ ] Results update when relevant posts are created or changed.
- [ ] The API enforces channel read permissions.
- [ ] The design includes cache invalidation or a reasoned no-cache decision.
- [ ] Tests cover permission filtering and result ordering.
**Files You'll Likely Touch:**
- `webapp/channels/src/components/root/root.tsx` - route shell if adding a new route or product view (`webapp/channels/src/components/root/root.tsx:315-470`).
- `webapp/channels/src/components/channel_view/channel_view.tsx` - entry point for channel-level UI (`webapp/channels/src/components/channel_view/channel_view.tsx:216-234`).
- `webapp/platform/types/src/posts.ts` - action item metadata/result type (`webapp/platform/types/src/posts.ts:76-119`).
- `webapp/platform/client/src/client4.ts` - add typed API method (`webapp/platform/client/src/client4.ts:2420-2434` shows post method style).
- `server/channels/api4/api.go` - register route under channel/post route patterns (`server/channels/api4/api.go:42-61`, `server/channels/api4/api.go:217-238`).
- `server/channels/api4/post.go` or new focused file - handler for action item query, following `getPostsForChannel` permission style (`server/channels/api4/post.go:239-355`).
- `server/channels/app/post.go` or new app service file - business query and sanitization behavior (`server/channels/app/post.go:483-488`).
- `server/channels/store/sqlstore/post_store.go` - query implementation and index needs (`server/channels/store/sqlstore/post_store.go:918-968`).
- `server/channels/db/migrations/postgres` - index migration if query needs one (`server/channels/db/migrations/postgres/000020_create_posts.up.sql:23-34`).
**High-Level Implementation Plan:**
1. Write a short design note in the PR description before coding: route, permissions, query, cache, invalidation, UI, tests.
2. Decide whether action-item state lives as post metadata, a new table, or a derived query from Story 8/9 metadata.
3. Add a backend read endpoint under channel scope.
4. Reuse channel read permission checks from `getPostsForChannel` (`server/channels/api4/post.go:280-289`).
5. Add app-layer method that queries store and prepares/sanitizes posts for the current user.
6. Add SQL query and index only after measuring/explaining query shape.
7. Add `Client4` method and frontend state/actions.
8. Add UI route or panel from channel view.
9. Add tests for permission, ordering, empty state, and metadata filtering.
**Tips:**
- Start from `getPostsForChannel` for permission, etag, prepare, and sanitize patterns (`server/channels/api4/post.go:239-355`).
- Treat cache invalidation as a first-class design problem because posts can be created, edited, deleted, or metadata-changed (`server/channels/store/sqlstore/post_store.go:970-1010` shows delete/update complexity).
- Do not expose posts the user cannot read; sanitize after query (`server/channels/app/post.go:483-488`).
- Keep UI separate from the main `PostView` until the API contract is stable.
**What Could Go Wrong:**
- Query scans too many posts in large channels.
- Cached results leak posts after membership or policy changes.
- UI and websocket updates disagree about whether a post is still an action item.
**Stretch Goal:** Add an unread/action-item badge in the sidebar row.
**Connects To:** Story 8 and Story 9 because this story depends on follow-up metadata and optional channel defaults.

