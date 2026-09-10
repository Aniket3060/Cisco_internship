# NetSage AI: Curated Troubleshooting Case Dataset (34 Cases)

This dataset compiles 34 real-world, grounded Cisco lab troubleshooting scenarios derived from official **Cisco Networking Academy (CCNA v7: ITN, SRWE, ENSA)** lab activities, Cisco Command References, and standard network engineering fault patterns.

---

## Dataset Schema Definition

| Field | Type | Description |
| :--- | :--- | :--- |
| `case_id` | String | Unique identifier (`CASE-001` through `CASE-034`) |
| `symptom` | String | User/client-reported network symptom |
| `topology_note` | String | Summary of relevant hosts, switches, routers, interfaces, and subnets |
| `show_output_evidence`| String | Concrete CLI outputs (`show ip interface brief`, `show running-config`, etc.) |
| `expected_fault` | String | Ground-truth root cause of the network outage |
| `osi_layer` | String | OSI Layer classification (Layer 2 Data Link, Layer 3 Network, Layer 4 Transport, Layer 7 Application) |
| `concept_tag` | String | Topic category (VLAN, Gateway, DHCP, DNS, OSPF, ACL, NAT, Wireless, Security, STP) |
| `severity` | String | Impact level (`Critical`, `High`, `Medium`, `Low`) |
| `reference_source_note`| String | Traceable citation to Cisco NetAcad / IOS documentation |

---

## Category Distribution Summary

```
+-------------------------------------------------------------+
| Domain                       | Case Count | OSI Layers      |
+-------------------------------------------------------------+
| VLAN & Trunking              | 4          | Layer 2, Layer 3|
| Default Gateway & FHRP (HSRP)| 4          | Layer 3         |
| DHCP & IP Addressing         | 4          | Layer 2, 3, 7   |
| DNS & Application Services   | 3          | Layer 4, Layer 7|
| Routing (Static & OSPF)      | 6          | Layer 3         |
| Access Control Lists (ACL)   | 4          | Layer 3, Layer 4|
| NAT & PAT                    | 4          | Layer 3         |
| Wireless LAN (WLC/AP)        | 2          | Layer 2         |
| Switch Security & STP        | 2          | Layer 2         |
| IP Subnetting                | 1          | Layer 3         |
| Total Curated Cases          | 34         | Layers 2 - 7    |
+-------------------------------------------------------------+
```

---

## Detailed Case Breakdown

### 1. VLAN & Trunking (Layer 2 / 3)

#### CASE-001: Missing VLAN on Trunk Allowed List
- **Symptom**: PC1 cannot ping PC2 in the same VLAN across Switch-1 and Switch-2.
- **Topology**: PC1 (192.168.10.10/24) on S1 Fa0/1 (VLAN 10). PC2 (192.168.10.20/24) on S2 Fa0/1 (VLAN 10). Trunk link between S1 Gi0/1 and S2 Gi0/1.
- **CLI Evidence**:
  ```text
  S1# show interfaces trunk
  Port        Mode         Encapsulation  Status        Native vlan
  Gi0/1       on           802.1q         trunking      1
  Port        Vlans allowed on trunk
  Gi0/1       10,20

  S2# show interfaces trunk
  Port        Mode         Encapsulation  Status        Native vlan
  Gi0/1       on           802.1q         trunking      1
  Port        Vlans allowed on trunk
  Gi0/1       20,30
  ```
- **Root Cause**: VLAN 10 is missing from the allowed trunk list on Switch-2 (`switchport trunk allowed vlan 20,30`).
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: NetAcad CCNA SRWE Lab 2.2.13 (*Troubleshoot VLANs and Trunks*).

#### CASE-002: Native VLAN Mismatch on Inter-Switch Trunk
- **Symptom**: Native VLAN mismatch error in Syslog; traffic between VLAN 1 and native untagged VLAN leaking.
- **Topology**: S1 Gi0/1 connects to S2 Gi0/1. S1 native VLAN configured as 99; S2 native VLAN remains default 1.
- **CLI Evidence**:
  ```text
  %CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (99), with S2 GigabitEthernet0/1 (1).
  S1# show interfaces Gi0/1 switchport | include Trunking Native Mode
  Trunking Native Mode VLAN: 99 (Management)
  S2# show interfaces Gi0/1 switchport | include Trunking Native Mode
  Trunking Native Mode VLAN: 1 (default)
  ```
