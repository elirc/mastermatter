# Codebase map: channel update request to SQL result

The main path is in [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go). `SqlChannelStore.Update` begins a master transaction, invokes `updateChannelT(transaction, channel)`, then calls `upsertPublicChannelT` and commits. `updateChannelT` prepares the model with `PreUpdate`, rejects nonzero `DeleteAt`, validates the channel, and executes a named SQL `UPDATE Channels ... WHERE Id=:Id`.

The changed boundary is immediately after `res.RowsAffected()`. The PostgreSQL update result reports an affected-row count; a successful SQL execution alone does not prove that a row existed. The helper `validateChannelUpdateCount` turns that count into a store contract: zero is `store.NewErrNotFound("Channel", channelID)`, one is success, and more than one is an internal consistency error. `Update` only reaches public-channel propagation when the helper returns nil. A returned not-found error also lets the deferred transaction finalizer roll back or close the transaction according to the existing store machinery.

| Layer | Responsibility | Source |
| --- | --- | --- |
| model preparation | timestamps and validity | `channel_store.go` |
| SQL mutation | update `Channels` by id | `channel_store.go` |
| row-count policy | not-found, success, impossible multiple | `channel_store.go` |
| public projection | propagate accepted channel | `channel_store.go` |
| focused regression | test helper outcomes | `channel_store_update_test.go` |

The original snapshot at [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt) is the comparison baseline. The test file at [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go) tests the pure helper without a live database. That is useful evidence for the contract, while a full SQL test would still be needed to prove `RowsAffected` behavior on the deployed driver.

When tracing, keep the channel object and database row distinct: the caller can hold a plausible object even when SQL changed nothing. The row count is the authority.
