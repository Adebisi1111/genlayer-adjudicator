# Agent Payment Adjudicator — GenLayer Intelligent Contract

A reusable GenLayer Intelligent Contract that resolves payment disputes between
autonomous agents using **real GenLayer consensus logic** (the equivalence
principle) over live web data and LLM judgment.

## Why this exists

The agentic economy (x402 payments, ERC-8004 agent identity, A2A) builds the
happy path — but none of those layers ship **dispute resolution**. If a payer
pays an agent and the service isn't delivered, there's no neutral judge. This
contract fills that gap: it fetches the live service state, asks an LLM to
judge delivery, and releases or refunds the deposited funds accordingly.

## How it works

1. **`open_dispute(agent, service_url, claim)`** — the payer deposits the
   contested amount (payable). The deposit is held by the contract.
2. **`resolve(dispute_id)`** — anyone can trigger resolution. The contract:
   - fetches the live service page via `gl.nondet.web.render(service_url)`
   - asks an LLM to judge delivery (`gl.nondet.exec_prompt`)
   - runs both through the **equivalence principle**
     (`gl.vm.run_nondet(leader, validator)`) so leader/validator outputs agree
   - emits a value transfer to the **agent** if delivered, or refunds the
     **payer** if not (`gl.get_contract_at(addr).emit_transfer(value=...)`)
3. **`get_dispute(dispute_id)`** — view the current state and verdict.

## State design

```python
@allow_storage
@dataclass
class Dispute:
    id: str
    payer: str        # hex
    agent: str        # hex
    amount: u256
    service_url: str
    claim: str
    status: str       # 'open' | 'resolved_payer' | 'resolved_agent'
    verdict: str      # '' | 'DELIVERED' | 'NOT_DELIVERED'
```

Storage uses GenLayer-native `TreeMap` / `u256` (not `dict`/`list`).

## Run the tests

```bash
python -m pytest tests/direct/ -q
```

Three direct-mode tests cover: refund-on-non-delivery, pay-agent-on-delivery,
and double-resolution revert. No server or Docker required.

## Files

- `contracts/agent_payment_adjudicator.py` — the contract
- `tests/direct/test_agent_payment_adjudicator.py` — direct-mode tests

Built for the GenLayer builder contribution program.