- **Root Cause**: Native VLAN mismatch across 802.1Q trunk interfaces causing unencapsulated frame bleed.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: Medium
- **Reference**: Cisco IOS Switching Command Reference & NetAcad SRWE Lab 2.2.13.

#### CASE-003: Access Port Assigned to Incorrect VLAN
- **Symptom**: PC in Accounting department cannot communicate with local gateway or file server.
- **Topology**: PC3 (192.168.30.15/24) connected to S1 Fa0/5. Accounting subnet is VLAN 30.
- **CLI Evidence**:
  ```text
  S1# show vlan brief
  VLAN Name                             Status    Ports
  ---- -------------------------------- --------- -------------------------------
  1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4, Fa0/5
  30   Accounting                       active    Fa0/10, Fa0/11, Fa0/12
  ```
- **Root Cause**: Access port Fa0/5 is assigned to default VLAN 1 instead of VLAN 30.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: CCNA ITN Lab 10.4.3 & SRWE Lab 2.1.4.

#### CASE-004: Router-on-a-Stick 802.1Q Subinterface Tag Mismatch
- **Symptom**: Inter-VLAN routing fails between Sales (VLAN 10) and Marketing (VLAN 20).
- **Topology**: Router R1 Gi0/0.10 and Gi0/0.20 subinterfaces connect to Switch S1 Gi0/1 (Trunk).
- **CLI Evidence**:
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
- **Root Cause**: Subinterface `Gi0/0.10` has mismatched encapsulation tag `dot1Q 20` instead of `dot1Q 10`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad SRWE Lab 3.4.5 (*Troubleshoot Inter-VLAN Routing*).

---

### 2. Default Gateway & First-Hop Redundancy (Layer 3)

#### CASE-005: Default Gateway Interface Administratively Down
- **Symptom**: Host PC cannot ping default gateway; local ARP table shows incomplete for gateway IP.
- **Topology**: PC1 IP 192.168.1.50/24, configured gateway 192.168.1.1. Router R1 interface Gi0/0.
- **CLI Evidence**:
  ```text
  C:\> arp -a
  Internet Address      Physical Address      Type
  192.168.1.1           incomplete            dynamic

  R1# show ip interface brief
  Interface              IP-Address      OK? Method Status                Protocol
  GigabitEthernet0/0     192.168.1.1     YES manual administratively down down
  ```
- **Root Cause**: Gateway interface `Gi0/0` is shut down (missing `no shutdown`).
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad ITN Lab 17.7.6 (*Troubleshoot Connectivity Issues*).

#### CASE-006: Host Workstation Configured with Wrong Gateway IP
- **Symptom**: Workstation cannot communicate outside local subnet; can ping neighbors on same switch.
- **Topology**: PC-A: IP 172.16.10.25, Mask 255.255.255.0, Gateway 172.16.10.254. Router Gateway IP is 172.16.10.1.
- **CLI Evidence**:
  ```text
  PC-A> ipconfig /all
     IPv4 Address. . . . . . . . . . . : 172.16.10.25
     Subnet Mask . . . . . . . . . . . : 255.255.255.0
     Default Gateway . . . . . . . . . : 172.16.10.254

  R1# show ip interface brief
  GigabitEthernet0/0/0   172.16.10.1     YES manual up                    up
  ```
- **Root Cause**: Host default gateway setting points to nonexistent IP `172.16.10.254`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ITN Lab 11.5.5 (*Subnetting & Host Gateway Troubleshooting*).

#### CASE-007: HSRP Group Number Mismatch Causing Split-Brain Active/Active
- **Symptom**: HSRP active/standby state flaps; dual active routers claiming virtual IP 192.168.1.254.
- **Topology**: R1 (Gi0/1: 192.168.1.2) and R2 (Gi0/1: 192.168.1.3). HSRP Group 1 Virtual IP 192.168.1.254.
- **CLI Evidence**:
  ```text
  R1# show standby brief
  P Indic.   Grp  Pri P State   Active          Standby         Virtual IP
  Gi0/1      1    110 P Active  local           unknown         192.168.1.254

  R2# show standby brief
  P Indic.   Grp  Pri P State   Active          Standby         Virtual IP
  Gi0/1      2    100 P Active  local           unknown         192.168.1.254
  ```
