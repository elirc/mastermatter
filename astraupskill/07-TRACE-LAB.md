# Trace lab: exact method outcomes

Trace the extracted production methods with the six cases in `mattermost/tests/crud-b02/run_channel_store_harness.py`. The harness executes `updateChannelT` and the helper directly; it does not execute the outer `SqlChannelStore.Update` method. Public propagation and transaction behavior below are source-level consequences that still need native or database evidence.

| Step | Zero rows | One row | Multiple rows | RowsAffected error | NamedExec error | Invalid DeleteAt |
| --- | --- | --- | --- | --- | --- | --- |
| `PreUpdate`/validation | pass | pass | pass | pass | pass | rejects |
| SQL call | executes | executes | executes | returns count error | returns exec error | skipped |
| row result | 0 | 1 | 2 | unusable | unavailable | none |
| helper | not-found | nil | internal error | not reached | not reached | not reached |
| method result | error | channel pointer | error | wrapped error | wrapped error | invalid input |
| outer `Update` consequence | returns before public upsert | may continue | returns before public upsert | returns before public upsert | returns before public upsert | returns before public upsert |

The most important boundary is the helper's return value. A missing row cannot be represented by the caller's in-memory channel because SQL changed nothing. A one-row result preserves the pre-existing return pointer. A multiple-row result violates the identity assumption and remains an internal consistency error. Driver failures are separate because the store cannot interpret an unavailable count.

Now inspect the outer method in [`channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go). `Update` calls `updateChannelT`, checks its error, and only then calls `upsertPublicChannelT`. The harness does not prove that transaction or public-table path; it proves the exact method that controls whether the path is reached. This distinction prevents a focused green harness from being mistaken for full repository integration.

For a senior exercise, trace deferred transaction finalization for each returned error and identify the native test needed to verify rollback and driver-specific `RowsAffected` semantics.