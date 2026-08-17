import json


def test_register_stake_builds_trusted(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/agent_reputation_ledger.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 6000000000000000000
    contract.register()
    direct_vm.mock_web(r".*e\.test.*", {"status": 200, "body": "Delivered successfully."})
    direct_vm.mock_llm(r".*", json.dumps({"decision": "DELIVERED"}))
    for i in range(6):
        contract.record_delivery(agent=direct_alice, bounty_id=str(i),
                                 evidence_url="https://e.test/" + str(i),
                                 claimed="done")
    out = json.loads(contract.get_reputation(agent=direct_alice))
    assert out["staked"] == 6000000000000000000
    assert out["completed"] == 6
    assert out["tier"] == "TRUSTED"
    direct_vm.clear_mocks()


def test_undelivered_slashes_stake(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/agent_reputation_ledger.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 10000000000000000000
    contract.register()
    direct_vm.mock_web(r".*e\.test.*", {"status": 200, "body": "No delivery."})
    direct_vm.mock_llm(r".*", json.dumps({"decision": "UNDELIVERED"}))
    contract.record_delivery(agent=direct_alice, bounty_id="x",
                             evidence_url="https://e.test/fail", claimed="done")
    out = json.loads(contract.get_reputation(agent=direct_alice))
    assert out["slashed_count"] == 1
    assert out["slash_points"] == 1000000000000000000
    assert out["staked"] == 9000000000000000000
    assert out["failed"] == 1
    direct_vm.clear_mocks()


def test_unregistered_agent_reverts(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/agent_reputation_ledger.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*e\.test.*", {"status": 200, "body": "ok"})
    direct_vm.mock_llm(r".*", json.dumps({"decision": "DELIVERED"}))
    try:
        contract.record_delivery(agent=direct_alice, bounty_id="1",
                                 evidence_url="https://e.test/1", claimed="x")
        raise AssertionError("expected revert for unregistered agent")
    except Exception:
        pass
    out = json.loads(contract.get_reputation(agent=direct_alice))
    assert out["exists"] is False
    direct_vm.clear_mocks()