- **Root Cause**: R1 configured with `standby 1 ip ...` while R2 configured with `standby 2 ip ...`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 9.2.9 (*Troubleshoot HSRP*).

#### CASE-008: Missing Preempt on Primary HSRP Router
- **Symptom**: Primary HSRP router fails to resume active role after reboot.
- **Topology**: R1 priority 110 (no preempt); R2 priority 100. R2 took active role while R1 was down.
- **CLI Evidence**:
  ```text
  R1# show standby brief
  P Indic.   Grp  Pri P State   Active          Standby         Virtual IP
  Gi0/1      1    110   Standby 192.168.1.3     local           192.168.1.254
  ```
- **Root Cause**: Missing `standby 1 preempt` on R1 prevents it from reclaiming the active state.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Medium
- **Reference**: Cisco IOS FHRP Configuration Guide.

---

### 3. DHCP & IP Addressing (Layer 2 / 3 / 7)

#### CASE-009: Missing IP Helper-Address on Multi-Subnet Router
- **Symptom**: Clients in Branch LAN receive APIPA address (169.254.x.x) instead of corporate DHCP scope.
- **Topology**: Clients on VLAN 10. Central DHCP server on 10.1.100.10 connected via Router R1 Gi0/0.
- **CLI Evidence**:
  ```text
  PC1> ipconfig
     Autoconfiguration IPv4 Address. : 169.254.45.12
     Subnet Mask . . . . . . . . . . . : 255.255.0.0

  R1# show running-config interface Gi0/0.10
  interface GigabitEthernet0/0.10
   encapsulation dot1Q 10
   ip address 192.168.10.1 255.255.255.0
   ! (Missing ip helper-address 10.1.100.10)
  ```
- **Root Cause**: Router does not relay DHCP broadcast discovery packets across subnets due to missing `ip helper-address`.
- **OSI Layer**: Layer 7 (Application) / Layer 3 (Relay) | **Severity**: Critical
- **Reference**: NetAcad SRWE Lab 7.4.2 (*Troubleshoot DHCPv4*).

#### CASE-010: DHCP Pool Scope Address Starvation via Over-exclusion
- **Symptom**: New devices cannot obtain DHCP lease; existing devices with active leases work normally.
- **Topology**: Router R1 acts as local DHCP server for pool 192.168.20.0/24.
- **CLI Evidence**:
  ```text
  R1# show ip dhcp pool LAN-POOL
  Pool LAN-POOL :
   Total addresses       : 5
   Leased addresses      : 5
   Excluded addresses    : 249
   Pending addresses     : 0

  R1# show running-config | include excluded-address
  ip dhcp excluded-address 192.168.20.6 192.168.20.254
  ```
- **Root Cause**: Accidental exclusion range `192.168.20.6 192.168.20.254` leaves only 5 addresses.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 7.2.7 (*Implement DHCPv4 on IOS*).

#### CASE-011: Static IP Address Overlap with Dynamic DHCP Pool
- **Symptom**: Client obtains DHCP address but receives IP conflict error pop-up; connectivity drops.
- **Topology**: PC1 receives 192.168.1.100 via DHCP. Network printer PR1 configured statically with 192.168.1.100.
- **CLI Evidence**:
  ```text
  R1# show ip dhcp conflict
  IP address        Detection method   Detection time
  192.168.1.100     Ping               Aug 27 2026 09:14 AM
  ```
- **Root Cause**: Static IP on printer was not excluded from IOS DHCP pool with `ip dhcp excluded-address`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: Cisco IOS IP Addressing Services Command Reference.

