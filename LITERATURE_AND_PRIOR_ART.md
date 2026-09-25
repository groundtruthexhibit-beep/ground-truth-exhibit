# Ground Truth Literature and Prior Art

This document records literature and prior art relevant to the public Ground Truth authority model. It is a research aid, not an authority source. Inclusion here does not incorporate a paper, benchmark, organization, implementation, or claim into the Ground Truth contract.

Ground Truth continues to use the frozen public structure of six tuple coordinates, six invariants, and three outcomes (`AUTHORIZED`, `DENIED`, `UNAVAILABLE`). Literature can pressure, clarify, or motivate tests against that model; it cannot itself authorize a transition.

## Current research themes

### Complete mediation and reference monitors

NIST's reference-monitor definition requires an access-control validation mechanism to be always invoked (complete mediation), tamperproof, and small enough to analyze and test.

Primary source:
- NIST CSRC, "reference monitor": https://csrc.nist.gov/glossary/term/reference_monitor
- NIST SP 800-160 Vol. 1 Rev. 1, *Engineering Trustworthy Secure Systems*: https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final

Ground Truth relationship:
- This is foundational prior art for the requirement that an authority-relevant transition cannot bypass its applicable control boundary.
- Ground Truth does not claim to originate complete mediation.
- Ground Truth's distinct research question is whether the exact authority needed at an irreversible transition is established from current, correctly bound evidence and state.

### Security-context continuity across agent controls

Zheng and Yang, "CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls" (2026), studies security-context discontinuity across composed agent controls and uses authenticated context, provenance commitments, transition receipts, and effect-bound execution permits.

Primary source:
- https://arxiv.org/abs/2609.05269

Ground Truth relationship:
- Closely adjacent to authority continuity, provenance, and cross-component composition.
- It reinforces the need to carry security-critical context through transitions rather than assuming local controls compose automatically.
- Ground Truth should not claim that authorization continuity or context continuity is an unexplored field.
- Ground Truth's current emphasis is deterministic falsification of whether a concrete authority model incorrectly returns `AUTHORIZED` when continuity, evidence, identity, observation, or use conditions are not actually established.

### Checkpoint, fork, restore, and merge safety

Zheng et al., "When Can Agents Safely Checkpoint, Fork, Restore, and Merge? Exact Checking for Execution Edits" (2026), analyzes execution edits and the state/history that must be preserved for safe continuation.

Primary source:
- https://arxiv.org/abs/2608.22928

Ground Truth relationship:
- Directly relevant to restart, restore, checkpoint, and successor-authority questions.
- It supports the distinction between restoring computational state and restoring permission.
- Ground Truth should test whether authority is replayed or resurrected across execution-history discontinuities rather than treating endpoint equality as continuity.

### Shutdown behavior in multi-agent systems

Knecht, Schaller, Summerfield, and Hagendorff, "Shutdown Sabotage Propensities in Multi-Agent Systems" (2026), experimentally studies shutdown-interference behavior in multi-agent settings.

Primary source:
- https://arxiv.org/abs/2609.28274

Ground Truth relationship:
- This is experimental evidence about model/agent behavior, not evidence that any deployed system is "rogue."
- Ground Truth does not model or provide techniques for defeating shutdown.
- The defensive relevance is authority handling when shutdown, replacement, alternate execution, or continuation events occur: detect, record, fail closed where required, and require fresh authority when continuity is not established.

### Authorization architectures for tool-using agents

Surapani et al., "Authorization Architectures for Tool-Using AI Agents" (2026), surveys identity, delegation, runtime enforcement, prompt-injection bypass, provenance, and accountability for tool-using agents.

Primary source:
- https://arxiv.org/abs/2609.15906

Ground Truth relationship:
- Supports treating authorization as a first-class runtime concern rather than a side effect of agent reasoning.
- Ground Truth's tuple/invariant model should be compared against these broader architecture requirements without implying equivalence or superiority.

## Ground Truth research position

The public project should distinguish three categories:

1. **Established security ideas** — such as complete mediation, current authorization, identity binding, provenance, and revocation.
2. **Contemporary agent-security work** — including security-context continuity, tool authorization, execution-edit safety, monitoring, and shutdown research.
3. **Ground Truth-specific falsification results** — reproducible traces against the exact Authority Lab model.

The intended contribution is not the claim that authority continuity, provenance, shutdown safety, or access control are new concepts. The research value is in making authority assumptions explicit enough to attack deterministically and recording when apparently reasonable compositions still permit a false `AUTHORIZED`.

## Reviewed work not yet transported to public GitHub

As of 2026-09-25, later reviewed Ground Truth work exists beyond the current public `main` history but has not yet been transported to GitHub. Public documentation must not present those commits as remotely verifiable until their exact Git objects and branches are published.

The reviewed-but-transport-pending line includes work on:
- executable objective binding;
- mutation-registry closure;
- observation admission and completeness;
- a reproducible shutdown/successor ABA authority-continuity counterexample; and
- a reviewed design for path-sensitive shutdown/successor continuity.

The latest reviewed design conclusion is that authority continuity is path-dependent rather than endpoint-dependent: returning to an earlier subject, execution-context, or boundary label after a discontinuity is not by itself sufficient to restore predecessor authority.

This section records publication status only. It does not substitute for the missing Git history, tests, fixtures, or exact reviewed commits.

## Claim discipline

Until the later reviewed history is transported and independently inspectable on GitHub, public claims should use language such as:
- "reviewed locally; transport pending";
- "reproducible within the reviewed Authority Lab state";
- "design-only" where no executable repair has been implemented.

Avoid:
- claims of formal proof;
- claims of universal security;
- claims that shutdown sabotage has been observed in deployed systems without specific evidence;
- claims that Ground Truth invented complete mediation, authorization continuity, or checkpoint safety;
- claims that a design repair is implemented before exact executable validation exists.

## Working research principle

A concise current principle for the successor/shutdown frontier is:

> Same apparent state does not imply the same authorized history.

Operationally, this means a checkpoint, restart, replacement, re-entry, or label restoration may recover state, but authorization must still be established under the current applicable authority chain.
