# Latency-Aware Network Protection
### A Hardware-Accelerated ML Middle Layer for Universal IDS Orchestration in ISP Environments

**M.Sc. Thesis — Data Science**  
University of Campania Luigi Vanvitelli, Italy  
Industry Partner: **TIM S.p.A. (Telecom Italia)**  
Author: Ali Ahson · [aahson45@gmail.com](mailto:aahson45@gmail.com)

---

## The Problem

Internet Service Providers like TIM rely on pfSense for traffic management, but traditional Intrusion Detection Systems (Snort, Suricata) impose a critical trade-off: the deeper the inspection, the higher the latency. During peak traffic events, inline Deep Packet Inspection consumes the same CPU resources that pfSense needs to route packets — causing measurable jitter and customer-facing degradation.

The result is that most ISPs are forced into **threat control** (passive monitoring) rather than **active protection** (real-time blocking), because blocking inline is too expensive at scale.

---

## The Solution

This research proposes a **two-speed hybrid ML orchestration layer** that sits between pfSense and any downstream IDS:

```
                    ┌─────────────────────────────────┐
  Network Traffic   │           pfSense               │
  ─────────────────►│    (Packet Filter / Router)     │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │     ML MIDDLE LAYER              │
                    │  ┌──────────────────────────┐   │
                    │  │  Packet Feature Selection │   │
                    │  │  (12 Header-Level Features│   │
                    │  └────────────┬─────────────┘   │
                    │               │                  │
                    │  ┌────────────▼─────────────┐   │
                    │  │  Multi-Class ML Classifier│   │
                    │  │  XGBoost / LightGBM       │   │
                    │  └────────────┬─────────────┘   │
                    └───────────────┼─────────────────┘
                                    │
               ┌────────────────────┼──────────────────┐
               │                   │                   │
    ┌──────────▼──────┐  ┌─────────▼────────┐  ┌──────▼──────────┐
    │  BENIGN          │  │  SUSPICIOUS      │  │  CRITICAL THREAT │
    │  Fast Path       │  │  Deep Inspection │  │  Instant Block   │
    │  0ms overhead    │  │  Snort / Suricata│  │  pfctl API call  │
    └──────────────────┘  └──────────────────┘  └─────────────────┘
                                    │
                    ┌───────────────▼─────────────────┐
                    │     UNIVERSAL ORCHESTRATOR       │
                    │  IDS-Agnostic Rule Rewriter      │
                    │  Reads: EVE JSON / Unified2      │
                    │  Writes: Dynamic pfSense Rules   │
                    └─────────────────────────────────┘
```

### Two-Speed Design

**Speed 1 — Offline Batch Engine (every 5 minutes)**
- Ingests network flow logs from the live environment
- Runs multi-class ML inference on accumulated traffic
- Rewrites Snort / Suricata rules to reflect emerging threat patterns
- Operates completely off the packet path — zero added latency to live traffic

**Speed 2 — Hardware-Accelerated Fast Path (real-time)**
- Lightweight binary classifier for high-confidence volumetric threats (DDoS)
- Triggers immediate `pfctl` firewall block without waiting for the batch cycle
- Theoretically offloadable to SmartNIC (NVIDIA BlueField / P4) or GPU (TensorRT)

---

## Dataset

Training and evaluation uses a merged dataset from:

| Source | Records | Attack Types |
|---|---|---|
| CICIDS 2017 | ~2.8M | DoS, Brute Force, Web Attacks, Infiltration |
| CSE-CIC-IDS 2018 | ~16M | DDoS, Botnet, Infiltration, SQL Injection |
| **Merged** | **~18M** | **Unified 6-class taxonomy** |

### Unified Attack Taxonomy

| Class | Source Labels | pfSense Response |
|---|---|---|
| Benign | Benign | Fast-path (0ms overhead) |
| DoS / DDoS | DoS Hulk, GoldenEye, Slowloris, LOIC | Rate limit at edge |
| Brute Force | FTP-Patator, SSH-Patator, Web BF | Block IP after threshold |
| Botnet | Botnet ARES | Deep scan via IDS |
| Web Attacks | SQLi, XSS, Web BF | Redirect / IDS signature |
| Infiltration | Infiltration | Log as potential zero-day |

---

## Packet Feature Selection (The "Golden 12")

Reducing 80+ raw flow features to 12 header-level, hardware-extractable attributes:

| Feature | Category | Why It Matters |
|---|---|---|
| Fwd Header Len | Layer 4 Header | Tunneling / exploit packet detection |
| Bwd Header Len | Layer 4 Header | C2 traffic asymmetry (Botnet) |
| Fwd PSH Flags | Layer 4 Header | Rapid-fire brute force (SSH/FTP) |
| ACK Flag Count | Layer 4 Header | ACK-flood DDoS detection |
| Init Win Bytes Fwd | Layer 4 Header | Slowloris / DoS window manipulation |
| Flow Duration | Flow Metadata | Slow-and-Low DoS identification |
| Flow Pkts/s | Flow Metadata | Volumetric DDoS indicator |
| Flow Byts/s | Flow Metadata | Data exfiltration detection |
| Fwd Pkt Len Max | Flow Metadata | Large payload web attacks (SQLi) |
| Flow IAT Mean | Temporal | Bot heartbeat regularity |
| Fwd IAT Max | Temporal | Low-and-slow brute force timing |
| Bwd IAT Min | Temporal | High-speed DDoS reflection |

