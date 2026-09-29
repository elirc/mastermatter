# Practice exercises

Use [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go), [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go), and [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt).

**Exercise 1, 2 points — outcomes.** Predict the error returned for counts 0, 1, and 2. Which outcome allows `Update` to call `upsertPublicChannelT`?

**Exercise 2, 3 points — ownership of truth.** Explain why returning the caller’s `channel` object is misleading when count is zero. Name the database fact that should control the result.

**Exercise 3, 3 points — transaction trace.** Trace `Update` with count zero. List the functions reached after `updateChannelT` returns and identify which public projection write must be skipped.

**Exercise 4, 4 points — error taxonomy.** Design a test where `RowsAffected()` itself returns an error. Explain why it must not become `store.NewErrNotFound`.

**Exercise 5, 4 points — SQL integration.** Propose a live test that updates a missing channel, an existing channel, and a query that unexpectedly affects two rows. State which assertions are stable across database drivers and which require checking driver semantics.

**Exercise 6, 4 points — review comment.** Write a review comment explaining why the multiple-row error stays even after adding the zero-row branch. Include the data-integrity assumption it protects.

Grade exact outcomes 5 points, transaction ordering 3, error distinction 4, integration design 4, and review reasoning 4. Do not infer a passing Go test from the source alone; the verification chapter distinguishes the historical launch failure, the source-method harness, and unexecuted native integration checks.

For an additional exercise, compare this helper with a delete method: decide whether zero rows should also be not-found, an idempotent success, or a policy-specific result. Support the choice with the caller contract and the side effects that follow it. Then identify which answer would be unsafe if a public projection were updated afterward.

