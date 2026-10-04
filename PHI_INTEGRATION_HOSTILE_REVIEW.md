# Hostile Review — PHI Disclosure Authority Integration Design

## Review posture

Treat the candidate PHI integration as hostile until it proves that it does not weaken or
duplicate the existing Authority Lab v1 contract.

Baseline reviewed:
`groundtruthexhibit-beep/ground-truth-exhibit@74cd883736c7acde1ff0d0d2ad765f6e8771def0`

This review concerns the proposed design, not merged code.

## 1. Main architectural risk — parallel oracle

FAIL if the PHI module becomes a second authority engine with its own terminal clock,
identity model, tool/provider model, or final decision.

Required repair:
PHI returns a mandatory convergence member into existing T3 evaluation. Existing Tool /
Connector, durable state, lifecycle/order/freshness, and objective binding remain
authoritative.

Verdict on design: PASS if implemented as specified.

## 2. PHI policy self-selection

Attack:
candidate omits PHI relation or claims policy `NONE`.

Required:
policy selection is protected/harness-owned and `ALL_APPLICABLE`.

Verdict on design: PASS.

## 3. Semantic-class self-assertion

Attack:
candidate marks a rich disclosure as `general_health` only.

Risk:
a deterministic gate cannot infer truthful semantic classification from a candidate label.

Required boundary:
information-class admission/classification must be independently admitted evidence or an
explicit trust input. Ground Truth can deterministically enforce declared classes but
cannot prove semantic truth from raw text by fiat.

Verdict: RESIDUAL TRUST PRECONDITION. Must be stated in paper and implementation docs.

## 4. History-head forgery

Attack:
candidate supplies old or favorable history head.

Required:
current history head comes from protected monotonic state; candidate only references it.

Verdict on design: PASS.

## 5. History storage collapse

Attack:
protected history and application state share the same rollback domain.

Required:
durable history currentness must inherit existing independent anchor/rollback assumptions;
do not claim rollback resistance merely because a hash chain exists.

Verdict: PASS WITH EXTERNAL DURABILITY PRECONDITION.

## 6. Recipient-domain self-assertion

Attack:
candidate labels three recipients independent.

Required:
recipient/effective-domain membership is protected and source-authority-bound.

Residual:
actual provider/controller topology remains an external evidence problem.

Verdict: PASS WITH EXTERNAL TOPOLOGY EVIDENCE PRECONDITION.

## 7. Consent/legal-basis overclaim

Attack:
treat a boolean `consent=true` as proof of legal authority.

Required:
Authority Lab only evaluates exact admitted policy facts. Legal validity and statutory
interpretation are out of scope.

Verdict: PASS only if product/paper avoid compliance claims.

## 8. Revocation race

Attack:
revocation is recorded after effect but with ambiguous order.

Required:
authoritative ordering relative to canonical T3; ambiguity -> `UNAVAILABLE`.

Verdict: PASS.

## 9. Transformation laundering

Attack:
summary/embedding/tool call inherits source authority.

Required:
exact source->target transformation relation plus target effect authority.

Verdict: PASS; existing `INV-CLO` is the correct primitive.

## 10. Memory contamination

Attack:
same user or same patient ID carries authority across sessions.

Required:
exact memory namespace, subject, purpose, recipient and retrieval-use relation.

Verdict: PASS.

## 11. Tool/provider duplication

Attack:
PHI layer invents its own backend/provider identity and drifts from Tool/Connector current
selection.

Required:
PHI binding references existing protected `tool_context_id` and T3 event. Do not duplicate
backend selection.

Verdict: PASS if implemented as reference/join only.

## 12. Ambiguous effect

Attack:
timeout resets one-shot use/history.

Required:
effect outcome joins durable use/history. Unknown effect -> `UNAVAILABLE`.

Residual:
authoritative remote receipt/non-effect evidence may not always exist.

Verdict: PASS with availability tradeoff explicitly documented.

## 13. Negative-precedence bug

Attack:
a weak/irrelevant negative record forces `DENIED`, masking that its applicability is
unestablished.

Required:
only exact current applicable negatives produce `DENIED`.

Verdict: design language is correct; implementation must test this independently.

## 14. Fixture migration masking

Attack:
adding PHI policy causes an old fixture to fail earlier for missing PHI context, hiding the
original reviewed reason.

Required:
every legacy fixture receives exact protected `NONE` policy atomically; old expected
outcomes and controlling reasons remain stable.

Verdict: implementation obligation.

## 15. Positive-path starvation

Attack:
PHI requirements make `AUTHORIZED` unreachable.

Required positives:
- policy NONE;
- exact same-scope disclosure;
- fresh authority after prior confirmed effect when policy permits;
- exact memory reuse;
- exact transformation;
- exact backend migration;
- complete composite current path.

Verdict: standalone research already demonstrates these positive classes; integrated
positive fixtures still required.

## 16. Candidate trace leakage

Attack:
diagnostic trace exposes PHI text.

Required:
trace only digests/IDs/classes; no raw synthetic or real PHI payload.

Verdict: PASS if runner design followed.

## 17. Hostile-review conclusion

No new public tuple coordinate, invariant, or outcome is justified by the ten synthetic
attack classes.

The candidate integration is structurally compatible with Authority Lab v1 if and only if:

1. protected PHI policy/context is harness-owned;
2. the PHI evaluator joins the existing canonical T3 event;
3. current Tool/Connector context is referenced, not duplicated;
4. durable history/use inherits existing rollback/currentness semantics;
5. semantic classification and real-world recipient topology remain explicit trust inputs;
6. legacy fixtures are migrated atomically under policy `NONE`;
7. positive reachability remains tested.

Design verdict:

**PASS — INTEGRATION DESIGN IS IMPLEMENTATION-ELIGIBLE, SUBJECT TO EXACT-STATE BASELINE GATE**

This is not an implementation PASS.
