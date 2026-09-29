# CRUD semantics of affected-row counts

An update method has at least three outcomes: a row was accepted, no row matched, or the database reported an impossible number of rows. Treating all non-error SQL executions as success creates a false state transition. In this project, `UPDATE Channels ... WHERE Id=:Id` returning zero means the requested channel is absent. The caller’s in-memory `*model.Channel` remains a proposed value, not evidence that a database row exists.

The staged helper expresses the contract directly:

```go
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

The zero-row error is more than a nicer message. `SqlChannelStore.Update` checks the helper before calling `upsertPublicChannelT`; therefore a missing primary channel cannot create or update a public projection. The deferred transaction finalizer receives the error and preserves the existing rollback behavior. The one-row case retains the original return value and downstream flow. The multiple-row error remains a defensive signal that the data or query assumptions are broken.

This helper does not prove the SQL statement changed every field, nor does it solve concurrent updates with equal ids. It defines the missing-record boundary. A live database test should confirm driver row-count semantics, especially when values are unchanged and a database reports matched versus changed rows differently. The focused unit test demonstrates the intended contract but cannot make that connector claim.

Reviewers should ask: what does the caller observe for zero, where does propagation stop, and which error remains internal? Those questions generalize to user updates, membership deletion, and inventory adjustments.

Inspect [the supported-driver validation](../mattermost/server/public/model/config.go): SqlSettings.isValid accepts DatabaseDriverPostgres. Keep that repository fact separate from generic matched-versus-changed behavior in other database products. The harness provides RowsAffected values deliberately; it does not connect to PostgreSQL or validate driver behavior. A native integration case should update an existing channel with unchanged business fields as well as a missing id, and assert the returned resource and public projection state.
