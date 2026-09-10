#set page(paper: "a4", margin: 1in)
#set text(font: "Linux Libertine", size: 11pt)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 16pt, weight: "bold")[NetSage AI: An AI-Assisted Network Troubleshooting Helper]
  
  #v(1em)
  *Cisco Virtual Internship Program 2026*   Problem Statement 2: AI Troubleshooting Helper with Human Review   Submission Track: Data Analytics & Applied AI   August 30, 2026
]

#v(2em)
= NetSage AI: An AI-Assisted Network Troubleshooting Helper with Deterministic Validation and Human Review

*Cisco Virtual Internship Program 2026*  
*Problem Statement 2: AI Troubleshooting Helper with Human Review*  
*Submission Track: Data Analytics & Applied AI*  
*Date of Submission:* August 30, 2026  

---

== Student & Project Metadata

#table(
  columns: 2,
  align: left,
  [*Attribute*], [*Project Details*],
  [*Project Title*], [NetSage AI: Hybrid Deterministic & Generative Network Troubleshooting Engine],
  [*Intern Name*], [Priyam Vidyarthi],
  [*Cisco NetAcad ID*], [`priyam.25scs1025004890@iilm.edu`],
  [*AICTE Student ID*], [STU68fe5745436201761498949],
  [*College / University*], [IILM University],
  [*Cohort*], [AI Track],
  [*Project Repository*], [`https://github.com/priyam-stdev/NetSage-AI-Cisco-Internship.git`],
)

---

== Executive Summary & Problem Statement

Modern enterprise and campus computer networks are mission-critical infrastructures governed by complex, multi-layered protocols spanning the OSI model. While entry-level and junior network engineers are frequently trained on individual Cisco IOS commands (`show ip interface brief`, `show interfaces trunk`, `show ip route`), they often encounter significant cognitive friction when diagnosing multifaceted network outages. A single user-facing symptom—such as a workstation being unable to reach an internal web server—can stem from a wide array of disparate root causes across different layers: an unassigned VLAN, an untrusted DHCP snooping port, an 802.1Q subinterface encapsulation mismatch, a misordered Access Control List (ACL), or a missing default route.

The core challenge is not a lack of diagnostic data, but the *semantic synthesis* required to correlate raw terminal outputs with protocol mechanics. Traditional deterministic scripts are fast and exact but rigid and incapable of interpreting free-form symptoms or generating step-by-step remediation plans. Conversely, pure generative AI models (LLMs) excel at natural-language reasoning and code generation, but are prone to hallucinating non-existent interfaces, misinterpreting subnet masks, or proposing dangerous commands without contextual verification.

*NetSage AI* addresses this challenge by introducing a *hybrid, human-in-the-loop diagnostic architecture*. The system combines:
1. A *Deterministic Python Rule Checker* that rigorously evaluates hard constraints (duplicate IPs, subnet boundary violations, gateway mismatches, administrative link states, trunk pruning, recursive route failures, and ACL shadowing).
2. A *Structured Generative AI Diagnostic Engine* that ingests raw Cisco CLI show commands and rule flags to produce structured, evidence-backed JSON diagnoses with calibrated confidence ratings and remediation steps.
3. A *Mandatory Human-in-the-Loop Review Workflow* ensuring that no configuration change is deployed to network infrastructure without explicit verification and approval by a qualified engineer.

---

== System Architecture & Diagnostic Pipeline

The NetSage AI workflow follows a structured six-stage pipeline designed to ensure safety, traceability, and high diagnostic accuracy:

```mermaid
flowchart TD
    A["Incident Reported<br/>(Symptom + Topology Notes)"] --> B["Cisco IOS Show Commands<br/>(CLI Output Capture)"]
    B --> C["Deterministic Python Rule Checker<br/>(Hard-Constraint Validation)"]
    B --> D["AI Prompt Formatter<br/>(Context + Evidence Injection)"]
    C --> D
    D --> E["NetSage AI Engine<br/>(Structured JSON Diagnosis)"]
    E --> F{"Human Reviewer Gate<br/>(Accepted / Edited / Rejected)"}
    F -- "Rejected / Re-evaluate" --> D
    F -- "Edited / Corrected" --> G["Remediation Execution<br/>(Cisco Packet Tracer / CLI)"]
    F -- "Accepted" --> G
    G --> H["Post-Remediation Verification<br/>(Ping / Traceroute / Show State)"]
    H --> I["Responsible AI Audit Log & Dashboard<br/>(Telemetry & Performance Tracking)"]
```

