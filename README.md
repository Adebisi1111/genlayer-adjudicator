# GenLayer Agent Toolkit — Intelligent Contracts

Two reusable GenLayer Intelligent Contracts for the agentic economy, each built
with **real GenLayer consensus logic** (live web data + LLM judgment run through
the equivalence principle) and clear `TreeMap`/`u256` state design.

## 1. Agent Payment Adjudicator

Resolves payment disputes between autonomous agents. A payer deposits contested
funds; on `resolve()` the contract fetches the live service state, asks an LLM to
judge delivery via the equivalence principle, then emits a value transfer to the
agent (delivered) or refunds the payer (not delivered).

- `contracts/agent_payment_adjudicator.py`
- `tests/direct/test_agent_payment_adjudicator.py`
- Deployed (Bradbury): `0x890BE3B1168779Cde231793a0D599f7D08A06Cc8`
- Explorer: https://explorer-bradbury.genlayer.com/address/0x890BE3B1168779Cde231793a0D599f7D08A06Cc8

## 2. Agent Reputation Ledger

A **stake-weighted reputation primitive with slashing** — an economic-security
layer for the agentic economy. Agents stake GEN to register (value at risk).
`record_delivery` does not trust claims: it fetches live evidence and asks an
LLM to verify delivery via the equivalence principle. Verdicts:
`DELIVERED` advances reputation; `UNDELIVERED` **slashes 10% of staked GEN**.
Reputation = stake-weighted score minus slash penalties, tiered
TRUSTED / ESTABLISHED / NEW / UNPROVEN.

- `contracts/agent_reputation_ledger.py`
- `tests/direct/test_agent_reputation_ledger.py`
- Deployed (Bradbury): `0x6e0eeEAa36cF264fD307f0d804cB96EbB5c5902b`
- Explorer: https://explorer-bradbury.genlayer.com/address/0x6e0eeEAa36cF264fD307f0d804cB96EbB5c5902b

## Why these are real primitives (not thin wrappers)

- Both use `gl.nondet.web.render` + `gl.nondet.exec_prompt` + the equivalence
  principle (`gl.vm.run_nondet`) — genuine GenLayer consensus, not blind storage.
- The adjudicator moves value based on a verified verdict.
- The ledger rejects unverified outcome claims (reverts), so reputation can't be
  gamed by self-assertion.
- State is modeled with GenLayer-native `TreeMap` / `u256`.

## Run the tests

```bash
python -m pytest tests/direct/ -q   # 51 passed
```

Direct-mode tests require no server or Docker.

## Demo

Visual walkthrough of the adjudicator: https://adebisi1111.github.io/genlayer-adjudicator/demo/

## Accounts

Deployed from a dedicated test wallet (`0x61fd...`). Main wallet untouched.
Built for the GenLayer builder contribution program.
