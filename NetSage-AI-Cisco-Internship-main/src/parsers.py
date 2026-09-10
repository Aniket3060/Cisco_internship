"""
NetSage AI: CLI and Network State Parsers
Module for loading structured network topologies and parsing standard Cisco IOS show commands.
"""

import json
import re
from typing import Dict, Any, List, Optional


def load_network_state_file(filepath: str) -> Dict[str, Any]:
    """Loads a structured network state file (JSON)."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_show_ip_interface_brief(cli_text: str) -> List[Dict[str, str]]:
    """
    Parses 'show ip interface brief' text into structured interface records.
    Example line:
    GigabitEthernet0/0     192.168.1.1     YES manual administratively down down
    """
    interfaces = []
    lines = cli_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.lower().startswith("interface") or line.startswith("---"):
            continue
        parts = re.split(r"\s+", line)
        if len(parts) >= 6:
            # Interface, IP-Address, OK?, Method, Status, Protocol
            iface_name = parts[0]
            ip_addr = parts[1]
            status = parts[4]
            if "administratively" in line.lower():
                # Status is 'administratively down', protocol is 'down'
                admin_idx = parts.index("administratively") if "administratively" in parts else -1
                if admin_idx != -1 and len(parts) > admin_idx + 1:
                    status = "administratively down"
                    protocol = parts[admin_idx + 2] if len(parts) > admin_idx + 2 else "down"
                else:
                    status = "administratively down"
                    protocol = parts[-1]
            else:
                protocol = parts[5]
            
            interfaces.append({
                "interface": iface_name,
                "ip_address": ip_addr,
                "status": status.lower(),
                "protocol": protocol.lower()
            })
    return interfaces


def parse_show_interfaces_trunk(cli_text: str) -> List[Dict[str, Any]]:
    """
    Parses 'show interfaces trunk' text into structured trunk port records.
    """
    trunks = []
    lines = cli_text.strip().splitlines()
    
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "Port" in line and "Mode" in line and "Encapsulation" in line:
            current_section = "mode"
            continue
        elif "Port" in line and "Vlans allowed on trunk" in line:
            current_section = "allowed"
            continue
        
        parts = re.split(r"\s+", line)
        if current_section == "mode" and len(parts) >= 5:
            # Port, Mode, Encapsulation, Status, Native vlan
            trunks.append({
                "port": parts[0],
                "mode": parts[1],
                "encapsulation": parts[2],
                "status": parts[3],
                "native_vlan": int(parts[4]) if parts[4].isdigit() else parts[4],
                "allowed_vlans": []
            })
        elif current_section == "allowed" and len(parts) >= 2:
            port = parts[0]
            vlans_str = parts[1]
            # Parse ranges like 1-10,20,30
            parsed_vlans = _parse_vlan_list(vlans_str)
            for t in trunks:
                if t["port"] == port:
                    t["allowed_vlans"] = parsed_vlans
    return trunks


def _parse_vlan_list(vlan_str: str) -> List[int]:
    """Helper to parse VLAN strings like '1,10,20-22' into a list of integers."""
    result = []
    for item in vlan_str.split(","):
        item = item.strip()
        if "-" in item:
            start_end = item.split("-")
            if len(start_end) == 2 and start_end[0].isdigit() and start_end[1].isdigit():
                result.extend(range(int(start_end[0]), int(start_end[1]) + 1))
        elif item.isdigit():
            result.append(int(item))
    return sorted(list(set(result)))
