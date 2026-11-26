# 025-child-trace-citations

Normative source: [§14 composition, law 8](../../../../../spec/14-composition.md) and
[§17 item observations](../../../../../spec/17-trace.md).

A parent runs one child workflow, `step.nika`, per item and per call. Every
child trace it started is cited by name: each `for_each` item row carries
`child` whatever its status (`ok`, a `recovered` row whose child timed out, a
`cancelled` row whose child the batch abandoned), a retried iteration adds
`child_attempts`, and the journal keeps the `task_retrying` and terminal
`child` rows of the plain calls. The `witness` task makes one builtin call, so
that the parent journal carries a permit frame of its own; the permit decisions
of the child calls are in the child journals. The exact assertion is in
`expected-verify.json`. `provenance.json` records the real source trace, the
engine identity (a development commit in no release yet) and that nothing was
mutated.

The fixture holds the parent journal only. The child traces it cites are not
beside it, so the reference engine's `nika trace verify` adds one line per
missing child; those lines change neither the verdict nor the exit.
