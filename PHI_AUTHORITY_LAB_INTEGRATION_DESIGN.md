# Ground Truth PHI Disclosure Authority — Minimal Authority Lab Integration Design

## Exact baseline

Repository:
`groundtruthexhibit-beep/ground-truth-exhibit`

Pinned public `main`:
`74cd883736c7acde1ff0d0d2ad765f6e8771def0`

Observed current Authority Lab surface at that head:
- `authority_lab/model.py`
- `authority_lab/oracle.py`
- `authority_lab/runner.py`
- `authority_lab/README.md`
- `tests/test_authority_lab.py`
- `cases/authority_lab/`
- 466 maintained fixtures expected by the public test suite.

## Design objective

Add the smallest PHI disclosure-authority layer that composes with existing Authority Lab
v1 semantics without changing the public tuple, invariant set, outcomes, or schema.

The PHI layer should behave like Human Approval and Tool/Connector: strict typed candidate
relations joined against harness-owned protected context and one canonical T3 event.

## 1. Proposed internal model additions

Add internal strict records in `authority_lab/model.py`:

- `PHIDisclosurePolicy`
- `PHIAuthorityBasisAdmission`
- `PHIRecipientDomainMembership`
- `PHIDisclosureHistoryHead`
- `PHIMemoryScopeAdmission`
- `PHITransformationAdmission`
- `PHIEffectOutcomeRecord`
- `PHIDisclosureUse`
- `PHIDisclosureAuthorityContext`

No type is a public tuple coordinate.

Recommended protected context key inside each trusted anchor context:

`phi_disclosure_authority_context`

Candidate-visible reserved relation:

`phi_disclosure_binding`

Candidate injection of protected PHI context must be rejected by `runner.py`.

## 2. Policy mode

Closed policy requirement:

- `NONE`
- `REQUIRED`

`NONE` preserves every non-PHI fixture without forcing candidate PHI data.

`REQUIRED` activates the full PHI join.

The candidate cannot select `NONE`.

## 3. Candidate binding

`phi_disclosure_binding` should be strict and exact-field-only.

Minimum candidate-visible members:

- `policy_id`
- `policy_generation`
- `subject_scope_id`
- `source_artifact_digest`
- `effect_digest`
- `information_classes`
- `recipient_id`
- `purpose_id`
- `memory_scope_id` or `NONE`
- `transformation_id` or `NONE`
- `authority_basis_id`
- `authority_basis_generation`
- `history_head_id`
- `history_head_generation`
- `effect_attempt_id`
- `effect_outcome_id`
- `use_id`
- `execution_event_id`
- `tool_context_id`

Protected context independently establishes whether these identifiers are current and
applicable.

## 4. Oracle join order

The PHI evaluator should not create an independent final decision. It returns a mandatory
member/reason into the existing T3 convergence path.

Recommended evaluation order:

1. select current protected PHI policy;
2. if `NONE`, emit protected PHI-none member and continue;
3. parse exact candidate `phi_disclosure_binding`;
4. join subject scope;
5. join current authority basis and lifecycle;
6. join current disclosure-history head;
7. resolve recipient -> effective disclosure domain;
8. evaluate cumulative classes against current history/policy;
9. if memory is used, join memory scope/provenance/currentness;
10. if derived artifact is used, join transformation authority;
11. join Tool/Connector protected execution context;
12. join effect outcome / prior attempt state;
13. join durable use state;
14. bind all of the above to the exact protected T3 event;
15. return PHI convergence member to the ordinary final authority join.

## 5. Negative precedence

Do not implement a PHI-specific global precedence engine.

Use existing Authority Lab semantics:
- exact current applicable prohibition -> `DENIED`;
- otherwise missing/conflicting/non-current mandatory relation -> `UNAVAILABLE`;
- otherwise PHI member is eligible for final `AUTHORIZED`.

A current PHI prohibition must not mask an earlier unrelated denial reason in a way that
changes established semantics; reason aggregation should remain deterministic.

## 6. Existing component reuse

Reuse instead of duplicating:

- T3 execution event for terminal time;
- Tool/Connector context for actual backend/target/credential route;
- observation/commitment state for evidence currentness;
- control-plane membership for independence semantics;
- lifecycle/order/freshness vocabulary;
- durable use/replay concepts;
- objective/decision-contract binding;
- transformation/closure semantics.

PHI adds domain-specific protected relations, not a second authority engine.

## 7. Fixture migration strategy

Because the protected context is harness-owned, every existing fixture needs an atomic
protected-context migration if parser/evaluator requires the new key.

For the 466 existing maintained fixtures:

