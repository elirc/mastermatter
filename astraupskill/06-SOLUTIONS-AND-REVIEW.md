# Solutions and review rubric

**Exercise 1.** Count zero returns `store.NewErrNotFound("Channel", id)`, one returns nil, and two returns the existing internal consistency error. Only one reaches public-channel propagation because any helper error returns from `Update`.

**Exercise 2.** The object belongs to the caller and can contain new fields, but SQL changed no row. `RowsAffected` is the authoritative persistence result; returning the proposal as success would turn absence into a false update.

**Exercise 3.** `Update` begins a transaction and calls `updateChannelT`. The helper returns not-found, `Update` returns immediately, and deferred finalization handles the transaction. `upsertPublicChannelT` and commit are skipped.

**Exercise 4.** Use a fake result whose `RowsAffected` returns `(0, driverError)`. Assert the wrapped rows-affected error, not not-found. A driver failure means the store cannot know whether a row matched.

**Exercise 5.** Insert one real channel and use a missing id for zero. Assert not-found, then assert one returns the channel and updates its fields. A two-row case is normally guarded by the primary key; a unit seam or deliberately broad SQL fixture can exercise the defensive error. Driver matched-versus-changed semantics need explicit documentation.

**Exercise 6.** The multiple-row branch protects the assumption that channel id identifies at most one row. Removing it would hide schema or query corruption and let a caller receive a misleading single object after an ambiguous update.

Review against [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt). Approve when zero is a production not-found error, one preserves behavior, two remains defensive, and downstream propagation follows only success. The portable compiler enables a separate source-method harness; it does not establish that the native Mattermost package or database tests passed.

The delete extension has a policy-dependent answer: an idempotent delete can accept zero when the desired absence already holds, while a strict resource endpoint can report not-found. Neither policy justifies creating a public projection from a failed primary update. State the caller contract before transferring this rule to another CRUD operation. For grading, give full credit only when the answer distinguishes a source trace from an executed transaction test and names a concrete assertion for each.
