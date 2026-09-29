# Verification record

Two checks are documented for this change. The native Mattermost follow-up is run from the server directory:

```text
cd mattermost/server
go test ./channels/store/sqlstore -run TestValidateChannelUpdateCount -count=1
```

The earlier native launch attempt from the workspace was blocked because the Go executable was unavailable; that historical failure is preserved in `checks/f5bd710b171f/crud-b02-go-test.log`. It is not a passing result and should not be confused with the portable harness.

From this project root, the portable command is:

```text
python mattermost/tests/crud-b02/run_channel_store_harness.py --go <path-to-go.exe>
```

That runner extracts the exact staged `updateChannelT` and `validateChannelUpdateCount` methods into a temporary Go module and supplies explicit SQL result, model, store-error, and pkg/errors contracts. Its six intended subtests cover zero rows, one row, multiple rows, `RowsAffected` failure, `NamedExec` failure, and invalid `DeleteAt`. The harness executes the method under review; it does not execute outer `SqlChannelStore.Update`, public-channel upsert, transaction rollback, or a live database. The captured portable run completed successfully with six passing subtests and no failed or skipped cases. The parent Go test is not counted as a seventh case.

The source files are [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go), [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go), and [`mattermost/tests/crud-b02/run_channel_store_harness.py`](../mattermost/tests/crud-b02/run_channel_store_harness.py). The exact baseline is [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt). The evidence claim is limited to the SQL row-count boundary and its error contract; native database and outer transaction behavior remain follow-up checks.
The portable harness also tests validation before SQL by presenting DeleteAt as nonzero, and it checks that an execution error is wrapped rather than mistaken for a missing row. Those cases exercise the exact method under review with explicit contracts. They do not assert the outer transaction's rollback callback or the PublicChannels projection. A native run from mattermost/server remains the correct next check for those repository concerns.

## Captured execution

Read the [Go output](evidence/crud-b02-go-harness-final.log), [command and six-case results](evidence/results.json), and [verified portable toolchain metadata](evidence/toolchain-verification.json). The earlier failed launch and incomplete-toolchain attempt remain separate workspace records. The successful run uses Go 1.27.1 from the checksum-verified official archive; no native Mattermost dependency suite was installed or claimed.