=== Architectural Stages:
1. *Symptom Ingestion:* The engineer documents the observable network failure (e.g., "PC cannot obtain DHCP address", "OSPF adjacency stuck in EXSTART").
2. *Deterministic Pre-Check:* The Python Rule Checker parses network state parameters and flags any objective RFC/IOS violations (e.g. duplicate IP `192.168.10.50` on two hosts, native VLAN mismatch).
3. *Structured Context Injection:* Raw CLI outputs and deterministic rule flags are assembled into a structured prompt template.
4. *Generative Diagnosis:* The AI reasoning model outputs a strict JSON payload categorizing the root cause, OSI layer, confidence score, CLI evidence, next command, and step-by-step fix.
5. *Human Engineering Gate:* The human reviewer evaluates the AI diagnosis against ground truth, assigning a formal status (*ACCEPTED*, *EDITED*, or *REJECTED*).
6. *Remediation & Post-Verification:* Remediation commands are executed in Cisco Packet Tracer, followed by verification pings and routing table validation.

---

== Case Dataset & Ground-Truth Reference Library

To ensure real-world validity without inventing fictitious outputs, NetSage AI's training and evaluation benchmark is designed to reflect *34 realistic, well-documented CCNA-style network fault patterns* based on standard Cisco IOS technical concepts.

Each case has been rewritten into an original format, categorized by OSI Layer, tagged by concept, and assigned an objective severity level.

=== Dataset Schema

#table(
  columns: 3,
  align: left,
  [*Field*], [*Description*], [*Example*],
  [`case_id`], [Unique incident identifier], [`CASE-004`],
  [`symptom`], [User-reported outage description], [Inter-VLAN routing fails between Sales and Marketing],
  [`topology_note`], [Physical and logical layout], [R1 Gi0/0.10 (VLAN 10) & Gi0/0.20 (VLAN 20) to S1 Gi0/1],
  [`show_output_evidence`], [Concrete CLI terminal snippet], [`R1# show running-config interface Gi0/0.10` -> `encapsulation dot1Q 20`],
  [`expected_fault`], [Verified ground-truth root cause], [Subinterface Gi0/0.10 configured with incorrect 802.1Q tag 20],
  [`osi_layer`], [Primary OSI Model layer], [Network (Layer 3)],
  [`concept_tag`], [Topic domain], [`Router_On_A_Stick`],
  [`severity`], [Outage criticality (`Critical`, `High`, `Medium`, `Low`)], [`Critical`],
  [`reference_source_note`], [Source traceability], [Adapted from NetAcad CCNA SRWE Lab 3.4.5],
)

=== Dataset Summary Distribution

```
+-------------------------------------------------------------------------------+
#table(
  columns: 4,
  align: left,
  [*Domain Category*], [*Case Count*], [*Primary OSI Layers*], [*Severity Range*],
)
+-------------------------------------------------------------------------------+
#table(
  columns: 4,
  align: left,
  [*VLAN & 802.1Q Trunking*], [*4*], [*Layer 2, Layer 3*], [*Medium - High*],
  [Default Gateway & HSRP (FHRP)], [4], [Layer 3], [Medium - Crit],
  [DHCP & Dynamic Addressing], [4], [Layer 2, 3, 7], [High - Crit],
  [DNS & Application Services], [3], [Layer 4, Layer 7], [Medium - High],
  [Static & OSPF Routing], [6], [Layer 3], [High - Crit],
  [Access Control Lists (ACL)], [4], [Layer 3, Layer 4], [Medium - Crit],
  [NAT & PAT], [4], [Layer 3], [High - Crit],
  [Wireless LAN (WLC / AP)], [2], [Layer 2], [High],
  [LAN Security & Spanning Tree], [2], [Layer 2], [High - Crit],
  [Subnetting & IP Boundaries], [1], [Layer 3], [Medium],
  [Total Curated Cases], [34], [Layers 2 - 7], [CCNA Concepts],
)
+-------------------------------------------------------------------------------+
```

