#!/usr/bin/env python3
"""Generate JSON fixtures from contract examples for frontend/E3 consumption."""

import json
from pathlib import Path

from myproj.core.contracts.examples import (
    ACTION_ENVELOPE_PAYLOAD,
    ATTENTION_DECISION_PAYLOAD,
    AUTHORITY_GRANT_PAYLOAD,
    DISCLOSURE_POLICY_PAYLOAD,
    DISCLOSURE_PREVIEW_PAYLOAD,
    SENDER_STACK_PAYLOAD,
)

FIXTURE_DIR = Path(__file__).parent


def write_fixture(name: str, payload: dict) -> None:
    """Write a payload to a JSON fixture file."""
    path = FIXTURE_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    print(f"Generated: {path}")


def main() -> None:
    """Generate all contract fixtures."""
    write_fixture("authority_grant", AUTHORITY_GRANT_PAYLOAD)
    write_fixture("sender_stack", SENDER_STACK_PAYLOAD)
    write_fixture("disclosure_policy", DISCLOSURE_POLICY_PAYLOAD)
    write_fixture("disclosure_preview", DISCLOSURE_PREVIEW_PAYLOAD)
    write_fixture("attention_decision", ATTENTION_DECISION_PAYLOAD)
    write_fixture("action_envelope", ACTION_ENVELOPE_PAYLOAD)

    print(f"\nGenerated {len(list(FIXTURE_DIR.glob('*.json')))} fixtures in {FIXTURE_DIR}")


if __name__ == "__main__":
    main()
