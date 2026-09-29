# Worked change: turn zero rows into not-found

The baseline is [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt). Before the repair, `updateChannelT` called `res.RowsAffected()` and had an inline check that rejected counts greater than one. A count of zero returned nil. The named helper is part of the staged correction, not the baseline. `SqlChannelStore.Update` then treated the caller’s channel object as accepted and proceeded to `upsertPublicChannelT`.

The staged behavior adds the missing branch:

```go
count, err := res.RowsAffected()
if err != nil {
    return nil, errors.Wrap(err, "error while getting rowsAffected in updateChannelT")
}
if err := validateChannelUpdateCount(count, channel.Id); err != nil {
    return nil, err
}
return channel, nil

func validateChannelUpdateCount(count int64, channelID string) error {
    if count == 0 {
        return store.NewErrNotFound("Channel", channelID)
    }
    if count > 1 {
        return fmt.Errorf("the expected number of channels to be updated is <=1 but was %d", count)
    }
    return nil
}
```

The native test at [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go) covers zero, one, and two. The dependency-free harness at [`mattermost/tests/crud-b02/run_channel_store_harness.py`](../mattermost/tests/crud-b02/run_channel_store_harness.py) extracts the exact staged method and helper, then exercises six cases: zero rows, one row, multiple rows, RowsAffected failure, NamedExec failure, and invalid DeleteAt. It supplies explicit contracts rather than copying the implementation. The harness does not execute SqlChannelStore.Update, public upsert, or database rollback.

The change is deliberately bounded. It does not alter SQL, public-channel propagation, or transaction finalization. It inserts the missing interpretation at the earliest point where the store knows the update did not target a row.

The returned error also preserves the resource vocabulary used elsewhere in the Mattermost store. That consistency matters to API layers and callers that distinguish not-found from validation, uniqueness, and database failures. A reviewer can therefore assess both control flow and contract shape without inventing a new error type.