#### CASE-012: DHCP Snooping Dropping Offers on Untrusted Trunk Port
- **Symptom**: DHCP Offer packets dropped after enabling switch security; clients cannot obtain IP.
- **Topology**: Clients on S1 access ports. S1 connects to DHCP server via trunk port Gi0/1. DHCP snooping enabled.
- **CLI Evidence**:
  ```text
  S1# show ip dhcp snooping
  Switch DHCP snooping is enabled
  DHCP snooping is configured on following VLANs: 10

  S1# show ip dhcp snooping | section Gi0/1
  Interface                   Trusted    Rate limit (pps)
  -----------------------     -------    ----------------
  GigabitEthernet0/1          no         unlimited
  ```
- **Root Cause**: Uplink interface Gi0/1 facing the DHCP server is not configured with `ip dhcp snooping trust`.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 10.4.3 (*Troubleshoot LAN Security*).

---

### 4. DNS & Application Services (Layer 4 / 7)

#### CASE-013: Incorrect DNS Server IP Assigned to Host
- **Symptom**: Workstations can ping external IP (8.8.8.8) but cannot browse websites using domain names.
- **Topology**: Host PC configured with static IP 192.168.1.20/24, Gateway 192.168.1.1, DNS 192.168.1.250.
- **CLI Evidence**:
  ```text
  PC> ping 8.8.8.8
  Reply from 8.8.8.8: bytes=32 time=14ms TTL=118

  PC> nslookup cisco.com
  DNS request timed out.
      timeout was 2 seconds.
  *** Can't find server name for address 192.168.1.250: Timed out
  ```
- **Root Cause**: Host workstation configured with non-operational DNS server IP `192.168.1.250` (correct is `192.168.1.2`).
- **OSI Layer**: Layer 7 (Application) | **Severity**: High
- **Reference**: NetAcad ITN Lab 17.8.3 (*Troubleshooting Challenge*).

#### CASE-014: Firewall ACL Permitting TCP DNS but Blocking UDP Port 53
- **Symptom**: Internal DNS queries fail across perimeter router; local hosts cannot resolve names.
- **Topology**: Internal clients on 10.0.1.0/24 query external DNS server 208.67.222.222 via edge router R1.
- **CLI Evidence**:
  ```text
  R1# show access-lists 101
  Extended IP access list 101
      10 permit tcp 10.0.1.0 0.0.0.255 any eq domain (0 matches)
      20 deny ip any any (450 matches)
  ```
- **Root Cause**: ACL 101 permits `tcp ... eq domain` (port 53) but omits `udp ... eq domain`, blocking standard UDP DNS queries.
- **OSI Layer**: Layer 4 (Transport) / Layer 7 (DNS) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 4.4.4 (*Troubleshoot IPv4 ACLs*).

#### CASE-015: Missing IP Domain-Lookup and Name-Server on Router CLI
- **Symptom**: Router cannot resolve hostnames in CLI; ping server1.lab.local fails with Unknown host.
- **Topology**: Router R1 management CLI trying to ping internal syslog/FTP server by hostname.
- **CLI Evidence**:
  ```text
  R1# ping server1.lab.local
  Translating "server1.lab.local"...domain server (255.255.255.255)
  % Unrecognized host or address, or protocol not running.

  R1# show running-config | include ip name-server
  (output empty)
  ```
- **Root Cause**: Router lacks `ip name-server <IP>` and domain lookup configuration.
- **OSI Layer**: Layer 7 (Application) | **Severity**: Medium
- **Reference**: Cisco IOS Basic System Management Command Reference.

---

### 5. Routing: Static Routes & OSPF (Layer 3)

#### CASE-016: Missing Default Route on Branch Edge Router
- **Symptom**: Branch router R1 cannot reach HQ server subnet (10.20.0.0/16); pings from R1 drop.
- **Topology**: Branch R1 connects to ISP via Serial0/0/0 (198.51.100.1/30). Next-hop is ISP Serial0/0/0 (198.51.100.2).
- **CLI Evidence**:
  ```text
  R1# show ip route
  Gateway of last resort is not set
  C    198.51.100.0/30 is directly connected, Serial0/0/0
  C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
  ```
- **Root Cause**: Missing static default route (`ip route 0.0.0.0 0.0.0.0 198.51.100.2`) on branch edge router.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad SRWE Lab 14.3.5 (*Troubleshoot Static and Default Routes*).