> **Key design decision:** All 12 features are extracted from packet headers and flow timing — no payload inspection required. This means the classifier works on encrypted TLS traffic and is suitable for SmartNIC hardware offload.

---

## Model

| Candidate | Why |
|---|---|
| XGBoost | Strong tabular performance, fast inference, quantisable to INT8 |
| LightGBM | Lower memory footprint, faster training on large datasets |

Evaluation metrics are chosen for ISP relevance:
- **Macro-Averaged F1-Score** — ensures rare attack classes (Infiltration, Botnet) are not ignored
- **Flow Processing Latency (μs)** — measures real overhead added to the packet path
- **False Positive Rate** — proxy for customer-facing service disruption

---

## Hardware Acceleration (Theoretical Evaluation)

| Approach | Latency | Model Complexity | Use Case |
|---|---|---|---|
| SmartNIC (NVIDIA BlueField / P4) | Microseconds | Shallow ML only | Feature extraction + binary triage |
| GPU (NVIDIA T4 via TensorRT) | Milliseconds | Deep models possible | Full multi-class inference at scale |
| CPU only | 10–50ms+ | Any | Development / baseline only |

The thesis evaluates the latency-accuracy trade-off across these paths under simulated ISP traffic loads, including peak-traffic scenarios analogous to high-demand broadcast events.

---

## Universal Orchestrator

The orchestrator is IDS-agnostic by design. It reads standardised log output from either IDS backend and translates ML decisions into pfSense firewall actions:

```
IDS Output          Orchestrator Action         pfSense Command
──────────────────────────────────────────────────────────────
Suricata EVE JSON → Parse alert + ML validate → pfctl -t block -T add [IP]
Snort Unified2    → Parse alert + ML validate → pfctl -t block -T add [IP]
ML-only (batch)   → Rewrite IDS rules         → Reload Snort / Suricata config
```

Switching between Snort 3 and Suricata 7 requires no changes to the orchestrator — only the log parser adapter changes.

---

## Repository Structure

```
thesis-ml-ids/
├── data/
│   ├── preprocessing/          # Merging, alignment, SMOTE scripts
│   ├── feature_selection/      # RFE, Information Gain analysis
│   └── unified_taxonomy.py     # Label mapping (2017 + 2018 → 6 classes)
├── models/
│   ├── train_xgboost.py        # Multi-class XGBoost training pipeline
│   ├── train_lgbm.py           # LightGBM baseline
│   └── evaluate.py             # F1, latency, FPR benchmarks
├── orchestrator/
│   ├── parser_suricata.py      # EVE JSON alert reader
│   ├── parser_snort.py         # Unified2 alert reader
│   ├── pfsense_api.py          # pfctl / pfSense API connector
│   └── rule_rewriter.py        # Offline batch rule generation
├── hardware/
│   └── smartnic_notes.md       # P4 / DPDK offload design notes
├── docs/
│   ├── thesis_proposal.pdf     # Research proposal (attached to PhD emails)
│   └── architecture.md        # Detailed system design
└── README.md
```

> **Note:** This repository is under active development alongside the thesis. Code will be added progressively as each component is completed.

---

## Industry Context

This research is conducted in direct collaboration with **TIM S.p.A. (Telecom Italia)**, providing access to a realistic ISP deployment environment built around pfSense. The collaboration ensures that the technical requirements reflect production constraints rather than laboratory assumptions.

The open-source foundation of pfSense (FreeBSD / pf) aligns with the European Digital Sovereignty agenda, making this framework directly relevant to the German National Cybersecurity Strategy and the EU's push to reduce dependence on proprietary security infrastructure.

---

## Tech Stack

Python · XGBoost · LightGBM · Scikit-learn · Pandas · Scapy · pfSense API · Snort 3 · Suricata 7 · CICIDS 2017/2018 · SmartNIC (theoretical) · TensorRT (theoretical)

---

## Status

| Component | Status |
|---|---|
| Dataset merging and preprocessing | 🔄 In progress |
| Feature selection (Golden 12) | 🔄 In progress |
| Multi-class model training | ⏳ Planned |
| Orchestrator daemon | ⏳ Planned |
| Hardware offload evaluation | ⏳ Planned |
| Final thesis submission | 🎯 June/July 2025 |

---

## Contact

**Ali Ahson** · M.Sc. Data Science · University of Campania Luigi Vanvitelli  
aahson45@gmail.com · [LinkedIn](https://linkedin.com/in/ali-ahson) · [GitHub](https://github.com/aahson45)
