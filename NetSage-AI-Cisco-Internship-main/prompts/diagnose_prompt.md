# NetSage AI: Structured Diagnosis Prompt Template

This prompt is submitted to the AI model alongside the system prompt to generate a deterministic, evidence-backed network diagnosis.

---

## User Prompt Template

```markdown
Analyze the following network incident and determine the root cause, OSI layer, confidence level, supporting CLI evidence, next diagnostic command, and step-by-step Cisco IOS remediation steps.

Respond STRICTLY with a valid JSON object matching the required schema.

### 1. Incident Symptom
{{SYMPTOM}}

### 2. Topology Context & Host Notes
{{TOPOLOGY_NOTE}}

### 3. Captured Cisco IOS Show Commands
```text
{{SHOW_OUTPUTS}}
```

### 4. Deterministic Rule Checker Flags
```text
{{RULE_CHECKER_FLAGS}}
```
```

---

## Worked Examples (Illustrative Templates)

> [!NOTE]
> The following 3 examples are **illustrative reference templates** demonstrating how NetSage AI translates captured show outputs into structured JSON diagnoses. These are examples for prompt development and evaluation testing.

---

### Worked Example 1: Inter-VLAN Subinterface Encapsulation Mismatch (CASE-004)

#### Input Prompt:
```markdown
### 1. Incident Symptom
Router-on-a-Stick inter-VLAN routing fails between Sales PC1 (192.168.10.10) and Marketing PC2 (192.168.20.10).

### 2. Topology Context & Host Notes
Router R1 Gi0/0 connects to Switch S1 Gi0/1 (Trunk). Subinterfaces Gi0/0.10 (IP 192.168.10.1) and Gi0/0.20 (IP 192.168.20.1) are configured for VLAN 10 and VLAN 20 respectively.

### 3. Captured Cisco IOS Show Commands
```text
R1# show running-config interface Gi0/0.10
interface GigabitEthernet0/0.10
 encapsulation dot1Q 20
 ip address 192.168.10.1 255.255.255.0
!
R1# show running-config interface Gi0/0.20
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
```

### 4. Deterministic Rule Checker Flags
```text
[HIGH] VLAN encapsulation collision: Subinterface Gi0/0.10 and Gi0/0.20 both declare 802.1Q tag 20.
```
```

#### NetSage AI Output:
```json
{
  "root_cause": "Subinterface GigabitEthernet0/0.10 is incorrectly configured with 802.1Q VLAN encapsulation tag 20 instead of tag 10, preventing R1 from processing untagged/tagged frames originating from Sales VLAN 10.",
  "osi_layer": "Data Link (Layer 2)",
  "concept_tag": "VLAN_Trunking",
  "confidence": "High",
  "evidence": [
    "R1 running-config shows 'encapsulation dot1Q 20' under interface GigabitEthernet0/0.10 with IP 192.168.10.1",
    "Duplicate dot1Q tag 20 exists on both Gi0/0.10 and Gi0/0.20 subinterfaces"
  ],
  "next_command": "show ip interface brief | include GigabitEthernet0/0",
  "fix_steps": [
    "configure terminal",
    "interface GigabitEthernet0/0.10",
    "encapsulation dot1Q 10",
    "ip address 192.168.10.1 255.255.255.0",
    "no shutdown",
    "end",
    "write memory"
  ],
  "rule_checker_alignment": "Confirms rule checker finding regarding duplicate 802.1Q encapsulation tag 20 across subinterfaces."
}
```

---

### Worked Example 2: Missing DHCP Relay Agent / IP Helper-Address (CASE-009)

#### Input Prompt:
```markdown
### 1. Incident Symptom
Clients in Branch Office LAN on VLAN 10 receive APIPA autoconfiguration IP address (169.254.45.12) and cannot reach corporate network.

### 2. Topology Context & Host Notes
Clients connect to Switch S1 on VLAN 10. Default gateway is Router R1 Gi0/0.10 (192.168.10.1). Central DHCP Server is located at HQ across WAN at IP 10.1.100.10.

### 3. Captured Cisco IOS Show Commands
```text
PC1> ipconfig /all
   Autoconfiguration IPv4 Address. : 169.254.45.12
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . : 

R1# show running-config interface Gi0/0.10
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
```

### 4. Deterministic Rule Checker Flags
```text
[MEDIUM] No local DHCP pool found on R1; no 'ip helper-address' configured on subinterface Gi0/0.10.
```
```

#### NetSage AI Output:
```json
{
  "root_cause": "The client-facing router subinterface GigabitEthernet0/0.10 lacks the 'ip helper-address' command. As DHCP DISCOVER broadcasts (255.255.255.255) cannot traverse routers by default, requests are dropped before reaching the central DHCP server (10.1.100.10).",
  "osi_layer": "Application (Layer 7)",
  "concept_tag": "DHCP",
  "confidence": "High",
  "evidence": [
    "PC1 receives 169.254.45.12 indicating failure of DORA transaction",
    "R1 'show running-config interface Gi0/0.10' contains no 'ip helper-address' statement"
  ],
  "next_command": "show ip dhcp binding (on central server) or debug ip packet (on R1)",
  "fix_steps": [
    "configure terminal",
    "interface GigabitEthernet0/0.10",
    "ip helper-address 10.1.100.10",
    "end",
    "write memory"
  ],
  "rule_checker_alignment": "Matches deterministic checker flag identifying absent DHCP relay mechanism on the broadcast domain boundary."
}
```

---

### Worked Example 3: OSPF Neighbor Adjacency MTU Mismatch (CASE-018)

#### Input Prompt:
```markdown
### 1. Incident Symptom
OSPF routing adjacency between Router R1 and Router R2 fails to achieve FULL state; stuck in EXSTART/EXCHANGE.

### 2. Topology Context & Host Notes
R1 Gi0/0 (10.1.1.1/30) directly connects to R2 Gi0/0 (10.1.1.2/30) in OSPF Area 0.

### 3. Captured Cisco IOS Show Commands
```text
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   EXSTART/DROTHER 00:00:33    10.1.1.2        GigabitEthernet0/0

R1# show interfaces Gi0/0 | include MTU
  MTU 1500 bytes, BW 1000000 Kbit/sec

R2# show interfaces Gi0/0 | include MTU
  MTU 1400 bytes, BW 1000000 Kbit/sec
```

### 4. Deterministic Rule Checker Flags
```text
[HIGH] Interface MTU discrepancy detected across point-to-point link: R1 Gi0/0 (1500) vs R2 Gi0/0 (1400).
```
```

#### NetSage AI Output:
```json
{
  "root_cause": "Interface MTU mismatch between R1 (1500 bytes) and R2 (1400 bytes). During OSPF adjacency formation, Database Description (DBD) packets with differing MTUs cause the neighbor state machine to become stuck in EXSTART/EXCHANGE.",
  "osi_layer": "Network (Layer 3)",
  "concept_tag": "OSPF_Adjacency",
  "confidence": "High",
  "evidence": [
    "R1 'show ip ospf neighbor' indicates neighbor 2.2.2.2 is stuck in EXSTART/DROTHER",
    "R1 Gi0/0 MTU is 1500 bytes whereas R2 Gi0/0 MTU is 1400 bytes"
  ],
  "next_command": "show ip ospf neighbor",
  "fix_steps": [
    "configure terminal",
    "interface GigabitEthernet0/0",
    "ip mtu 1500",
    "end",
    "clear ip ospf process"
  ],
  "rule_checker_alignment": "Aligns with MTU discrepancy flag detected across the link."
}
```