#### CASE-017: Static Route Unresolvable Next-Hop (Recursive Failure)
- **Symptom**: Static route installed on Router R1 is inactive and does not appear in the routing table.
- **Topology**: R1 has Gi0/0 (192.168.10.1/24) and Gi0/1 (10.0.0.1/30). Static route configured: `ip route 172.16.1.0 255.255.255.0 10.0.1.2`.
- **CLI Evidence**:
  ```text
  R1# show running-config | include ip route
  ip route 172.16.1.0 255.255.255.0 10.0.1.2

  R1# show ip route 10.0.1.2
  % Network not in table

  R1# show ip route static
  (empty)
  ```
- **Root Cause**: Next-hop IP `10.0.1.2` is not reachable via any connected or known route (typo for `10.0.0.2`).
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad SRWE Module 14 & CCNA Routing Protocols Guide.

#### CASE-018: OSPF MTU Mismatch Blocking DBD Exchange
- **Symptom**: OSPF neighbor adjacency stuck in EXSTART/EXCHANGE state between R1 and R2.
- **Topology**: R1 Gi0/0 (10.1.1.1/30) connects to R2 Gi0/0 (10.1.1.2/30). Area 0.
- **CLI Evidence**:
  ```text
  R1# show ip ospf neighbor
  Neighbor ID     Pri   State           Dead Time   Address         Interface
  2.2.2.2           1   EXSTART/DROTHER 00:00:33    10.1.1.2        GigabitEthernet0/0

  R1# show interfaces Gi0/0 | include MTU
    MTU 1500 bytes, BW 1000000 Kbit/sec

  R2# show interfaces Gi0/0 | include MTU
    MTU 1400 bytes, BW 1000000 Kbit/sec
  ```
- **Root Cause**: Interface MTU mismatch (1500 vs 1400 bytes) prevents database descriptor (DBD) exchange completion.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 2.7.1 (*Troubleshoot Single-Area OSPFv2*).

#### CASE-019: OSPF Area ID Mismatch on Interconnecting Link
- **Symptom**: OSPF neighbor adjacency fails to form; no neighbor listed in `show ip ospf neighbor`.
- **Topology**: R1 Gi0/0 connects to R2 Gi0/0. Both routers configured with `router ospf 1`.
- **CLI Evidence**:
  ```text
  R1# show ip ospf interface Gi0/0 | include Area
    Internet Address 10.1.1.1/30, Area 0, Attached via Interface Enable

  R2# show ip ospf interface Gi0/0 | include Area
    Internet Address 10.1.1.2/30, Area 1, Attached via Interface Enable

  R1# show ip ospf neighbor
  (empty)
  ```
- **Root Cause**: OSPF Area ID mismatch on connecting link (Area 0 on R1 vs Area 1 on R2).
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad ENSA Lab 2.7.2 (*Troubleshoot OSPFv2 Neighbor Relationships*).

#### CASE-020: Missing Network Statement in OSPF Routing Process
- **Symptom**: OSPF neighbor adjacency forms, but R2 LAN subnet (192.168.20.0/24) is not advertised to R1.
- **Topology**: R2 Gi0/1 connects to LAN 192.168.20.0/24. R2 runs OSPF process 1.
- **CLI Evidence**:
  ```text
  R1# show ip route ospf
  (empty)

  R2# show running-config | section router ospf
  router ospf 1
   router-id 2.2.2.2
   network 10.1.1.0 0.0.0.3 area 0
   ! (missing network 192.168.20.0 0.0.0.255 area 0)
  ```
- **Root Cause**: LAN interface subnet was not enabled in OSPF via `network` statement or interface OSPF command.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 2.7.1 (*Single-Area OSPFv2 Configuration*).

#### CASE-021: OSPF Hello/Dead Timer Interval Mismatch
- **Symptom**: OSPF neighbor hello packets ignored; adjacency drops after dead timer expires.
- **Topology**: R1 Gi0/1 connects to R2 Gi0/1.
- **CLI Evidence**:
  ```text
  R1# show ip ospf interface Gi0/1 | include Timer
    Timer intervals configured, Hello 5, Dead 20, Wait 20, Retransmit 5

  R2# show ip ospf interface Gi0/1 | include Timer
    Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5

  %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Gi0/1 from FULL to DOWN, Neighbor Down: Dead timer expired
  ```
