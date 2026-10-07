# Practice exercises

Use [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go), [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go), and [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt).

**Exercise 1, 2 points — outcomes.** Predict the error returned for counts 0, 1, and 2. Which outcome allows `Update` to call `upsertPublicChannelT`?

*Goal:* state the three helper results from source. *Check:* your answers match the three subtests of `TestValidateChannelUpdateCount` in `channel_store_update_test.go`, including the exact error strings.

**Exercise 2, 3 points — ownership of truth.** Explain why returning the caller’s `channel` object is misleading when count is zero. Name the database fact that should control the result.

*Goal:* separate the caller's proposal from durable state. *Check:* point to the `RowsAffected` call at `channel_store.go:887` and the `return channel, nil` at `:895` that is only reached after the helper passes.

**Exercise 3, 3 points — transaction trace.** Trace `Update` with count zero. List the functions reached after `updateChannelT` returns and identify which public projection write must be skipped.

*Goal:* follow control flow across the transaction. *Check:* your trace names `finalizeTransactionX` (`sqlstore/utils.go:91`) and skips `upsertPublicChannelT` (`channel_store.go:835`) and `Commit` (`:839`).

**Exercise 4, 4 points — error taxonomy.** Design a test where `RowsAffected()` itself returns an error. Explain why it must not become `store.NewErrNotFound`.

*Goal:* keep driver failures distinct from absence. *Check:* compare with the `rows affected failure propagates` subtest that `mattermost/tests/crud-b02/run_channel_store_harness.py` generates — it asserts `errors.Is` on the sentinel, not a not-found type.

**Exercise 5, 4 points — SQL integration.** Propose a live test that updates a missing channel, an existing channel, and a query that unexpectedly affects two rows. State which assertions are stable across database drivers and which require checking driver semantics.

*Goal:* design the native test this course does not have. *Check:* no existing test file covers it — `channel_store_update_test.go` and the harness both use fixed counts — so your design must name a real database fixture and assert the `PublicChannels` row, not just the returned error.

**Exercise 6, 4 points — review comment.** Write a review comment explaining why the multiple-row error stays even after adding the zero-row branch. Include the data-integrity assumption it protects.

*Goal:* defend a guard that looks redundant. *Check:* cite the `unexpected multiple rows remains an error` subtest in `channel_store_update_test.go` as the test that would fail if the branch were deleted.

Grade exact outcomes 5 points, transaction ordering 3, error distinction 4, integration design 4, and review reasoning 4. Do not infer a passing Go test from the source alone; the verification chapter distinguishes the historical launch failure, the source-method harness, and unexecuted native integration checks.

For an additional exercise, compare this helper with a delete method: decide whether zero rows should also be not-found, an idempotent success, or a policy-specific result. Support the choice with the caller contract and the side effects that follow it. Then identify which answer would be unsafe if a public projection were updated afterward.

