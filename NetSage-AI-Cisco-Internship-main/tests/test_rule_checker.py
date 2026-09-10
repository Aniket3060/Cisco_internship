"""
NetSage AI: Rule Checker Unit Tests
====================================
Tests for deterministic network validation rules.
"""

import json
import unittest
from src.rule_checker import NetworkRuleChecker, RuleViolation


class TestNetworkRuleChecker(unittest.TestCase):

    def setUp(self):
        # Base minimal valid network
        self.valid_network = {
            "devices": [
                {
                    "name": "R1",
                    "type": "router",
                    "interfaces": [
                        {
                            "name": "Gi0/0",
                            "ip_address": "192.168.1.1/24",
                            "status": "up",
                            "protocol": "up",
                        }
                    ],
                    "vlans": [1],
                    "static_routes": [],
                    "access_lists": [],
                }
            ],
            "hosts": [
                {
                    "name": "PC1",
                    "ip_address": "192.168.1.50",
                    "subnet_mask": "255.255.255.0",
                    "default_gateway": "192.168.1.1",
                }
            ],
            "links": [],
        }

    def test_clean_network_passes(self):
        checker = NetworkRuleChecker(self.valid_network)
        violations = checker.run_all_checks()
        self.assertEqual(len(violations), 0)

    def test_duplicate_ip_detection(self):
        bad_network = {
            "devices": [],
            "hosts": [
                {"name": "PC1", "ip_address": "10.0.0.5", "subnet_mask": "/24"},
                {"name": "PC2", "ip_address": "10.0.0.5", "subnet_mask": "/24"},
            ],
            "links": [],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-001", rule_ids)

    def test_broadcast_ip_detection(self):
        bad_network = {
            "devices": [],
            "hosts": [
                {"name": "PC1", "ip_address": "192.168.1.255", "subnet_mask": "/24"}
            ],
            "links": [],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-002B", rule_ids)

    def test_gateway_outside_subnet_detection(self):
        bad_network = {
            "devices": [
                {
                    "name": "R1",
                    "type": "router",
                    "interfaces": [{"name": "Gi0/0", "ip_address": "10.0.0.1/24", "status": "up", "protocol": "up"}],
                }
            ],
            "hosts": [
                {
                    "name": "PC1",
                    "ip_address": "192.168.1.50",
                    "subnet_mask": "/24",
                    "default_gateway": "10.0.0.1",
                }
            ],
            "links": [],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-003A", rule_ids)

    def test_interface_admin_down_detection(self):
        bad_network = {
            "devices": [
                {
                    "name": "R1",
                    "type": "router",
                    "interfaces": [
                        {
                            "name": "Gi0/0",
                            "ip_address": "192.168.1.1/24",
                            "status": "administratively down",
                            "protocol": "down",
                        }
                    ],
                }
            ],
            "hosts": [],
            "links": [],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-004A", rule_ids)

    def test_native_vlan_mismatch_detection(self):
        bad_network = {
            "devices": [],
            "hosts": [],
            "links": [
                {
                    "src_device": "S1",
                    "src_port": "Gi0/1",
                    "src_native_vlan": 99,
                    "dst_device": "S2",
                    "dst_port": "Gi0/1",
                    "dst_native_vlan": 1,
                }
            ],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-005B", rule_ids)

    def test_acl_shadowing_detection(self):
        bad_network = {
            "devices": [
                {
                    "name": "R1",
                    "type": "router",
                    "access_lists": [
                        {
                            "name": "BLOCK_ALL_EARLY",
                            "rules": [
                                {"sequence": 10, "action": "deny", "source": "any", "destination": "any"},
                                {"sequence": 20, "action": "permit", "source": "192.168.1.0/24", "destination": "any"},
                            ],
                        }
                    ],
                }
            ],
            "hosts": [],
            "links": [],
        }
        checker = NetworkRuleChecker(bad_network)
        violations = checker.run_all_checks()
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("RULE-007A", rule_ids)


if __name__ == "__main__":
    unittest.main()