- **Root Cause**: Mismatched Hello/Dead timers (5/20s vs 10/40s) violate OSPF adjacency requirements.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: Cisco OSPF Neighbor States Reference & NetAcad ENSA Lab 2.7.2.

---

### 6. Access Control Lists (ACLs) (Layer 3 / 4)

#### CASE-022: Incorrect ACL Rule Ordering (Premature Deny Statement)
- **Symptom**: HR VLAN cannot access Web Server in Server Farm; all HTTP traffic times out.
- **Topology**: HR Subnet: 192.168.10.0/24. Web Server: 172.16.50.100 (Port 80/443). ACL 100 on R1 Gi0/0 inbound.
- **CLI Evidence**:
  ```text
  R1# show access-lists 100
  Extended IP access list 100
      10 deny ip 192.168.10.0 0.0.0.255 any (245 matches)
      20 permit tcp any host 172.16.50.100 eq www
      30 permit ip any any

  R1# show running-config interface Gi0/0
  interface GigabitEthernet0/0
   ip access-group 100 in
  ```
- **Root Cause**: Broad `deny ip 192.168.10.0 0.0.0.255 any` at sequence 10 shadows specific permit rule at sequence 20.
- **OSI Layer**: Layer 3 (Network) / Layer 4 (Transport) | **Severity**: Critical
- **Reference**: NetAcad ENSA Lab 4.4.4 (*Troubleshoot IPv4 ACLs*).

#### CASE-023: VTY Access-Class Blocking Admin SSH Subnet
- **Symptom**: Branch network cannot SSH into Edge Router management interface; pings succeed.
- **Topology**: Admin PC (192.168.1.100) attempting SSH to Router R1 (192.168.1.1).
- **CLI Evidence**:
  ```text
  Admin-PC> ssh -l admin 192.168.1.1
  Connection closed by foreign host.

  R1# show running-config | section line vty
  line vty 0 4
   access-class 21 in
   transport input ssh

  R1# show access-lists 21
  Standard IP access list 21
      10 permit 192.168.2.0, wildcard bits 0.0.0.255
      ! (Implicit deny blocks 192.168.1.100)
  ```
- **Root Cause**: Standard ACL 21 only permits management subnet `192.168.2.0/24`, denying `192.168.1.100`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ITN Lab 16.5.1 & ENSA Lab 4.2.7.

#### CASE-024: Inverted Wildcard Mask in Extended ACL
- **Symptom**: Outbound traffic from Engineering VLAN blocked at border router; show access-lists shows hits on deny.
- **Topology**: Engineering Subnet 10.10.0.0/16. ACL 110 placed on R1 Gi0/1 (Outbound to ISP).
- **CLI Evidence**:
  ```text
  R1# show access-lists 110
  Extended IP access list 110
      10 permit ip 10.10.0.0 0.0.0.255 any (0 matches)
      20 deny ip any any (132 matches)
  ```
- **Root Cause**: Wildcard mask `0.0.0.255` (/24) applied instead of `0.0.255.255` (/16), blocking half the subnet addresses.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Medium
- **Reference**: NetAcad ENSA Lab 4.4.4 & Cisco ACL Wildcard Mask Reference.

#### CASE-025: ACL Directional Misconfiguration Dropping Server Responses
- **Symptom**: Web clients cannot reach intranet HTTPS server after applying outbound ACL on router interface.
- **Topology**: Clients 192.168.1.0/24 accessing internal Web Server 10.0.0.50 on port 443.
- **CLI Evidence**:
  ```text
  R1# show access-lists 105
  Extended IP access list 105
      10 permit tcp any host 10.0.0.50 eq 443

  R1# show running-config interface Gi0/0
  interface GigabitEthernet0/0
   ip access-group 105 in
  ```
- **Root Cause**: ACL applied inbound on LAN interface allows clients to initiate TCP, but lacks established return rule.
- **OSI Layer**: Layer 4 (Transport) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 4.4.4 (*Troubleshoot Extended ACLs*).

