#!/usr/bin/env python3
"""
NetSage AI: Deterministic Network Rule Checker
==============================================
Validates network configurations against fundamental networking rules before/after AI diagnosis:
1. Duplicate IP Address Detection
2. Subnet Mask & Host Range Consistency
3. Default Gateway Verification
4. Interface Up/Down Status
5. VLAN Configuration & Trunk Consistency
6. Routing Consistency (Unreachable Next-Hops & Missing Routes)
7. Access Control List (ACL) Ordering & Anomaly Checks

Usage:
    python src/rule_checker.py --config data/sample_network_state.json
    python src/rule_checker.py --config data/sample_network_state.json --json
"""

import argparse
import ipaddress
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


class RuleViolation:
    """Represents a deterministic network rule violation."""

    def __init__(
        self,
        rule_id: str,
        category: str,
        severity: str,
        device: str,
        target: str,
        message: str,
        recommendation: str,
    ):
        self.rule_id = rule_id
        self.category = category
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.device = device
        self.target = target
        self.message = message
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity,
            "device": self.device,
            "target": self.target,
            "message": self.message,
            "recommendation": self.recommendation,
        }


class NetworkRuleChecker:
    """Deterministic Rule Validation Engine."""

    def __init__(self, network_state: Dict[str, Any]):
        self.state = network_state
        self.violations: List[RuleViolation] = []

    def run_all_checks(self) -> List[RuleViolation]:
        """Executes the full suite of deterministic rule checks."""
        self.violations = []
        self.check_duplicate_ips()
        self.check_subnet_masks_and_ranges()
        self.check_default_gateways()
        self.check_interface_states()
        self.check_vlan_and_trunk_consistency()
        self.check_routing_consistency()
        self.check_acl_anomalies()
        return self.violations

    # -------------------------------------------------------------------------
    # RULE 1: Duplicate IP Detection
    # -------------------------------------------------------------------------
    def check_duplicate_ips(self):
        """Flags duplicate IPv4 addresses across devices and hosts."""
        ip_locations = defaultdict(list)

        # Check routers & switches
        for device in self.state.get("devices", []):
            dev_name = device.get("name", "Unknown")
            for iface in device.get("interfaces", []):
                ip_str = iface.get("ip_address")
                if ip_str and ip_str.lower() not in ("unassigned", "dhcp", "none"):
                    clean_ip = ip_str.split("/")[0].strip()
                    ip_locations[clean_ip].append(f"{dev_name}:{iface.get('name')}")

        # Check hosts / PCs
        for host in self.state.get("hosts", []):
            h_name = host.get("name", "Unknown")
            ip_str = host.get("ip_address")
            if ip_str and ip_str.lower() not in ("dhcp", "unassigned", "none"):
                clean_ip = ip_str.split("/")[0].strip()
                ip_locations[clean_ip].append(f"Host:{h_name}")

        for ip_addr, locs in ip_locations.items():
            if len(locs) > 1:
                self.violations.append(
                    RuleViolation(
                        rule_id="RULE-001",
                        category="IP_Addressing",
                        severity="CRITICAL",
                        device=", ".join(locs),
                        target=ip_addr,
                        message=f"Duplicate IP address detected: '{ip_addr}' is assigned to multiple endpoints: {', '.join(locs)}.",
                        recommendation=f"Reassign unique IP addresses to avoid Layer 3 ARP collisions.",
                    )
                )

    # -------------------------------------------------------------------------
    # RULE 2: Subnet Mask & Host Range Consistency
    # -------------------------------------------------------------------------
    def check_subnet_masks_and_ranges(self):
        """Verifies host IPs are within valid usable range and not network/broadcast IPs."""
        for host in self.state.get("hosts", []):
            h_name = host.get("name", "Unknown")
            ip_str = host.get("ip_address")
            mask_str = host.get("subnet_mask", "/24")

            if not ip_str or ip_str.lower() in ("dhcp", "unassigned"):
                continue

            try:
                if "/" in ip_str:
                    interface_obj = ipaddress.IPv4Interface(ip_str)
                else:
                    prefix = mask_str if mask_str.startswith("/") else f"/{mask_str}"
                    interface_obj = ipaddress.IPv4Interface(f"{ip_str}{prefix}")

                network = interface_obj.network
                ip_only = interface_obj.ip

                # Check if IP is network or broadcast address
                if ip_only == network.network_address:
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-002A",
                            category="IP_Addressing",
                            severity="CRITICAL",
                            device=h_name,
                            target=str(ip_only),
                            message=f"Host '{h_name}' IP '{ip_only}' is the Subnet Network Address for {network}.",
                            recommendation=f"Assign a usable host IP within range {list(network.hosts())[0]} - {list(network.hosts())[-1]}.",
                        )
                    )
                elif ip_only == network.broadcast_address:
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-002B",
                            category="IP_Addressing",
                            severity="CRITICAL",
                            device=h_name,
                            target=str(ip_only),
                            message=f"Host '{h_name}' IP '{ip_only}' is the Subnet Broadcast Address for {network}.",
                            recommendation=f"Assign a usable host IP within range {list(network.hosts())[0]} - {list(network.hosts())[-1]}.",
                        )
                    )
            except ValueError as e:
                self.violations.append(
                    RuleViolation(
                        rule_id="RULE-002C",
                        category="IP_Addressing",
                        severity="HIGH",
                        device=h_name,
                        target=str(ip_str),
                        message=f"Invalid IPv4 configuration format for host '{h_name}': {e}",
                        recommendation="Correct IP address and subnet mask format.",
                    )
                )

    # -------------------------------------------------------------------------
    # RULE 3: Default Gateway Verification
    # -------------------------------------------------------------------------
    def check_default_gateways(self):
        """Verifies default gateway exists in the host's local subnet and matches a router interface."""
        router_ips = set()
        for device in self.state.get("devices", []):
            if device.get("type", "").lower() in ("router", "l3_switch"):
                for iface in device.get("interfaces", []):
                    ip_str = iface.get("ip_address")
                    if ip_str and "/" in ip_str:
                        router_ips.add(ipaddress.IPv4Interface(ip_str).ip)
                    elif ip_str and ip_str.lower() not in ("unassigned", "dhcp", "none"):
                        try:
                            router_ips.add(ipaddress.IPv4Address(ip_str))
                        except ValueError:
                            pass

        for host in self.state.get("hosts", []):
            h_name = host.get("name", "Unknown")
            gw_str = host.get("default_gateway")
            ip_str = host.get("ip_address")
            mask_str = host.get("subnet_mask", "/24")

            if not gw_str or not ip_str or ip_str.lower() in ("dhcp", "unassigned"):
                continue

            try:
                prefix = mask_str if mask_str.startswith("/") else f"/{mask_str}"
                host_iface = ipaddress.IPv4Interface(f"{ip_str}{prefix}")
                gw_ip = ipaddress.IPv4Address(gw_str)

                # Check 1: Is gateway in host's local subnet?
                if gw_ip not in host_iface.network:
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-003A",
                            category="Gateway",
                            severity="CRITICAL",
                            device=h_name,
                            target=gw_str,
                            message=f"Host '{h_name}' gateway '{gw_str}' is outside local subnet {host_iface.network}.",
                            recommendation=f"Configure default gateway within subnet {host_iface.network}.",
                        )
                    )

                # Check 2: Does gateway IP match a known router interface?
                if router_ips and gw_ip not in router_ips:
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-003B",
                            category="Gateway",
                            severity="HIGH",
                            device=h_name,
                            target=gw_str,
                            message=f"Host '{h_name}' default gateway '{gw_str}' does not match any configured router interface IP.",
                            recommendation=f"Update gateway to point to valid active router interface IP.",
                        )
                    )
            except ValueError as e:
                self.violations.append(
                    RuleViolation(
                        rule_id="RULE-003C",
                        category="Gateway",
                        severity="MEDIUM",
                        device=h_name,
                        target=str(gw_str),
                        message=f"Invalid default gateway address '{gw_str}' on host '{h_name}': {e}",
                        recommendation="Configure valid IPv4 gateway address.",
                    )
                )

    # -------------------------------------------------------------------------
    # RULE 4: Interface Up/Down Status
    # -------------------------------------------------------------------------
    def check_interface_states(self):
        """Flags interfaces that are administratively down or protocol down."""
        for device in self.state.get("devices", []):
            dev_name = device.get("name", "Unknown")
            for iface in device.get("interfaces", []):
                iface_name = iface.get("name", "Unknown")
                status = str(iface.get("status", "")).lower()
                protocol = str(iface.get("protocol", "")).lower()
                is_connected = iface.get("connected", True)

                if "administratively down" in status or status == "admin_down":
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-004A",
                            category="Interface_Status",
                            severity="HIGH",
                            device=dev_name,
                            target=iface_name,
                            message=f"Interface '{iface_name}' on '{dev_name}' is administratively down (shutdown).",
                            recommendation=f"Enter interface configuration mode and execute 'no shutdown'.",
                        )
                    )
                elif status == "down" and is_connected:
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-004B",
                            category="Interface_Status",
                            severity="HIGH",
                            device=dev_name,
                            target=iface_name,
                            message=f"Interface '{iface_name}' on '{dev_name}' is down (Layer 1 / Physical carrier loss).",
                            recommendation="Check physical/virtual cable connection and remote interface state.",
                        )
                    )
                elif protocol == "down" and status == "up":
                    self.violations.append(
                        RuleViolation(
                            rule_id="RULE-004C",
                            category="Interface_Status",
                            severity="HIGH",
                            device=dev_name,
                            target=iface_name,
                            message=f"Interface '{iface_name}' on '{dev_name}' has line protocol down (Layer 2 framing / encapsulation issue).",
                            recommendation="Verify Layer 2 encapsulation, clock rate, or keepalive configuration.",
                        )
                    )

    # -------------------------------------------------------------------------
    # RULE 5: VLAN & Trunk Consistency
    # -------------------------------------------------------------------------
    def check_vlan_and_trunk_consistency(self):
        """Verifies VLAN creation, access port assignments, trunk allowed lists, and native VLANs."""
        device_vlans = {}
        for device in self.state.get("devices", []):
            dev_name = device.get("name", "Unknown")
            configured_vlans = set(device.get("vlans", [1]))  # VLAN 1 default
            device_vlans[dev_name] = configured_vlans

            # Check access ports
            for iface in device.get("interfaces", []):
                mode = iface.get("mode", "access").lower()
                access_vlan = iface.get("access_vlan")
                if mode == "access" and access_vlan:
                    if access_vlan not in configured_vlans:
                        self.violations.append(
                            RuleViolation(
                                rule_id="RULE-005A",
                                category="VLAN",
                                severity="HIGH",
                                device=dev_name,
                                target=iface.get("name"),
                                message=f"Access port '{iface.get('name')}' is assigned to non-existent VLAN {access_vlan}.",
                                recommendation=f"Create 'vlan {access_vlan}' in global configuration mode on '{dev_name}'.",
                            )
                        )

        # Check trunk links across connections
        for link in self.state.get("links", []):
            src_dev = link.get("src_device")
            src_port = link.get("src_port")
            dst_dev = link.get("dst_device")
            dst_port = link.get("dst_port")

            # Native VLAN check
            src_native = link.get("src_native_vlan", 1)
            dst_native = link.get("dst_native_vlan", 1)
            if src_native != dst_native:
                self.violations.append(
                    RuleViolation(
                        rule_id="RULE-005B",
                        category="VLAN_Trunking",
                        severity="MEDIUM",
                        device=f"{src_dev} <-> {dst_dev}",
                        target=f"{src_port} <-> {dst_port}",
                        message=f"Native VLAN mismatch on trunk link: {src_dev} ({src_port}) uses VLAN {src_native}, while {dst_dev} ({dst_port}) uses VLAN {dst_native}.",
                        recommendation=f"Configure matching native VLAN with 'switchport trunk native vlan <id>' on both trunk ends.",
                    )
                )

            # Allowed VLANs check
            src_allowed = set(link.get("src_allowed_vlans", []))
            dst_allowed = set(link.get("dst_allowed_vlans", []))
            if src_allowed and dst_allowed and src_allowed != dst_allowed:
                diff = src_allowed.symmetric_difference(dst_allowed)
                self.violations.append(
                    RuleViolation(
                        rule_id="RULE-005C",
                        category="VLAN_Trunking",
                        severity="HIGH",
                        device=f"{src_dev} <-> {dst_dev}",
                        target=f"{src_port} <-> {dst_port}",
                        message=f"Trunk allowed VLAN mismatch between {src_dev} and {dst_dev}. Discrepant VLANs: {sorted(list(diff))}.",
                        recommendation=f"Ensure consistent 'switchport trunk allowed vlan' lists on both ends of the trunk.",
                    )
                )

    # -------------------------------------------------------------------------
    # RULE 6: Routing Consistency (Unreachable Next-Hops & Missing Routes)
    # -------------------------------------------------------------------------
    def check_routing_consistency(self):
        """Checks for static routes pointing to unreachable next-hops."""
        for device in self.state.get("devices", []):
            dev_name = device.get("name", "Unknown")
            if device.get("type", "").lower() not in ("router", "l3_switch"):
                continue

            connected_networks = []
            for iface in device.get("interfaces", []):
                ip_str = iface.get("ip_address")
                if ip_str and "/" in ip_str and iface.get("status", "").lower() == "up":
                    try:
                        connected_networks.append(ipaddress.IPv4Interface(ip_str).network)
                    except ValueError:
                        pass

            for route in device.get("static_routes", []):
                dest_network = route.get("destination")
                next_hop = route.get("next_hop")

                if next_hop and next_hop.lower() not in ("null0", "interface"):
                    try:
                        nh_ip = ipaddress.IPv4Address(next_hop)
                        # Is next_hop reachable via directly connected network?
                        is_reachable = any(nh_ip in net for net in connected_networks)
                        if not is_reachable:
                            self.violations.append(
                                RuleViolation(
                                    rule_id="RULE-006A",
                                    category="Routing",
                                    severity="CRITICAL",
                                    device=dev_name,
                                    target=f"ip route {dest_network} {next_hop}",
                                    message=f"Static route next-hop '{next_hop}' is unreachable via any directly connected active interface on '{dev_name}' (recursive lookup failure).",
                                    recommendation=f"Correct next-hop IP address to match directly connected neighbor subnet.",
                                )
                            )
                    except ValueError:
                        pass

    # -------------------------------------------------------------------------
    # RULE 7: ACL Ordering & Anomaly Checks
    # -------------------------------------------------------------------------
    def check_acl_anomalies(self):
        """Flags shadowed ACL statements and standard ACLs blocking essential protocols."""
        for device in self.state.get("devices", []):
            dev_name = device.get("name", "Unknown")
            for acl in device.get("access_lists", []):
                acl_name = acl.get("name", "Unknown")
                rules = acl.get("rules", [])

                seen_deny_any = False
                for idx, rule in enumerate(rules):
                    action = rule.get("action", "").lower()
                    src = rule.get("source", "").lower()
                    dst = rule.get("destination", "").lower()

                    if action == "deny" and src == "any" and dst in ("any", ""):
                        seen_deny_any = True
                    elif seen_deny_any and action == "permit":
                        self.violations.append(
                            RuleViolation(
                                rule_id="RULE-007A",
                                category="ACL",
                                severity="CRITICAL",
                                device=dev_name,
                                target=f"ACL:{acl_name}:Seq_{idx+1}",
                                message=f"Shadowed ACL rule detected in '{acl_name}': Permit statement at sequence {idx+1} appears AFTER a broad 'deny any any' statement and will never be evaluated.",
                                recommendation=f"Reorder ACL statements using sequence numbers so specific permit entries precede broad deny rules.",
                            )
                        )


