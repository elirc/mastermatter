# Channel update row counts: a CRUD boundary lesson

This course follows one narrow change in the staged Mattermost source. The production store is [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go), where `SqlChannelStore.Update` opens a transaction, calls `updateChannelT`, propagates the accepted channel to `PublicChannels`, and commits. The exact original file is preserved in [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt). The focused regression is [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go).

The defect was a CRUD error-boundary mismatch. SQL `UPDATE` can affect zero rows when the channel id does not exist. The old inline greater-than-one check allowed zero to fall through as success, returned the caller’s channel object, and allowed `Update` to continue into public-channel propagation. The staged helper now maps zero to `store.NewErrNotFound("Channel", channelID)`, treats one nonnegative affected row as success, and preserves the existing multiple-row internal consistency error. This makes the store’s result reflect durable state before downstream work begins.

The intended lesson is about row counts, transactions, and error contracts. It is not a claim that all Mattermost channel writes are covered. The native Go test remains a separate follow-up; a dependency-free harness now extracts the exact production methods and supplies explicit SQL, model, store, and error contracts. The chapters therefore use exact source traces, a before/after snippet, prediction exercises, separate solutions, and a verification record that distinguishes code review from executed test evidence.

Read the map first, then predict the three row-count outcomes before opening the test. A junior engineer should be able to explain why a missing channel is not a successful no-op. A reviewer should also ask why returning not-found before `upsertPublicChannelT` protects transaction semantics and public-channel consistency.

That distinction is the central review habit for this project: follow the durable result before following projections or responses.