---

### 7. NAT & PAT (Network Address Translation) (Layer 3)

#### CASE-026: Undefined ACL in NAT Inside Source List Command
- **Symptom**: Internal LAN clients cannot access Internet; ping to public IP 203.0.113.1 fails.
- **Topology**: Internal LAN: 192.168.1.0/24. Edge Router R1 WAN IP: 209.165.200.225/30 on Serial0/1/0.
- **CLI Evidence**:
  ```text
  R1# show ip nat translations
  (empty)

  R1# show running-config | include ip nat
  ip nat inside source list 1 interface Serial0/1/0 overload

  R1# show access-lists 1
  (empty / ACL not configured)
  ```
- **Root Cause**: Standard ACL 1 referenced by the `ip nat inside source` statement does not exist, permitting 0 packets.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad ENSA Lab 5.4.3 (*Troubleshoot NAT Configuration*).

#### CASE-027: Omission of 'Overload' Keyword Causing NAT Pool Exhaustion
- **Symptom**: Only one internal host can access the Internet simultaneously; subsequent hosts time out.
- **Topology**: Internal Subnet 192.168.10.0/24. Router R1 WAN interface Gi0/0/1 (Public IP 203.0.113.5).
- **CLI Evidence**:
  ```text
  R1# show ip nat translations
  Pro Inside global         Inside local          Outside local         Outside global
  --- 203.0.113.5           192.168.10.15         ---                   ---

  R1# show running-config | include ip nat inside source
  ip nat inside source list 10 interface GigabitEthernet0/0/1
  ```
- **Root Cause**: Missing `overload` keyword creates static 1-to-1 dynamic translation rather than Port Address Translation (PAT).
- **OSI Layer**: Layer 3 (Network) | **Severity**: Critical
- **Reference**: NetAcad ENSA Lab 5.4.3 & Cisco IOS NAT Configuration Guide.

#### CASE-028: Missing 'ip nat inside' Configuration on LAN Interface
- **Symptom**: NAT translations not occurring; show ip nat translations is completely empty despite active traffic.
- **Topology**: Router R1 connects LAN on Gi0/0 and ISP on Gi0/1. NAT overload configured for ACL 5.
- **CLI Evidence**:
  ```text
  R1# show running-config interface Gi0/0
  interface GigabitEthernet0/0
   ip address 192.168.1.1 255.255.255.0
   ! (Missing ip nat inside)

  R1# show running-config interface Gi0/1
  interface GigabitEthernet0/1
   ip address 203.0.113.2 255.255.255.252
   ip nat outside
  ```
- **Root Cause**: Internal interface Gi0/0 is not designated as NAT inside interface (`ip nat inside` missing).
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 5.4.3 (*Troubleshoot NAT*).

#### CASE-029: Typo in Static NAT Inside Local Private IP
- **Symptom**: Static NAT for DMZ Web Server fails; external users cannot access public IP 209.165.201.5.
- **Topology**: DMZ Web Server private IP: 192.168.50.10. Public IP: 209.165.201.5. Edge Router R1.
- **CLI Evidence**:
  ```text
  R1# show running-config | include ip nat inside source static
  ip nat inside source static 192.168.50.100 209.165.201.5

  R1# show ip interface brief | include GigabitEthernet0/2
  GigabitEthernet0/2     192.168.50.1    YES manual up                    up
  ```
- **Root Cause**: Static NAT statement maps to non-existent private host `192.168.50.100` instead of `192.168.50.10`.
- **OSI Layer**: Layer 3 (Network) | **Severity**: High
- **Reference**: NetAcad ENSA Lab 5.2.6 & 5.4.3.

---

### 8. Wireless LAN & Switch Security (Layer 2)

#### CASE-030: Corporate WLAN Profile Disabled on Wireless LAN Controller (WLC)
- **Symptom**: Wireless laptop cannot connect to Corporate SSID; receives 'Unable to connect to this network'.
- **Topology**: Laptop-1 connecting to SSID 'Corp-Secure' managed by Cisco WLC 3504 / 2504.
- **CLI Evidence**:
  ```text
  (Cisco Controller) > show wlan summary
  Number of WLANs.................................. 1
  WLAN ID  WLAN Profile Name / SSID          Status    Interface Name
  -------  --------------------------------  --------  --------------------
  1        Corp-Secure / Corp-Secure         Disabled  management
  ```
