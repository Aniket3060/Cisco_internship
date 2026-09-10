# NetSage AI: AI Troubleshooting Helper with Human Review

**Cisco Virtual Internship Program 2026 — Problem Statement 2**

NetSage AI is an AI-assisted network troubleshooting helper combining a deterministic Python rule-validation engine with structured generative AI reasoning and mandatory human-in-the-loop engineering review.

---

## Repository Structure

```
cisco/
├── data/
│   ├── cases.csv                   # 34 curated CCNA/NetAcad-grounded troubleshooting cases
│   ├── cases_reference.md          # Comprehensive case catalog with citations & CLI outputs
│   ├── sample_network_state.json   # SAMPLE/TEST dataset for rule checker validation
│   ├── sample_show_outputs.txt     # Sample Cisco CLI show command outputs
│   └── llm_outputs/                # 34 generated JSON diagnoses from the LLM
├── prompts/
│   ├── system_prompt.md            # NetSage AI core system prompt & JSON schema
│   ├── diagnose_prompt.md          # Diagnosis prompt template with 3 worked examples
│   └── helper_templates.md         # Human review verdict template & verification prompt
├── src/
│   ├── __init__.py
│   ├── parsers.py                  # State and CLI parsers
│   └── rule_checker.py             # Deterministic Python Rule Checker
├── tests/
│   └── test_rule_checker.py        # Unit tests for deterministic validation rules
├── scripts/
│   └── run_all_cases.py            # Batch script to execute LLM diagnosis on all 34 cases
├── report/
│   ├── NetSage_AI_Project_Report.typ # Complete Cisco/AICTE project report (Typst source)
│   ├── NetSage_AI_Project_Report.pdf # Final compiled project report
│   └── certificates/                 # Cisco NetAcad course completion certificates
└── README.md
```

---

## Quick Start: Running the Deterministic Rule Checker

### 1. Run the Unit Test Suite
```bash
python -m unittest discover tests
```

### 2. Run the Rule Checker in Terminal Text Mode
```bash
python src/rule_checker.py --config data/sample_network_state.json
```

### 3. Run the Rule Checker in JSON Mode
```bash
python src/rule_checker.py --config data/sample_network_state.json --json
```

---

## Workflow Overview

1. **Deterministic Pre-Check:** Run `rule_checker.py` against the network topology to instantly identify hard constraints (duplicate IPs, gateway errors, admin down interfaces, VLAN mismatches, ACL shadowing).
2. **AI Diagnosis:** Pass the symptom, show command outputs, and rule checker flags into `prompts/diagnose_prompt.md`.
3. **Human Review:** The engineer evaluates the AI diagnosis, assigns a verdict (**ACCEPTED / EDITED / REJECTED**), and records it in `report/NetSage_AI_Project_Report.typ`.
4. **Remediation & Verification:** Apply the remediation commands in Cisco Packet Tracer and run verification pings.
