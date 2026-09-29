"""Run a dependency-free Go test around the exact production update method.

The runner extracts updateChannelT and validateChannelUpdateCount from the staged
production file verbatim. The generated module supplies only explicit SQL,
model, error, and transaction contracts needed to execute those functions.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def extract(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish].rstrip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", default=os.environ.get("GO_BIN", "go"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    production = root / "server/channels/store/sqlstore/channel_store.go"
    source = production.read_text(encoding="utf-8")
    method = extract(source, "func (s SqlChannelStore) updateChannelT", "func validateChannelUpdateCount")
    helper = extract(source, "func validateChannelUpdateCount", "func (s SqlChannelStore) GetChannelUnread")

    with tempfile.TemporaryDirectory(prefix="crud-b02-channel-") as raw:
        work = Path(raw)
        (work / "store").mkdir()
        (work / "model").mkdir()
        (work / "pkgerrors").mkdir()
        (work / "go.mod").write_text(
            "module crudb02\n\ngo 1.23\n\nrequire github.com/pkg/errors v0.0.0\nreplace github.com/pkg/errors => ./pkgerrors\n",
            encoding="utf-8",
        )
        (work / "pkgerrors/go.mod").write_text("module github.com/pkg/errors\n\ngo 1.23\n", encoding="utf-8")
        (work / "pkgerrors/errors.go").write_text(
            "package errors\n\nimport (\n stdErrors \"errors\"\n \"fmt\"\n)\nfunc Wrap(err error, msg string) error { return fmt.Errorf(\"%s: %w\", msg, err) }\nfunc Wrapf(err error, format string, args ...any) error { return fmt.Errorf(format+\": %w\", append(args, err)...)}\nfunc As(err error, target any) bool { return stdErrors.As(err, target) }\n",
            encoding="utf-8",
        )
        (work / "store/store.go").write_text(
            "package store\n\nimport \"fmt\"\n\ntype ErrNotFound struct { Resource, ID string }\nfunc NewErrNotFound(resource, id string) *ErrNotFound { return &ErrNotFound{resource, id} }\nfunc (e *ErrNotFound) Error() string { return fmt.Sprintf(\"resource %q not found, id: %s\", e.Resource, e.ID) }\ntype ErrInvalidInput struct{}\nfunc NewErrInvalidInput(string, string, any) *ErrInvalidInput { return &ErrInvalidInput{} }\nfunc (e *ErrInvalidInput) Error() string { return \"invalid input\" }\ntype ErrUniqueConstraint struct{}\nfunc NewErrUniqueConstraint(string) *ErrUniqueConstraint { return &ErrUniqueConstraint{} }\nfunc (e *ErrUniqueConstraint) Error() string { return \"unique constraint\" }\n",
            encoding="utf-8",
        )
        (work / "model/model.go").write_text(
            "package model\n\n type Channel struct { Id string; DeleteAt int }\n func (c *Channel) PreUpdate() {}\n func (c *Channel) IsValid() error { return nil }\n",
            encoding="utf-8",
        )
        (work / "channel_store_harness_test.go").write_text(
            "package sqlstore\n\nimport (\n stdErrors \"errors\"\n \"fmt\"\n \"testing\"\n\n \"crudb02/model\"\n \"crudb02/store\"\n \"github.com/pkg/errors\"\n)\n\ntype execResult struct { rows int64; err error }\nfunc (r execResult) RowsAffected() (int64, error) { return r.rows, r.err }\ntype sqlxTxWrapper struct { exec func(any) (execResult, error) }\nfunc (t *sqlxTxWrapper) NamedExec(query string, arg any) (execResult, error) { return t.exec(arg) }\ntype SqlChannelStore struct{}\nfunc IsUniqueConstraintError(error, []string) bool { return false }\n\n" + method + "\n" + helper + "\n\nfunc run(t *testing.T, rows int64, namedErr, rowsErr error, channel *model.Channel) (*model.Channel, error) {\n called := false\n tx := &sqlxTxWrapper{exec: func(any) (execResult, error) { called = true; return execResult{rows: rows, err: rowsErr}, namedErr }}\n got, err := (SqlChannelStore{}).updateChannelT(tx, channel)\n if namedErr == nil && rowsErr == nil && rows == 1 && channel.DeleteAt == 0 && got != channel { t.Fatalf(\"expected same channel pointer\") }\n if (namedErr != nil || rowsErr != nil || rows == 0 || rows > 1 || channel.DeleteAt != 0) && got != nil { t.Fatalf(\"expected nil result on failure\") }\n if channel.DeleteAt != 0 && called { t.Fatalf(\"invalid channel reached SQL\") }\n return got, err\n}\n\nfunc TestUpdateChannelTContracts(t *testing.T) {\n t.Run(\"zero rows is not found\", func(t *testing.T) { got, err := run(t, 0, nil, nil, &model.Channel{Id: \"missing\"}); if got != nil { t.Fatal(\"expected nil result\") }; var nf *store.ErrNotFound; if !stdErrors.As(err, &nf) || nf.Resource != \"Channel\" || nf.ID != \"missing\" { t.Fatalf(\"got %T: %v\", err, err) } })\n t.Run(\"one row returns channel\", func(t *testing.T) { if _, err := run(t, 1, nil, nil, &model.Channel{Id: \"present\"}); err != nil { t.Fatal(err) } })\n t.Run(\"multiple rows fails\", func(t *testing.T) { if _, err := run(t, 2, nil, nil, &model.Channel{Id: \"many\"}); err == nil { t.Fatal(\"expected error\") } })\n t.Run(\"rows affected failure propagates\", func(t *testing.T) { sentinel := fmt.Errorf(\"rows failed\"); if _, err := run(t, 1, nil, sentinel, &model.Channel{Id: \"rows-error\"}); !stdErrors.Is(err, sentinel) { t.Fatalf(\"expected wrapped rows error, got %v\", err) } })\n t.Run(\"named exec failure propagates\", func(t *testing.T) { sentinel := fmt.Errorf(\"exec failed\"); if _, err := run(t, 1, sentinel, nil, &model.Channel{Id: \"exec-error\"}); !stdErrors.Is(err, sentinel) { t.Fatalf(\"expected wrapped exec error, got %v\", err) } })\n t.Run(\"invalid delete is rejected before SQL\", func(t *testing.T) { if _, err := run(t, 1, nil, nil, &model.Channel{Id: \"deleted\", DeleteAt: 1}); err == nil { t.Fatal(\"expected error\") } })\n}\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.update({"GOPROXY": "off", "GOWORK": "off", "GOTOOLCHAIN": "local"})
        result = subprocess.run([args.go, "test", "-v", "./...", "-count=1"], cwd=work, env=env, text=True)
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
