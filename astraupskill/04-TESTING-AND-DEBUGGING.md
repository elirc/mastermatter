# Testing and debugging the row-count contract

There are two useful checks. The native follow-up runs from the Mattermost directory:

```text
cd mattermost/server
go test ./channels/store/sqlstore -run TestValidateChannelUpdateCount -count=1
```

From this project root, the portable source-method harness is:

```text
python mattermost/tests/crud-b02/run_channel_store_harness.py --go <path-to-go.exe>
```

The harness reads the exact staged `updateChannelT` and `validateChannelUpdateCount` bodies, places them in a temporary Go module, and supplies explicit contracts for sqlx-like execution, model.Channel, store errors, and pkg/errors. Its six subtests cover zero rows, one row, multiple rows, a RowsAffected failure, a NamedExec failure, and invalid DeleteAt. This is production-source execution with dependency doubles. It does not execute the outer `SqlChannelStore.Update`, `upsertPublicChannelT`, transaction finalization, or a real database.

Debug in layers. First inspect `RowsAffected` error handling; a driver failure must stay distinct from zero-row not-found. Next inspect `validateChannelUpdateCount(0, id)` and verify the returned error includes resource and id. Then trace `Update` in the source: its early return after `updateChannelT` must precede public propagation. Finally inspect count two, which remains a defensive consistency failure. Also remember that SQL affected-row counts should be nonnegative; the helper's explicit branches are for zero, one, and greater-than-one production results.

| Observation | Likely defect | Check |
| --- | --- | --- |
| missing channel succeeds | zero branch absent | harness zero case |
| public table reached after zero | outer caller ignored error | source inspection |
| driver failure says not found | errors collapsed | harness error case |
| count two succeeds | defensive guard removed | harness multiple case |

The native command remains a separate follow-up for the repository's real dependencies and driver behavior. The harness result must be reported separately from it.