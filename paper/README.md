# Ground Truth paper

**Ground Truth: Deterministic Falsification of Authority Continuity in Autonomous Systems**

David B. Boyd  
Independent Researcher  
Antigonish, Nova Scotia, Canada  
Research preprint v1.0 — 27 September 2026

## Public reading copy

Google Docs:
https://docs.google.com/document/d/1oG9gGmoeVaAcIInzyC-7BbdL1sdhW0oB/edit?usp=drivesdk&ouid=100784840950225384768&rtpof=true&sd=true

## Publication artifacts

The finalized v1.0 files are:

- `Ground_Truth_Paper_v1_0_Preprint_David_B_Boyd.pdf` — canonical publication PDF
- `Ground_Truth_Paper_v1_0_Preprint_David_B_Boyd.docx` — editable source document
- `SHA256SUMS.txt` — cryptographic checksums for both files

The repository metadata and checksums are committed here first; the binary PDF/DOCX must be uploaded without altering their bytes so the recorded SHA-256 values remain valid.

## Evidence binding

The paper is written against the remotely inspectable Ground Truth v1 research state:

- public repository publication merge: `c57bdd0e85f14f1f927901fb880a2d3cbfdb06fa`
- freeze documentation commit: `3d09acc804bc1271965696f2d9561143ca28b835`
- frozen research HEAD: `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- schema: `authority-lab-v1`
- corpus: `LAB-V0-001..012` and `LAB-V1-013..466`
- public tests on freeze branch: 260/260 PASS
- Authority Lab fixtures at frozen research HEAD: 466/466 PASS

PASS is a bounded failure-to-falsify result under the exact stated model, corpus, implementation, assumptions, and Git state. It is not a claim of universal security, formal proof, production readiness, or complete authority modeling.

## Post-freeze PHI disclosure-authority paper

**Ground Truth for PHI: Deterministic Authorization of Semantic Disclosure in AI Systems**

Publication-candidate artifacts:
- `Ground_Truth_for_PHI_Preprint_v1_0_David_B_Boyd.md`
- `Ground_Truth_for_PHI_Preprint_v1_0_David_B_Boyd.docx`
- `Ground_Truth_for_PHI_Preprint_v1_0_David_B_Boyd.pdf`
- `PHI_SHA256SUMS.txt` — SHA-256 checksums for the PHI Markdown, DOCX, and PDF artifacts

Evidence binding:
- pinned case study: `ethereum/zkapi@045b444ea1b52538d1b40273c7cb6ed09468a052`
- reviewed feature head: `0b88a4814496c32c2a729f350106e0038f1b8e63`
- merged Ground Truth state: `05ab14a7c260e8d94e737a8d4a524385bb673515`
- schema: unchanged `authority-lab-v1`
- fixture corpus: 478
- Authority Lab regression: 265/265 PASS
- all-fixture runner: PASS
- hostile review: PASS
- final bounded implementation verifier: OVERALL PASS

This PHI paper is a post-freeze extension. It does not rewrite the historical evidence binding of the v1.0 authority-continuity preprint above.