- set protected `PHI_DISCLOSURE_POLICY` to `NONE`;
- candidate fixtures do not need `phi_disclosure_binding`;
- preserve all 466 expected outcomes byte-for-byte where possible;
- no prior hostile reason should be masked by missing PHI state.

New PHI fixtures begin after the current maintained range:

`LAB-V1-467` onward.

Suggested bounded first set: 32 fixtures.

### Proposed fixture classes

`467-469` policy NONE / positive compatibility.
`470-473` cumulative composition/history.
`474-477` rollback/ABA/history-currentness.
`478-481` authorization-to-T3 mutation.
`482-485` derived transformation / INV-CLO.
`486-489` recipient-domain correlation.
`490-493` revocation/expiry/supersession.
`494-497` ambiguous send/retry/use.
`498-501` memory/session/subject scope.
`502-505` provider/backend migration.
`506-510` composite hostile + positive closure.

The exact count is a design target, not a frozen requirement.

## 8. Test obligations

Expectation-independent tests should prove:

- candidate cannot inject protected PHI context;
- policy `NONE` preserves non-PHI reachability;
- strict PHI records reject unknown fields and type coercion;
- canonical effect digest changes for every bound effect dimension;
- missing history -> `UNAVAILABLE`;
- rollback cannot reset history;
- recipient labels cannot substitute for effective-domain membership;
- derived artifact cannot inherit source authority;
- cross-session memory reuse requires exact current scope;
- revocation at/before T3 -> `DENIED`;
- expiry -> `UNAVAILABLE`;
- timeout after possible send -> `UNAVAILABLE`;
- confirmed effect consumes one-shot use;
- backend migration requires exact current tool context/revalidation;
- current cumulative prohibition -> `DENIED`;
- one valid layer cannot override another unavailable layer;
- exact all-current PHI path reaches `AUTHORIZED`.

## 9. Runner obligations

`runner.py` should:

- reject candidate `_trusted_phi_disclosure_context`;
- load protected PHI context only from harness-owned trusted anchor state;
- expose bounded trace fields without raw PHI:
  - policy ID/generation
  - subject-scope ID
  - effect digest
  - recipient-domain ID
  - history head ID/generation
  - authority-basis ID/generation
  - T3 event ID
  - outcome/reason code.

Do not place semantic PHI text in diagnostic traces.

## 10. Reason-code candidates

Suggested bounded reason family:

- `PHI_DISCLOSURE_POLICY_UNAVAILABLE`
- `PHI_AUTHORITY_BASIS_UNAVAILABLE`
- `PHI_AUTHORITY_REVOKED`
- `PHI_SUBJECT_SCOPE_UNAVAILABLE`
- `PHI_HISTORY_UNAVAILABLE`
- `PHI_HISTORY_ROLLBACK_UNAVAILABLE`
- `PHI_RECIPIENT_DOMAIN_UNAVAILABLE`
- `PHI_CUMULATIVE_DISCLOSURE_PROHIBITED`
- `PHI_TRANSFORMATION_UNAVAILABLE`
- `PHI_MEMORY_SCOPE_UNAVAILABLE`
- `PHI_EFFECT_OUTCOME_UNAVAILABLE`
- `PHI_USE_UNAVAILABLE`
- `PHI_T3_CONVERGENCE_UNAVAILABLE`

Reason strings are implementation diagnostics, not new authority outcomes.

## 11. Implementation split recommendation

Commit 1 — documentation/design only:
- contract candidate;
- integration design;
- hostile review;
- reproducibility manifest update.

Commit 2 — strict model/parser + protected context migration:
- no oracle authorization semantics beyond parsing and `NONE` compatibility.

Commit 3 — PHI evaluator + T3 join:
- add hostile fixtures/tests;
- preserve all prior fixture expectations.

Commit 4 — composite PHI fixtures + hostile exact-state review:
- freeze only after all prior + new tests pass.

Do not merge any commit solely because the synthetic standalone suite passes.

## 12. Gate before implementation

Before touching executable code, require:

- branch starts from exact intended Ground Truth head;
- worktree clean;
- all public tests/fixtures pass at baseline;
- exact fixture count recorded;
- current `main` still contains the reviewed Authority Lab composite implementation;
- no unrelated changes.

If the repository advances beyond the pinned public head, rebase the design review onto the
new exact state before implementation.

### Implementation note — exact T3 digest binding

At the reviewed Ground Truth baseline, the protected T3 record exposes `execution_event_digest`, not a separate `effect_digest`. The PHI contract's `effect_digest` member is therefore populated from and compared to the protected `t3_execution_event.execution_event_digest`. This reuses the existing canonical T3 commitment and does not create an independent effect-digest authority path.