- **Root Cause**: WLAN profile is set to `Disabled` state in WLC configuration (`config wlan enable 1` required).
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 13.5.1 (*Troubleshoot WLAN Issues on WLC*).

#### CASE-031: Wireless Guest VLAN Not Tagged on Uplink Switch
- **Symptom**: Wireless clients associate with SSID 'Guest-WiFi' but fail to receive IP address from DHCP.
- **Topology**: WLC with AP1. SSID 'Guest-WiFi' mapped to interface 'guest-interface' (VLAN 40).
- **CLI Evidence**:
  ```text
  (Cisco Controller) > show interface summary
   Interface Name        Port Vlan Id  IP Address      Type    Ap Mgr
  ---------------------  ---- -------  --------------- ------- ------
   guest-interface       1    40       192.168.40.254  Dynamic No

  S1# show vlan brief | include 40
  (output empty - VLAN 40 does not exist on switch)
  ```
- **Root Cause**: Dynamic VLAN 40 assigned to Guest SSID is missing from the Layer 2 switch database.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 13.4.5 (*Troubleshoot WLAN Issues*).

#### CASE-032: Port Security Violation Triggering Err-Disabled State
- **Symptom**: Switch port shuts down immediately when user connects a new laptop; port LED turns solid amber.
- **Topology**: User on Switch S1 interface FastEthernet0/10. Port security configured with max MAC 1.
- **CLI Evidence**:
  ```text
  S1# show interfaces Fa0/10 status
  Port      Name               Status       Vlan       Duplex  Speed Type
  Fa0/10                       err-disabled 10           auto   auto 10/100BaseTX

  S1# show port-security interface Fa0/10
  Port Security              : Enabled
  Port Status                : Secure-shutdown
  Violation Mode             : Shutdown
  Last Source Address:Vlan   : 0050.7966.6803:10
  ```
- **Root Cause**: MAC address violation on port Fa0/10 exceeded `maximum 1`, placing port into `err-disabled`.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: High
- **Reference**: NetAcad SRWE Lab 10.4.3 (*Troubleshoot LAN Security*).

#### CASE-033: Global Spanning Tree Protocol Accidental Deactivation
- **Symptom**: Spanning Tree loop detected; high CPU utilization and broadcast radiation across switch fabric.
- **Topology**: Triangular switch loop between S1, S2, S3 with redundant Gigabit uplinks.
- **CLI Evidence**:
  ```text
  S2# show spanning-tree
  No spanning tree instance exists.

  S2# show processes cpu | include CPU
  CPU utilization for five seconds: 99%/24%; one minute: 98%; five minutes: 95%
  ```
- **Root Cause**: Global Spanning Tree was disabled via `no spanning-tree vlan 1-4094`, causing an unmitigated Layer 2 loop.
- **OSI Layer**: Layer 2 (Data Link) | **Severity**: Critical
- **Reference**: NetAcad SRWE Lab 5.1.9 (*Troubleshoot STP*).

#### CASE-034: Host Subnet Mask Misconfiguration Restricting Broadcast Domain
- **Symptom**: Subnet mask mismatch causes host to reject direct Layer 2 communication with neighbor.
- **Topology**: Host A (192.168.1.10/24) and Host B (192.168.1.150/26) on the same VLAN and switch. Host B cannot ping Host A.
- **CLI Evidence**:
  ```text
  Host-A> ipconfig
     IPv4 Address: 192.168.1.10
     Subnet Mask:  255.255.255.0

  Host-B> ipconfig
     IPv4 Address: 192.168.1.150
     Subnet Mask:  255.255.255.192
  ```
- **Root Cause**: Host B has `/26` mask (255.255.255.192), treating `192.168.1.10` as off-subnet and failing to ARP directly.
- **OSI Layer**: Layer 3 (Network) | **Severity**: Medium
- **Reference**: NetAcad ITN Lab 11.5.5 (*Subnetting Scenarios*).
