import json


def test_adjudicate_refunds_payer(direct_vm, direct_deploy, direct_alice, direct_bob):
    """When service is NOT delivered, payer gets refunded."""
    contract = direct_deploy("contracts/agent_payment_adjudicator.py")
    direct_vm.sender = direct_alice  # payer
    direct_vm.value = 100  # deposit contested amount

    contract.open_dispute(direct_bob, "https://example.com/service", "Agent never delivered")

    # mock the live service page as "empty / not delivered"
    direct_vm.mock_web(r".*example\.com.*", {"status": 200, "body": "404 Not Found - service unavailable"})
    # mock LLM to judge NOT_DELIVERED
    direct_vm.mock_llm(r".*adjudicator.*", "NOT_DELIVERED")

    contract.resolve("DSP-0")
    result = json.loads(contract.get_dispute("DSP-0"))
    assert result["status"] == "resolved_payer", result
    assert result["verdict"] == "NOT_DELIVERED", result
    direct_vm.clear_mocks()


def test_adjudicate_pays_agent(direct_vm, direct_deploy, direct_alice, direct_bob):
    """When service IS delivered, agent gets paid."""
    contract = direct_deploy("contracts/agent_payment_adjudicator.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 100

    contract.open_dispute(direct_bob, "https://example.com/service", "Agent never delivered")

    direct_vm.mock_web(r".*example\.com.*", {"status": 200, "body": "Order #1234 completed successfully"})
    direct_vm.mock_llm(r".*adjudicator.*", "DELIVERED")

    contract.resolve("DSP-0")
    result = json.loads(contract.get_dispute("DSP-0"))
    assert result["status"] == "resolved_agent", result
    assert result["verdict"] == "DELIVERED", result
    direct_vm.clear_mocks()


def test_cannot_resolve_twice(direct_vm, direct_deploy, direct_alice, direct_bob):
    """Resolving an already-resolved dispute must revert."""
    contract = direct_deploy("contracts/agent_payment_adjudicator.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 100

    contract.open_dispute(direct_bob, "https://example.com/service", "broken")

    direct_vm.mock_web(r".*example\.com.*", {"status": 200, "body": "done"})
    direct_vm.mock_llm(r".*adjudicator.*", "DELIVERED")
    contract.resolve("DSP-0")

    with direct_vm.expect_revert("Dispute already resolved"):
        contract.resolve("DSP-0")
