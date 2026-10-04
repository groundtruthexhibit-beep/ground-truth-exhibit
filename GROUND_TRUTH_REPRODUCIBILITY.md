# Ground Truth v1 Reproducibility

## Exact state

- repository: `groundtruthexhibit-beep/ground-truth-exhibit`
- freeze branch: `docs/ground-truth-research-freeze-v1`
- frozen research HEAD: `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- research parent: `406a37b4a0019a9eb9d8526b5d248dd1ebc6de20`
- schema: `authority-lab-v1`
- corpus: `LAB-V0-001..012`, `LAB-V1-013..466`; 466 fixtures
- public tests at research HEAD: 259/259 PASS
- public tests on the freeze branch: 260/260 PASS after adding the explicit deterministic replay test
- fixtures at research HEAD: 466/466 PASS
- T3 focused checkpoint: 7/7 PASS
- Composite focused checkpoint: 2/2 PASS

Python 3 is required. The implementation uses only repository code plus Python
standard-library modules for the Authority Lab path exercised here.

## Exact verification commands

```bash
git rev-parse HEAD
git rev-parse HEAD^
git status --short
git diff --check
python -m unittest discover -s tests
python -m authority_lab run-all cases/authority_lab
```

Focused T3 regression:

```bash
python -m unittest \
  tests.test_authority_lab.AuthorityLabTests.test_t3_hostile_matrix_matches_independent_expectations \
  tests.test_authority_lab.AuthorityLabTests.test_approval_and_delegation_local_heads_cannot_precede_t3 \
  tests.test_authority_lab.AuthorityLabTests.test_candidate_cached_authorized_result_is_not_authority \
  tests.test_authority_lab.AuthorityLabTests.test_duplicate_and_conflicting_t3_events_fail_closed \
  tests.test_authority_lab.AuthorityLabTests.test_t3_positive_paths_remain_reachable \
  tests.test_authority_lab.AuthorityLabTests.test_t3_refresh_requires_protected_underlying_transition \
  tests.test_authority_lab.AuthorityLabTests.test_current_revocation_at_t3_remains_denied
```

Focused Composite regression:

```bash
python -m unittest \
  tests.test_authority_lab.AuthorityLabTests.test_composite_adversarial_control_continuity_matrix \
  tests.test_authority_lab.AuthorityLabTests.test_full_composite_positive_joins_all_authority_layers_at_t3
```

Oracle-independence evidence:

- `tests/test_authority_lab.py::AuthorityLabTests.test_wrong_expectation_does_not_change_actual`
- `tests/test_authority_lab.py::AuthorityLabTests.test_expected_outcome_remains_outside_v1_oracle_input`
- `tests/test_authority_lab.py::AuthorityLabTests.test_labels_titles_and_expectation_do_not_change_oracle`

An intentionally wrong expected outcome leaves the oracle result unchanged and
produces `CASE_MISMATCH`.

Explicit deterministic replay evidence:

- `tests/test_authority_lab.py::AuthorityLabTests.test_identical_canonical_input_replays_deterministically`

It evaluates the same canonical protected Composite-positive input five times
and requires identical outcome/reason objects each time.

## Expected semantics

`AUTHORIZED` permits only the exact current effect. `DENIED` is an established
applicable negative condition. `UNAVAILABLE` means a required fact cannot be
established. Only the fixture expectation comparison affects harness status; it
never enters the oracle. A clean reproduction ends with empty
`git status --short`, successful `git diff --check`, all tests passing, and no
`CASE_MISMATCH` from `run-all`.

Canonicalization, schema parsing, and protected state are detailed in
`GROUND_TRUTH_FIXTURE_AND_CANONICALIZATION.md`.

## Post-freeze PHI disclosure-authority reproduction

The following is a later extension and does not replace the frozen v1 evidence above.

- PR: `#25`
- reviewed feature head: `0b88a4814496c32c2a729f350106e0038f1b8e63`
- merge commit on `main`: `05ab14a7c260e8d94e737a8d4a524385bb673515`
- schema: unchanged `authority-lab-v1`
- fixture corpus after extension: 478 fixtures
- Authority Lab regression: 265/265 PASS
- all-fixture runner: PASS
- hostile PHI review: PASS
- final bounded implementation verifier: OVERALL PASS
- GitHub status checks on PR #25: none configured/reported

The final hostile review also fixed denial precedence for incomplete disclosure history: incomplete required history returns `UNAVAILABLE / PHI_HISTORY_UNAVAILABLE`; cumulative `DENIED` is evaluated only after history completeness is established.