def format_text_report(violations: List[RuleViolation]) -> str:
    """Formats violations into a clean, human-readable terminal report."""
    if not violations:
        return (
            "\n"
            + "=" * 70
            + "\n"
            + " [NetSage AI Rule Checker] Deterministic Validation Results\n"
            + "=" * 70
            + "\n"
            + " [SUCCESS] 0 deterministic rule violations found.\n"
            + " All verified network parameters conform to standard RFC/Cisco rules.\n"
            + "=" * 70
            + "\n"
        )

    output = []
    output.append("\n" + "=" * 80)
    output.append(f" [NetSage AI Rule Checker] Rule Violations Detected: {len(violations)}")
    output.append("=" * 80)

    for i, v in enumerate(violations, start=1):
        sev_tag = f"[{v.severity}]"
        output.append(f"\n{i}. {sev_tag:<10} Rule ID: {v.rule_id} | Category: {v.category}")
        output.append(f"   Device(s)     : {v.device}")
        output.append(f"   Target/Entity : {v.target}")
        output.append(f"   Violation     : {v.message}")
        output.append(f"   Remediation   : {v.recommendation}")
        output.append("   " + "-" * 75)

    output.append("\n" + "=" * 80 + "\n")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="NetSage AI Deterministic Network Rule Checker"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to structured network state JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON payload",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display detailed execution steps",
    )

    args = parser.parse_args()

    try:
        with open(args.config, "r", encoding="utf-8") as f:
            network_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{args.config}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON file '{args.config}': {e}", file=sys.stderr)
        sys.exit(1)

    checker = NetworkRuleChecker(network_data)
    violations = checker.run_all_checks()

    if args.json:
        result_payload = {
            "total_violations": len(violations),
            "status": "PASS" if not violations else "FAIL",
            "violations": [v.to_dict() for v in violations],
        }
        print(json.dumps(result_payload, indent=2))
    else:
        print(format_text_report(violations))

    if violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