---

== Deterministic Python Rule Checker

=== Design Rationale

While generative AI models possess advanced natural language comprehension, they cannot replace deterministic mathematical and logical verification in networking. The NetSage Python Rule Checker operates as an automated pre-flight and post-flight validation engine implementing seven deterministic checks:

1. *Duplicate IP Detection (`RULE-001`):* Traverses all router interfaces, switch SVIs, and host configurations to identify duplicate IPv4 assignments that would cause ARP poisoning or flapping.
2. *Subnet Mask & Broadcast Range Verification (`RULE-002`):* Validates using Python's standard `ipaddress` library that no endpoint is assigned a Subnet Network Address (e.g. `192.168.1.0/24`) or Broadcast Address (e.g. `192.168.1.255/24`).
3. *Default Gateway Consistency (`RULE-003`):* Ensures host default gateways are strictly within the local host's subnet boundaries and match an active Layer 3 router interface.
4. *Interface Operational States (`RULE-004`):* Flags any interface in an `administratively down` or `down/down` state on active communication paths.
5. *VLAN & Trunk Configuration Consistency (`RULE-005`):* Identifies access ports mapped to uncreated VLANs, native VLAN mismatches across switch uplinks, and trunk allowed list discrepancies.
6. *Routing Reachability & Recursive Next-Hops (`RULE-006`):* Detects static routes whose next-hop IP is not directly reachable on any active local interface subnet.
7. *Access Control List Shadowing (`RULE-007`):* Analyzes ACL statement sequences to flag permit statements shadowed by preceding broad deny rules.

=== Rule Checker Execution Proof

Below is the verified terminal output of the NetSage Rule Checker running in demonstration mode on `data/sample_network_state.json`:

```text
================================================================================
 [NetSage AI Rule Checker] Rule Violations Detected: 10
================================================================================

1. [CRITICAL] Rule ID: RULE-001 | Category: IP_Addressing
   Device(s)     : Host:PC-Sales-1, Host:PC-Sales-2
   Target/Entity : 192.168.10.50
   Violation     : Duplicate IP address detected: '192.168.10.50' is assigned to multiple endpoints: Host:PC-Sales-1, Host:PC-Sales-2.
   Remediation   : Reassign unique IP addresses to avoid Layer 3 ARP collisions.
   ---------------------------------------------------------------------------

2. [CRITICAL] Rule ID: RULE-002B | Category: IP_Addressing
   Device(s)     : PC-Test-Broadcast
   Target/Entity : 192.168.20.255
   Violation     : Host 'PC-Test-Broadcast' IP '192.168.20.255' is the Subnet Broadcast Address for 192.168.20.0/24.
   Remediation   : Assign a usable host IP within range 192.168.20.1 - 192.168.20.254.
   ---------------------------------------------------------------------------

3. [CRITICAL] Rule ID: RULE-003A | Category: Gateway
   Device(s)     : PC-Marketing-1
   Target/Entity : 192.168.99.254
   Violation     : Host 'PC-Marketing-1' gateway '192.168.99.254' is outside local subnet 192.168.20.0/24.
   Remediation   : Configure default gateway within subnet 192.168.20.0/24.
   ---------------------------------------------------------------------------

4. [HIGH]     Rule ID: RULE-003B | Category: Gateway
   Device(s)     : PC-Marketing-1
   Target/Entity : 192.168.99.254
   Violation     : Host 'PC-Marketing-1' default gateway '192.168.99.254' does not match any configured router interface IP.
   Remediation   : Update gateway to point to valid active router interface IP.
   ---------------------------------------------------------------------------

5. [HIGH]     Rule ID: RULE-004A | Category: Interface_Status
   Device(s)     : R1-Edge
   Target/Entity : GigabitEthernet0/1
   Violation     : Interface 'GigabitEthernet0/1' on 'R1-Edge' is administratively down (shutdown).
   Remediation   : Enter interface configuration mode and execute 'no shutdown'.
   ---------------------------------------------------------------------------

6. [HIGH]     Rule ID: RULE-005A | Category: VLAN
   Device(s)     : SW-Core1
   Target/Entity : FastEthernet0/3
   Violation     : Access port 'FastEthernet0/3' is assigned to non-existent VLAN 50.
   Remediation   : Create 'vlan 50' in global configuration mode on 'SW-Core1'.
   ---------------------------------------------------------------------------

7. [MEDIUM]   Rule ID: RULE-005B | Category: VLAN_Trunking
   Device(s)     : SW-Core1 <-> SW-Access2
   Target/Entity : GigabitEthernet0/1 <-> GigabitEthernet0/1
   Violation     : Native VLAN mismatch on trunk link: SW-Core1 (GigabitEthernet0/1) uses VLAN 99, while SW-Access2 (GigabitEthernet0/1) uses VLAN 1.
   Remediation   : Configure matching native VLAN with 'switchport trunk native vlan \<id\>' on both trunk ends.
   ---------------------------------------------------------------------------

8. [HIGH]     Rule ID: RULE-005C | Category: VLAN_Trunking
   Device(s)     : SW-Core1 <-> SW-Access2
   Target/Entity : GigabitEthernet0/1 <-> GigabitEthernet0/1
   Violation     : Trunk allowed VLAN mismatch between SW-Core1 and SW-Access2. Discrepant VLANs: [99].
   Remediation   : Ensure consistent 'switchport trunk allowed vlan' lists on both ends of the trunk.
   ---------------------------------------------------------------------------

9. [CRITICAL] Rule ID: RULE-006A | Category: Routing
   Device(s)     : R1-Edge
   Target/Entity : ip route 10.50.0.0/16 172.16.99.1
   Violation     : Static route next-hop '172.16.99.1' is unreachable via any directly connected active interface on 'R1-Edge' (recursive lookup failure).
   Remediation   : Correct next-hop IP address to match directly connected neighbor subnet.
   ---------------------------------------------------------------------------

10. [CRITICAL] Rule ID: RULE-007A | Category: ACL
   Device(s)     : R1-Edge
   Target/Entity : ACL:ACL_INBOUND_FILTER:Seq_2
   Violation     : Shadowed ACL rule detected in 'ACL_INBOUND_FILTER': Permit statement at sequence 2 appears AFTER a broad 'deny any any' statement and will never be evaluated.
   Remediation   : Reorder ACL statements using sequence numbers so specific permit entries precede broad deny rules.
   ---------------------------------------------------------------------------
================================================================================
```

---

== AI Prompt Library & Diagnosis Schema

The prompt library enforces structured reasoning through role specification, format constraints, few-shot examples, and strict JSON output schemas.

=== Diagnosis Prompt Schema

```json
{
  "root_cause": "<Precise description of the fault>",
  "osi_layer": "<Data Link (Layer 2) | Network (Layer 3) | Transport (Layer 4) | Application (Layer 7)>",
  "concept_tag": "<Domain concept identifier>",
  "confidence": "<High | Medium | Low>",
  "evidence": [
    "<Primary CLI output line citation>",
    "<Secondary rule checker finding>"
  ],
  "next_command": "<Cisco IOS verification command>",
  "fix_steps": [
    "configure terminal",
    "<remediation command 1>",
    "<remediation command 2>",
    "end"
  ]
}
```

---

== Responsible AI Log: Human-in-the-Loop Oversight & Corrections

Human oversight is a mandatory, graded requirement of this project. All 34 curated cases were personally reviewed by the intern by comparing the AI's diagnosis against the documented, ground-truth root cause for each case.

*Evaluation summary:* All 34 cases were reviewed. 31 diagnoses were accepted as matching the documented root cause (in some cases using different wording for the same finding). 3 diagnoses were rejected: CASE-008 (HSRP — AI asserted preempt was already enabled and proposed unverified alternative causes not supported by the evidence), CASE-024 (ACL wildcard mask — AI diagnosed an unrelated NAT-ordering issue instead), and CASE-033 (Spanning Tree — AI diagnosed missing guard features rather than STP being disabled).

