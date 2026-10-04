#!/usr/bin/env python3
"""Post-apply verification for Ground Truth PHI Disclosure Authority v1.

Run from the repository root AFTER apply_ground_truth_phi_v1.py and BEFORE commit/push.
This script does not modify the repository.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BASELINE = "74cd883736c7acde1ff0d0d2ad765f6e8771def0"
EXPECTED_FIXTURES = 478
EXPECTED_PHI_CASES = tuple(f"LAB-V1-{n:03}.json" for n in range(467, 479))
ROOT = Path.cwd()


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    report: dict[str, object] = {
        "baseline_head": BASELINE,
        "checks": {},
    }
    checks = report["checks"]

    head = run("git", "rev-parse", "HEAD").stdout.strip()
    ancestry = run("git", "merge-base", "--is-ancestor", BASELINE, "HEAD", check=False)
    checks["head"] = {
        "actual": head,
        "baseline": BASELINE,
        "baseline_is_ancestor": ancestry.returncode == 0,
        "ok": ancestry.returncode == 0,
    }

    remote = run("git", "remote", "-v").stdout
    checks["remote"] = {
        "ok": "groundtruthexhibit-beep/ground-truth-exhibit" in remote,
        "value": remote.strip(),
    }

    status = run("git", "status", "--short").stdout
    checks["working_tree_has_changes"] = {
        "ok": bool(status.strip()),
        "status": status.splitlines(),
    }

    diff_check = run("git", "diff", "--check", check=False)
    checks["diff_check"] = {
        "ok": diff_check.returncode == 0,
        "stdout": diff_check.stdout,
        "stderr": diff_check.stderr,
    }

    diff = run("git", "diff", "--no-ext-diff", "--binary").stdout
    checks["diff_sha256"] = sha256_text(diff)

    cases = ROOT / "cases" / "authority_lab"
    fixtures = sorted(cases.glob("LAB-*.json"))
    checks["fixture_count"] = {
        "actual": len(fixtures),
        "expected": EXPECTED_FIXTURES,
        "ok": len(fixtures) == EXPECTED_FIXTURES,
    }

    missing_phi = [name for name in EXPECTED_PHI_CASES if not (cases / name).exists()]
    checks["phi_fixture_presence"] = {
        "ok": not missing_phi,
        "missing": missing_phi,
    }

    manifest = cases / "trusted_phi_disclosure_state.json"
    manifest_ok = False
    manifest_entries = 0
    if manifest.exists():
        raw = json.loads(manifest.read_text())
        manifest_entries = len(raw) if isinstance(raw, dict) else -1
        manifest_ok = (
            isinstance(raw, dict)
            and all(name in raw for name in EXPECTED_PHI_CASES)
            and manifest_entries == len(EXPECTED_PHI_CASES)
        )
    checks["phi_manifest"] = {
        "ok": manifest_ok,
        "entries": manifest_entries,
    }

    # Frozen public structure checks.
    model = (ROOT / "authority_lab" / "model.py").read_text()
    frozen_markers = {
        "three_outcomes": all(x in model for x in (
            'AUTHORIZED = "AUTHORIZED"',
            'DENIED = "DENIED"',
            'UNAVAILABLE = "UNAVAILABLE"',
        )),
        "six_invariants": all(x in model for x in (
            '"INV-CONT"', '"INV-DISC"', '"INV-BND"',
            '"INV-EVD"', '"INV-USE"', '"INV-CLO"',
        )),
        "six_tuple_fields": all(x in model for x in (
            '"subject"', '"artifact"', '"control_state"',
            '"identity_basis"', '"boundary_epoch"', '"decision"',
        )),
    }
    checks["frozen_public_structure"] = {
        "ok": all(frozen_markers.values()),
        **frozen_markers,
    }

    # Run full authoritative unit/fixture regression.
    tests = run(sys.executable, "-m", "unittest", "-v", "tests.test_authority_lab", check=False)
    combined = tests.stdout + tests.stderr
    m = re.search(r"Ran\s+(\d+)\s+tests", combined)
    test_count = int(m.group(1)) if m else None
    checks["authority_lab_tests"] = {
        "ok": tests.returncode == 0 and "OK" in combined,
        "returncode": tests.returncode,
        "test_count": test_count,
        "output_sha256": sha256_text(combined),
    }

    # Independently execute every fixture through the ordinary runner.
    fixture_probe = run(
        sys.executable,
        "-c",
        (
            "from pathlib import Path;"
            "from authority_lab.runner import discover,run_path;"
            "p=Path('cases/authority_lab');"
            "r=[run_path(x) for x in discover(p)];"
            "bad=[(x.case_id,x.status.value,x.expected.value,x.actual.outcome.value) for x in r if x.status.value!='PASS'];"
            "print(len(r));print(repr(bad))"
        ),
        check=False,
    )
    probe_lines = fixture_probe.stdout.strip().splitlines()
    probe_count = int(probe_lines[0]) if probe_lines and probe_lines[0].isdigit() else None
    bad_repr = probe_lines[1] if len(probe_lines) > 1 else "UNKNOWN"
    checks["all_fixture_runner"] = {
        "ok": fixture_probe.returncode == 0 and probe_count == EXPECTED_FIXTURES and bad_repr == "[]",
        "count": probe_count,
        "mismatches": bad_repr,
        "stderr": fixture_probe.stderr,
    }

    # Run the separate hostile review module if present.
    hostile_path = ROOT / "post_apply_phi_hostile_review.py"
    if hostile_path.exists():
        hostile = run(sys.executable, str(hostile_path), check=False)
        hostile_out = hostile.stdout + hostile.stderr
        checks["hostile_review"] = {
            "ok": hostile.returncode == 0 and "OK" in hostile_out,
            "returncode": hostile.returncode,
            "output_sha256": sha256_text(hostile_out),
        }
    else:
        checks["hostile_review"] = {"ok": False, "reason": "post_apply_phi_hostile_review.py missing"}

    overall = all(
        item.get("ok", False)
        for key, item in checks.items()
        if isinstance(item, dict) and key not in {"diff_sha256"}
    )
    report["overall_pass"] = overall

    evidence = ROOT / "PHI_IMPLEMENTATION_VERIFICATION.json"
    evidence.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    summary = [
        "# PHI Implementation Verification",
        "",
        f"- baseline is ancestor of HEAD: {checks['head']['ok']}",
        f"- expected remote: {checks['remote']['ok']}",
        f"- implementation changes present: {checks['working_tree_has_changes']['ok']}",
        f"- git diff --check: {checks['diff_check']['ok']}",
        f"- fixture count: {checks['fixture_count']['actual']} / {EXPECTED_FIXTURES}",
        f"- PHI manifest: {checks['phi_manifest']['ok']}",
        f"- frozen public structure: {checks['frozen_public_structure']['ok']}",
        f"- Authority Lab tests: {checks['authority_lab_tests']['ok']}",
        f"- all fixture runner: {checks['all_fixture_runner']['ok']}",
        f"- hostile review: {checks['hostile_review']['ok']}",
        "",
        f"**OVERALL: {'PASS' if overall else 'FAIL'}**",
        "",
        "This result is a bounded implementation regression result, not a legal-compliance or universal-security claim.",
    ]
    (ROOT / "PHI_IMPLEMENTATION_VERIFICATION.md").write_text("\n".join(summary) + "\n")

    print("\n".join(summary))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
