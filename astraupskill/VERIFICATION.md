# Verification record

> **Status note (2026-10-06, frozen record).** The run described below (2026-09-22, exit code 0, six cases) is kept as recorded. A static re-check on 2026-10-06 — no Go toolchain, no test execution — confirmed: the staged helper and its call site are at `channel_store.go:898-906` and `:891`; `channel_store_update_test.go` contains `TestValidateChannelUpdateCount` with three subtests (`missing channel is a not found error`, `one updated row succeeds`, `unexpected multiple rows remains an error`) whose expected strings match `store.ErrNotFound.Error()` and the helper's `fmt.Errorf`; and the harness generates `TestUpdateChannelTContracts` with exactly the six subtests listed in `evidence/results.json`. Two links pointed at logs that were never committed and have been replaced with plain-text references. The machine-specific paths inside the JSON evidence files describe the original workspace, not this repository.

Two checks are documented for this change. The native Mattermost follow-up is run from the server directory:

```text
cd mattermost/server
go test ./channels/store/sqlstore -run TestValidateChannelUpdateCount -count=1
```

The earlier native launch attempt from the workspace was blocked because the Go executable was unavailable; that historical failure was recorded in a workspace log (`checks/f5bd710b171f/crud-b02-go-test.log`) that is **not tracked in this repository**. It is not a passing result and should not be confused with the portable harness.

From this project root, the portable command is:

```text
python mattermost/tests/crud-b02/run_channel_store_harness.py --go <path-to-go.exe>
```

That runner extracts the exact staged `updateChannelT` and `validateChannelUpdateCount` methods into a temporary Go module and supplies explicit SQL result, model, store-error, and pkg/errors contracts. Its six intended subtests cover zero rows, one row, multiple rows, `RowsAffected` failure, `NamedExec` failure, and invalid `DeleteAt`. The harness executes the method under review; it does not execute outer `SqlChannelStore.Update`, public-channel upsert, transaction rollback, or a live database. The captured portable run completed successfully with six passing subtests and no failed or skipped cases. The parent Go test is not counted as a seventh case.

The source files are [`mattermost/server/channels/store/sqlstore/channel_store.go`](../mattermost/server/channels/store/sqlstore/channel_store.go), [`mattermost/server/channels/store/sqlstore/channel_store_update_test.go`](../mattermost/server/channels/store/sqlstore/channel_store_update_test.go), and [`mattermost/tests/crud-b02/run_channel_store_harness.py`](../mattermost/tests/crud-b02/run_channel_store_harness.py). The exact baseline is [`snapshots/channel_store.go.original.txt`](snapshots/channel_store.go.original.txt). The evidence claim is limited to the SQL row-count boundary and its error contract; native database and outer transaction behavior remain follow-up checks.
The portable harness also tests validation before SQL by presenting DeleteAt as nonzero, and it checks that an execution error is wrapped rather than mistaken for a missing row. Those cases exercise the exact method under review with explicit contracts. They do not assert the outer transaction's rollback callback or the PublicChannels projection. A native run from mattermost/server remains the correct next check for those repository concerns.

## Captured execution

Read the [command and six-case results](evidence/results.json) and [verified portable toolchain metadata](evidence/toolchain-verification.json). The raw Go output (`crud-b02-go-harness-final.log`, named in `results.json`) was not committed, so `results.json` is the only in-repo record of the run. The earlier failed launch and incomplete-toolchain attempt remain separate workspace records. The successful run uses Go 1.27.1 from the checksum-verified official archive; no native Mattermost dependency suite was installed or claimed.
