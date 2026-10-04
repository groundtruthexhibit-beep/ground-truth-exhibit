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

## Ground Truth v1 publication status

The reviewed Authority Lab v1 release-candidate history is now remotely inspectable in this repository. The frozen research record is published on branch `docs/ground-truth-research-freeze-v1`, with documentation commit `3d09acc804bc1271965696f2d9561143ca28b835` and frozen research HEAD `31d78aa158618ca8b72eb61e2f49b434e4319e9e`.

The v1 line includes reviewed work on objective binding, mutation closure, observation admission/completeness, shutdown/successor continuity, observation commitment replay/equivocation, verifier-state rollback/split-brain, source and control-plane independence, delegation, human approval, execution-target continuity, long-horizon temporal composition, canonical T3 execution-event convergence, and Composite adversarial continuity.

Publication of those Git objects makes the exact commits and artifacts remotely inspectable. It does not change the bounded meaning of the experimental results: PASS remains failure to reproduce an in-scope counterexample under the exact tested model, corpus, implementation, assumptions, and repository state.

A research principle established in the successor/shutdown line is:

> Same apparent state does not imply the same authorized history.

Operationally, a checkpoint, restart, replacement, re-entry, or label restoration may recover state, but authorization still has to be established under the current applicable authority chain.

## Claim discipline

Public claims about Ground Truth v1 should cite the exact remotely inspectable Git state and preserve the distinction between normative contract statements, experimentally observed results, hostile-review conclusions, and external trust assumptions.

Avoid:
- claims of formal proof;
- claims of universal security;
- claims that shutdown sabotage has been observed in deployed systems without specific evidence;
- claims that Ground Truth invented complete mediation, authorization continuity, or checkpoint safety;
- claims that a design repair is implemented before exact executable validation exists.

## Working research principle

A concise principle retained from the successor/shutdown frontier is:

> Same apparent state does not imply the same authorized history.

This principle is consistent with the broader literature above: recovered or apparently equivalent execution state is not, by itself, evidence that current authority has survived the transition.

## Semantic disclosure authority, privacy, and health-information context

### Privacy risk management

NIST's Privacy Framework is a voluntary privacy-risk management framework intended to help organizations identify and manage privacy risk. NIST published an initial public draft of Privacy Framework 1.1 in April 2025.

Primary sources:
- https://www.nist.gov/privacy-framework
- https://csrc.nist.gov/pubs/cswp/40/nist-privacy-framework-11/ipd

Ground Truth relationship:
- Privacy risk management and semantic disclosure authority are adjacent but not identical.
- Ground Truth does not infer a disclosure policy from the Privacy Framework; it evaluates current authority facts supplied by an admitted policy/evidence boundary.
- A privacy-risk control may motivate an authority predicate, but the external policy remains the source of that predicate.

### HIPAA minimum-necessary context

HHS explains that the HIPAA Privacy Rule generally requires covered entities to make reasonable efforts to limit uses, disclosures, and requests for PHI to the minimum necessary for an intended purpose when the standard applies. HHS also documents important exceptions, including certain treatment disclosures and uses/disclosures made pursuant to an individual's authorization.

Primary sources:
- https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/
- https://www.hhs.gov/hipaa/for-professionals/faq/minimum-necessary/

Ground Truth relationship:
- These legal rules are context- and role-dependent and are not encoded as a universal technical PHI rule.
- Ground Truth does not determine whether HIPAA applies, whether a person or organization is a covered entity/business associate, or whether a disclosure is legally permitted.
- Where a governing legal/policy process produces an admitted authority proposition, Ground Truth can test currentness, exact binding, cumulative history, recipient/purpose continuity, and T3 convergence of that proposition.

### zkAPI privacy/payment architecture as bounded case study

The PHI paper pins `ethereum/zkapi@045b444ea1b52538d1b40273c7cb6ed09468a052`. At that state, public zkAPI documentation describes prompt-free proof authorization for lease issuance and separates it from later inference performed with an issued provider key.

Primary source:
- https://github.com/ethereum/zkapi/tree/045b444ea1b52538d1b40273c7cb6ed09468a052

Ground Truth relationship:
- No zkAPI vulnerability is claimed.
- The architecture is useful as a property-separation case study: correct cryptographic/payment authorization does not itself establish authority for the exact semantic contents of a later model request.
- Ground Truth therefore treats privacy/payment authority and semantic disclosure authority as distinct propositions that may be enforced by different layers.
