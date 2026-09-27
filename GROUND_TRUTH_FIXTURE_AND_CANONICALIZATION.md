# Ground Truth v1 Fixture and Canonicalization Record

## Paths and schema

- fixture directory: `cases/authority_lab/`
- fixture parser/model: `authority_lab/model.py` (`OracleInput.from_fixture`)
- loader and protected-manifest injection: `authority_lab/runner.py::load_fixture`
- oracle: `authority_lab/oracle.py::evaluate`
- runner: `authority_lab/runner.py::run_fixture`, `run_path`, and `discover`
- CLI: `authority_lab/__main__.py`
- schema identifier: fixture root field `schema_version`; supported values are
  `authority-lab-v0` and `authority-lab-v1`. v0 cannot authorize under the v1
  parser/oracle contract.

Root fixture records contain `schema_version`, `case_id`, `title`, `objective`,
`source_case_id`, `notes`, `authority_tuple`, `t1`, `t2`, `t3`,
`applicable_invariants`, `authority_question`, `expected_outcome`, and
`expected_reason`. Exact nested
required fields are enforced by typed parsers and `_require_exact_fields` in
`authority_lab/model.py`; the executable model, not this summary, is canonical.

## Protected state

`authority_lab/runner.py::load_fixture` injects v1 protected state by fixture
filename from:

- `cases/authority_lab/trusted_commitment_state.json`
- `cases/authority_lab/trusted_anchor_state.json`

Fixture JSON is rejected if it directly supplies `_trusted_commitment_context`,
`_trusted_anchor_context`, `_trusted_control_plane_context`,
`_trusted_delegation_context`, `_trusted_human_approval_context`,
`_trusted_tool_connector_context`, or `_trusted_t3_execution_event`.

## Canonical serialization and digests

`authority_lab/oracle.py::_canonical_digest` serializes mappings with:

```python
json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
```

It hashes `domain + "\\0" + payload`, UTF-8 encoded, with SHA-256 and returns
the lowercase hexadecimal digest. Domain-separated helpers cover human approval
effects/requests/envelopes, tool contexts, and T3 execution events.

Observation commitment and durable-state digest helpers are imported by
`authority_lab/oracle.py` from `authority_lab/commitment.py`. Commitment
envelopes require `SHA-256`, canonical payload equality, exact referenced
segments, verifier linkage, append-only predecessor relations, checkpoints, and
harness-owned durable-state agreement.

## Evaluation and expectation separation

`run_fixture` first builds `OracleInput` and calls `evaluate`. Only after the
actual result is fixed does it parse `expected_outcome`. Equality produces
`HarnessStatus.PASS`; disagreement produces `HarnessStatus.CASE_MISMATCH`.
Title, expected reason, and expected outcome are excluded from `OracleInput`.

The exact tuple, invariant, and outcome declarations are in
`authority_lab/model.py`. A fixture ID maps directly to
`cases/authority_lab/<ID>.json`; `discover` returns sorted `LAB-*.json` paths.