== Full Incident Review Audit Table

#table(
  columns: 4,
  align: left,
  [*Case ID*], [*Concept*], [*Verdict*], [*Reviewer Note*],
  [CASE-001], [VLAN_Trunking], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-002], [VLAN_Trunking], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-003], [VLAN_Access], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-004], [Router_On_A_Stick], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-005], [Default_Gateway], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-006], [Default_Gateway], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-007], [FHRP_HSRP], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-008], [FHRP_HSRP], [*REJECTED*], [Documented cause is a missing HSRP preempt setting. AI asserted preempt was already enabled and instead proposed unverified alternative causes (ACL blocking HSRP hellos, an unexpired preempt delay timer) not supported by the case evidence.],
  [CASE-009], [DHCP], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-010], [DHCP], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-011], [DHCP_IP_Conflict], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-012], [DHCP_Snooping], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-013], [DNS], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-014], [DNS_ACL], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-015], [DNS_Config], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-016], [Static_Routing], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-017], [Static_Routing], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-018], [OSPF_Adjacency], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-019], [OSPF_Adjacency], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-020], [OSPF_Routing], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-021], [OSPF_Adjacency], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-022], [ACL_Extended], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-023], [ACL_Standard_VTY], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-024], [ACL_Wildcard_Mask], [*REJECTED*], [Documented cause is an inverted ACL wildcard mask. AI diagnosed an unrelated NAT-ordering conflict and never identified the wildcard mask error.],
  [CASE-025], [ACL_Direction], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-026], [NAT_PAT], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-027], [NAT_PAT], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-028], [NAT_Interfaces], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-029], [NAT_Static], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-030], [Wireless_WLC], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-031], [Wireless_VLAN], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-032], [Port_Security], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
  [CASE-033], [Spanning_Tree], [*REJECTED*], [Documented cause is STP disabled globally. AI diagnosed missing loop-protection features (BPDU/Loop Guard) instead — a different, more specific misconfiguration that would lead to the wrong fix.],
  [CASE-034], [IP_Subnetting], [*ACCEPTED*], [AI's diagnosis matches the documented root cause (different wording, same substance).],
)

= Performance & Evaluation Dashboard

*Evaluation metrics summary:* Of the 34 cases actually reviewed by the intern, NetSage AI's diagnosis was accepted as correct for 31 cases (91.2% first-pass accuracy). 0 case(s) required editing. 3 cases were rejected as misdiagnoses.

== Diagnosis Accuracy by Domain

#table(
  columns: 6,
  align: left,
  [*Category*], [*Tested*], [*Accepted*], [*Edited*], [*Rejected*], [*Accuracy (%)*],
  [VLAN & 802.1Q Trunking], [4], [4], [0], [0], [100.0%],
  [Default Gateway & HSRP], [4], [3], [0], [1], [75.0%],
  [DHCP & Dynamic Addressing], [4], [4], [0], [0], [100.0%],
  [DNS & Application Services], [3], [3], [0], [0], [100.0%],
  [Static & OSPF Routing], [6], [6], [0], [0], [100.0%],
  [Access Control Lists (ACL)], [4], [3], [0], [1], [75.0%],
  [NAT & PAT], [4], [4], [0], [0], [100.0%],
  [Wireless LAN (WLC / AP)], [2], [2], [0], [0], [100.0%],
  [LAN Security & Spanning Tree], [2], [1], [0], [1], [50.0%],
  [Subnetting & IP Boundaries], [1], [1], [0], [0], [100.0%],
  [*Total / Overall*], [*34*], [*31*], [*0*], [*3*], [*91.2%*],
)

== Human Review Agreement Breakdown

- Accepted (Direct Approval): 31 cases (91.2%)
- Edited (Refined / Fixed): 0 cases (0.0%)
- Rejected (Misdiagnosis): 3 cases (8.8%)
- Total cases reviewed: 34 of 34 curated cases (100% of dataset)


