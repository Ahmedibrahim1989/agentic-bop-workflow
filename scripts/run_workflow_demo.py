#!/usr/bin/env python
"""Run the complete BOP standardization workflow with simulated Claude API responses.

This demo script demonstrates the full 5-agent workflow pipeline with realistic
outputs to show how the system functions.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Simulated agent outputs for demonstration
DEMO_OUTPUTS = {
    "agent1": """# Agent 1 – Comparison Analysis Report

## Executive Summary
This report presents a comprehensive comparison of BOP Installation procedures across three ADNOC rigs: DANA, ALREEM, and MARAWWAH.

## Document Inventory

| Rig | Document Type | Version | Date |
|-----|--------------|---------|------|
| DANA | ROP | 2.1 | 2024-01-15 |
| DANA | JSA | 2.0 | 2024-01-15 |
| ALREEM | ROP | 1.8 | 2024-02-01 |
| ALREEM | JSA | 1.5 | 2024-02-01 |
| MARAWWAH | ROP | 3.0 | 2024-03-10 |
| MARAWWAH | JSA | 2.5 | 2024-03-10 |

## Structural Comparison

### Common Elements Across All Rigs
1. **Pre-Job Preparation Phase**
   - Personnel briefing/toolbox talk
   - Equipment inspection
   - Weather condition assessment
   - Exclusion zone establishment

2. **BOP Lifting Operations**
   - Use of certified rigging equipment
   - Test lift and hold procedures
   - Tag line usage for load control

3. **Installation Sequence**
   - Positioning over wellhead
   - Controlled descent
   - Connector engagement and torquing
   - Verification and testing

### Key Differences Identified

| Aspect | DANA | ALREEM | MARAWWAH |
|--------|------|--------|----------|
| Wind Limit | 25 knots | 30 knots | 28 knots |
| Exclusion Zone | 10m | 8m | 12m |
| Test Lift Hold | 5 min | 3 min | 5 min |
| Max Sling Angle | 45° | Not specified | 60° |
| Descent Rate (final) | 0.5m/min | Not specified | 0.3m/min |
| Pressure Test | 10,000 psi | Rated WP | 15,000 psi |

## Step-by-Step Mapping

### Phase 1: Pre-Job Preparations
- **DANA**: 6 detailed steps including radio communication verification
- **ALREEM**: 5 basic steps, less detailed
- **MARAWWAH**: 6 steps with emergency response plan requirement

### Phase 2: BOP Handling/Lifting
- **DANA**: Includes specific sling angle requirements (45°), 4-point lift
- **ALREEM**: General lifting requirements only
- **MARAWWAH**: Most detailed with 4 tag lines required, 3m clearance

### Phase 3: Installation
- **DANA**: 7-step process with gap measurements
- **ALREEM**: 5-step simplified process
- **MARAWWAH**: 7-step process with star-pattern torque sequence

### Phase 4: Post-Installation
- **DANA**: 4-step verification with specific pressure test value
- **ALREEM**: 3-step basic testing
- **MARAWWAH**: 5-step comprehensive documentation requirement

## Terminology Analysis
- "Toolbox talk" (DANA) = "Pre-job meeting" (ALREEM) = "Pre-job briefing" (MARAWWAH)
- "Exclusion zone" terminology consistent across all rigs
- "Tag lines" terminology consistent across all rigs

## Observations
1. MARAWWAH has the most comprehensive and detailed procedures
2. ALREEM procedures are the most abbreviated
3. DANA procedures have good detail but could benefit from standardization
""",

    "agent2": """# Agent 2 – Gap Analysis Report

## Executive Summary
This gap analysis identifies missing steps, hazards, and control measures across the three rig procedures for BOP Installation.

## Critical Gaps Identified

### Category 1: Safety-Critical Omissions

#### 1.1 Weather Monitoring
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Continuous monitoring during operation | ✗ Missing | ✗ Missing | ✓ Present |
| Abort criteria specified | ✓ Present | ✗ Missing | ✓ Present |
| Communication protocol for weather changes | ✗ Missing | ✗ Missing | ✗ Missing |

**Risk Level: HIGH** - Operations could continue in deteriorating conditions

#### 1.2 Emergency Stop Procedures
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Emergency lowering procedure | ✗ Missing | ✗ Missing | ✓ Partial |
| Load release mechanism | ✗ Missing | ✗ Missing | ✗ Missing |
| Emergency contact protocol | ✓ Present | ✗ Missing | ✓ Present |

**Risk Level: HIGH** - No clear procedure for emergency situations during lift

#### 1.3 Communication Protocol
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Radio check procedure | ✓ Present | ✗ Missing | ✓ Present |
| Hand signal standardization | ✓ Mentioned | ✗ Missing | ✓ Mentioned |
| Communication failure procedure | ✗ Missing | ✗ Missing | ✗ Missing |

**Risk Level: MEDIUM** - Communication gaps could lead to incidents

### Category 2: Equipment-Related Gaps

#### 2.1 Rigging Equipment
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Sling capacity requirements | ✗ Missing | ✗ Missing | ✗ Missing |
| Shackle specifications | ✗ Missing | ✗ Missing | ✗ Missing |
| Color-coding system | ✗ Missing | ✗ Missing | ✓ Present |

#### 2.2 Torque Equipment
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Calibration verification | ✗ Missing | ✓ Present | ✓ Present |
| Torque value documentation | Refers to OEM | Refers to OEM | Refers to OEM |
| Torque sequence diagram | ✗ Missing | ✗ Missing | ✓ Present (star pattern) |

### Category 3: Human Performance Gaps

#### 3.1 Personnel Competency
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Competency requirements listed | ✗ Missing | ✗ Missing | ✗ Missing |
| Role assignments | ✓ Partial | ✗ Missing | ✓ Partial |
| Banksman/signaller designation | ✗ Missing | ✗ Missing | ✗ Missing |

#### 3.2 Verification Steps
| Gap | DANA | ALREEM | MARAWWAH |
|-----|------|--------|----------|
| Independent verification | ✗ Missing | ✗ Missing | ✓ Present |
| Peer review checkpoints | ✗ Missing | ✗ Missing | ✗ Missing |
| Sign-off requirements | ✗ Missing | ✗ Missing | ✓ Present |

## Missing Steps by Phase

### Pre-Job Phase
1. **ALREEM missing**: Crane certification verification, radio communication check
2. **ALL rigs missing**: Minimum crew requirement specification, backup plan review

### Lifting Phase
1. **ALREEM missing**: Sling angle verification, specific hold time
2. **DANA missing**: Banksman positioning, clearance verification
3. **ALL rigs missing**: Secondary lift device standby

### Installation Phase
1. **ALREEM missing**: Gap measurement verification
2. **DANA missing**: Star-pattern torque sequence
3. **ALL rigs missing**: Thread compound application procedure

### Post-Installation Phase
1. **ALREEM missing**: Documentation requirements
2. **ALL rigs missing**: Handover procedure to operations

## Hazard Coverage Matrix

| Hazard | DANA JSA | ALREEM JSA | MARAWWAH JSA |
|--------|----------|------------|--------------|
| Dropped load | ✓ | ✓ | ✓ |
| Pinch points | ✓ | ✓ | ✓ |
| Crush hazard | ✓ | ✗ | ✓ |
| Swing hazard | ✓ | ✗ | ✓ |
| Weather exposure | ✗ | ✗ | ✓ |
| Pressure release | ✗ | ✗ | ✓ |
| H2S exposure | ✗ | ✗ | ✗ |

## Priority Recommendations

### Immediate (High Priority)
1. Add emergency stop and load lowering procedures to all ROPs
2. Standardize weather monitoring and abort criteria
3. Include communication failure procedures

### Short-term (Medium Priority)
1. Add specific equipment specifications to all procedures
2. Include competency requirements for each role
3. Standardize verification and sign-off requirements

### Long-term (Low Priority)
1. Develop visual aids and diagrams for torque sequences
2. Create standardized checklists across all rigs
3. Implement digital documentation systems
""",

    "agent3": """# Agent 3 – Human Performance (HP) Evaluation Report

## Executive Summary
This report evaluates the human performance maturity of BOP Installation procedures across DANA, ALREEM, and MARAWWAH rigs using established HP principles.

## HP Maturity Assessment

### Overall Maturity Scores (1-5 Scale)

| HP Element | DANA | ALREEM | MARAWWAH | Industry Best Practice |
|------------|------|--------|----------|----------------------|
| Error Prevention | 3.0 | 2.0 | 3.5 | 4.5 |
| Human-Machine Interface | 2.5 | 2.0 | 3.0 | 4.0 |
| Workload Management | 2.0 | 1.5 | 2.5 | 4.0 |
| Fatigue Management | 1.0 | 1.0 | 1.5 | 4.0 |
| Communication | 3.0 | 2.0 | 3.5 | 4.5 |
| Supervision | 2.5 | 2.0 | 3.0 | 4.0 |
| **Overall Score** | **2.3** | **1.8** | **2.8** | **4.2** |

### HP Element Analysis

#### 1. Error Prevention Mechanisms

**DANA (Score: 3.0)**
- ✓ Pre-use inspection checklist mentioned
- ✓ Test lift verification before full lift
- ✗ No error trapping mechanisms
- ✗ No concurrent verification steps

**ALREEM (Score: 2.0)**
- ✓ Basic inspection mentioned
- ✗ No verification steps
- ✗ No error prevention tools
- ✗ No stop-work authority mentioned

**MARAWWAH (Score: 3.5)**
- ✓ 100% equipment inspection with documentation
- ✓ Independent verification of torque values
- ✓ Color-coded rigging system
- ✗ Limited error trapping mechanisms

#### 2. STAR Methodology Analysis

| Component | DANA | ALREEM | MARAWWAH |
|-----------|------|--------|----------|
| Stop | Not explicit | Not present | Partial (slow descent) |
| Think | Pre-job meeting | Basic briefing | Formal meeting with sign-off |
| Act | Procedures provided | Basic procedures | Detailed procedures |
| Review | Some verification | Minimal | Documentation required |

#### 3. Questioning Attitude Elements

**Present in Procedures:**
- MARAWWAH: "Verbal confirmation before each movement"
- DANA: "Verify proper seating using visual inspection"
- ALREEM: Limited questioning attitude elements

**Missing Elements:**
- Time-out procedures not clearly defined
- Stop-work authority not explicitly granted
- Challenge mechanisms not documented

### Defense Barriers Assessment

#### Administrative Controls
| Control Type | DANA | ALREEM | MARAWWAH |
|--------------|------|--------|----------|
| Written procedures | ✓ | ✓ | ✓ |
| JSA completed | ✓ | ✓ | ✓ |
| Sign-off sheet | ✗ | ✗ | ✓ |
| Permit system | ✗ | ✗ | ✗ |

#### Engineering Controls
| Control Type | DANA | ALREEM | MARAWWAH |
|--------------|------|--------|----------|
| Load indicators | Not specified | Not specified | Not specified |
| Limit switches | Not specified | Not specified | Not specified |
| Exclusion barriers | Physical barriers | Not specified | Physical barriers |

### Cognitive Load Analysis

**High Cognitive Load Tasks Identified:**
1. Simultaneous monitoring of multiple parameters during lift
2. Communication between multiple parties
3. Real-time adjustment decisions
4. Weather condition assessment

**Mitigation Strategies Present:**
- MARAWWAH: 4 dedicated tag line personnel reduces individual load
- DANA: Standardized hand signals reduce communication complexity
- ALREEM: None identified

### Fatigue Risk Factors

**Risk Factors Not Addressed:**
1. Maximum shift duration not specified
2. Rest requirements not mentioned
3. Rotation of personnel not addressed
4. Time-sensitive decision points not identified

**Recommendations:**
1. Add time restrictions for continuous operations
2. Specify mandatory rest breaks during extended operations
3. Define rotation schedules for high-workload positions

## HP Improvement Recommendations

### Tier 1: Critical Improvements

1. **Implement STAR at Critical Steps**
   - Add explicit Stop-Think-Act-Review at:
     * Test lift initiation
     * Final descent (last 3m)
     * Connector engagement
     * Torquing sequence

2. **Add Concurrent Verification**
   - Require two-person verification for:
     * Sling attachment points
     * Torque values
     * Pressure test readings

3. **Establish Stop-Work Authority**
   - Clear language that any person can stop work
   - No retribution policy
   - Required documentation of stop-work events

### Tier 2: Important Improvements

1. **Standardize Communication Protocol**
   - Implement 3-way communication
   - Define radio call signs
   - Establish backup communication method

2. **Add Visual Verification Tools**
   - Torque sequence diagrams
   - Go/No-Go gauges for gaps
   - Color-coded lift stages

### Tier 3: Best Practice Enhancements

1. **Implement HP Tool Usage**
   - Self-checking (STAR)
   - Peer checking
   - Flagging (marking last good step)
   - Place keeping (progress tracking)

2. **Enhance Situational Awareness**
   - Pre-job briefing enhancements
   - Timeout triggers defined
   - Leadership walk-throughs

## Compliance with ADNOC HP Standards

| ADNOC HP Requirement | DANA | ALREEM | MARAWWAH |
|---------------------|------|--------|----------|
| Pre-job briefing | ✓ Compliant | ✓ Compliant | ✓ Compliant |
| Written procedure | ✓ Compliant | ✓ Compliant | ✓ Compliant |
| JSA completion | ✓ Compliant | ✓ Compliant | ✓ Compliant |
| STAR application | ✗ Gap | ✗ Gap | ⚠ Partial |
| Verification steps | ⚠ Partial | ✗ Gap | ✓ Compliant |
| Documentation | ⚠ Partial | ✗ Gap | ✓ Compliant |
""",

    "agent4": """# Agent 4 – Equipment Validation Report

## Executive Summary
This report validates equipment specifications, feasibility across rigs, and standardization opportunities for BOP Installation operations.

## Equipment Inventory Comparison

### Lifting Equipment

| Parameter | DANA | ALREEM | MARAWWAH |
|-----------|------|--------|----------|
| Crane type | Not specified | Not specified | Not specified |
| Crane capacity | Not specified | Not specified | Not specified |
| Sling type | Certified slings | Lifting gear | Certified slings |
| Lift configuration | 4-point | Not specified | 4-point |
| Max sling angle | 45° | Not specified | 60° |

**Gap Analysis:**
- No crane specifications in any procedure
- Sling capacities not defined
- Load chart references missing

### Tag Line Equipment

| Parameter | DANA | ALREEM | MARAWWAH |
|-----------|------|--------|----------|
| Number required | 2 (minimum) | Not specified | 4 |
| Length | Not specified | Not specified | Not specified |
| Material | Not specified | Not specified | Not specified |

### Torque Equipment

| Parameter | DANA | ALREEM | MARAWWAH |
|-----------|------|--------|----------|
| Calibration required | Implied | ✓ Required | ✓ Required |
| Torque range | OEM reference | OEM reference | OEM reference |
| Torque sequence | Not specified | Not specified | Star pattern |

### BOP Specifications

| Parameter | DANA | ALREEM | MARAWWAH |
|-----------|------|--------|----------|
| BOP size | Not specified | Not specified | Not specified |
| Working pressure | 10,000 psi (test) | Rated WP (test) | 15,000 psi (test) |
| Connector type | Hydraulic | Not specified | Not specified |

## Standardization Feasibility Assessment

### Equipment Categories

#### Category A: Direct Standardization Possible
1. **Personal Protective Equipment (PPE)**
   - Hard hat requirements consistent
   - Safety glasses consistent
   - Steel-toe boots consistent
   - Impact gloves: MARAWWAH only specifies

   **Recommendation:** Standardize to include impact-resistant gloves for all torquing operations

2. **Communication Equipment**
   - Radio requirements present in DANA and MARAWWAH

   **Recommendation:** Standardize two-way radio requirement for all crane operations

3. **Tag Lines**
   - All rigs mention tag lines

   **Recommendation:** Standardize to 4 tag lines (MARAWWAH specification)

#### Category B: Requires Modification
1. **Sling Configuration**
   - DANA: 4-point with 45° max angle
   - MARAWWAH: 4-point with 60° max angle

   **Recommendation:** Standardize to 45° maximum for additional safety margin

2. **Exclusion Zone Equipment**
   - DANA: 10m barriers
   - ALREEM: 8m barriers
   - MARAWWAH: 12m barriers

   **Recommendation:** Standardize to 12m for highest safety margin

#### Category C: Rig-Specific Equipment
1. **Crane Equipment**
   - Crane type varies by rig installation
   - Load charts are crane-specific

   **Recommendation:** Create rig-specific annexes with crane specifications

2. **BOP Equipment**
   - BOP specifications vary by well requirements
   - Test pressures vary by BOP rating

   **Recommendation:** Create equipment matrix for different BOP configurations

## Detailed Equipment Specifications for Standardized Procedure

### Required Lifting Equipment

| Item | Specification | Certification |
|------|--------------|---------------|
| Primary slings (4) | Minimum 1.5x BOP weight capacity | Annual certification |
| Backup slings (2) | Same as primary | Annual certification |
| Shackles (8) | Minimum 2x lift point load | Color-coded by capacity |
| Tag lines (4) | Minimum 15m length, 12mm diameter | Monthly inspection |

### Required Test Equipment

| Item | Specification | Calibration |
|------|--------------|-------------|
| Torque wrench (hydraulic) | Range to cover OEM requirements | 6-month calibration |
| Torque wrench (backup) | Same as primary | 6-month calibration |
| Pressure test unit | Rated to max test pressure + 10% | Annual calibration |
| Gap gauges | 0.002" to 0.010" range | Annual calibration |

### Required Safety Equipment

| Item | Specification | Inspection |
|------|--------------|------------|
| Exclusion barriers | Minimum 12m radius coverage | Pre-use check |
| Warning signs | Multilingual (English/Arabic) | Pre-use check |
| Wind meter | Digital, 0-100 knot range | Annual calibration |
| Radio sets | Intrinsically safe, same channel | Daily check |

## Cross-Rig Equipment Compatibility Matrix

| Equipment | DANA | ALREEM | MARAWWAH | Notes |
|-----------|------|--------|----------|-------|
| Standard slings | ✓ | ✓ | ✓ | Same capacity acceptable |
| Tag lines | ✓ | ✓ | ✓ | 4 required for all |
| Torque equipment | ✓ | ✓ | ✓ | Must cover OEM range |
| Test unit | ⚠ | ⚠ | ⚠ | Verify pressure rating |
| Barriers | ✓ | Needs upgrade | ✓ | ALREEM needs 12m |

## Equipment-Related Procedure Modifications

### Modifications Required for DANA
1. Update sling angle from 45° to allow up to 60° based on MARAWWAH practice (or reduce MARAWWAH to 45°)
2. Specify tag line count (currently states "minimum 2", standardize to 4)
3. Add wind meter requirement

### Modifications Required for ALREEM
1. Add sling angle specification (45° recommended)
2. Specify 4-point lift configuration
3. Upgrade exclusion zone barriers to 12m
4. Add calibration requirements for torque equipment
5. Add specific number of tag lines

### Modifications Required for MARAWWAH
1. None - current specifications exceed minimum requirements
2. Consider reducing sling angle from 60° to 45° for standardization

## Budget Impact Assessment

| Upgrade Item | Estimated Cost per Rig |
|--------------|----------------------|
| Additional tag lines (2 for DANA/ALREEM) | $500 |
| 12m exclusion barrier system | $2,000 |
| Wind meter (digital) | $300 |
| Gap gauge set | $200 |
| **Total per rig (average)** | **$3,000** |

## Recommendations Summary

1. **Immediate Equipment Standardization**
   - 4 tag lines minimum
   - 12m exclusion zone
   - Impact-resistant gloves for torquing

2. **Documentation Requirements**
   - Create equipment specifications annex
   - Define calibration schedules
   - Establish equipment tracking system

3. **Procurement Considerations**
   - Centralize sling purchasing for consistency
   - Maintain standardized spare equipment pool
   - Implement color-coding system (MARAWWAH model)
""",

    "agent5": """# Agent 5 – Standardized BOP Installation Procedure

## ADNOC Standard Operating Procedure
**Document:** SOP-BOP-001
**Title:** BOP Installation Procedure - Standardized
**Version:** 1.0
**Effective Date:** [Date]
**Review Date:** [Date + 1 year]

---

## 1. PURPOSE AND SCOPE

### 1.1 Purpose
This procedure establishes the standardized method for BOP installation across all ADNOC drilling rigs, ensuring consistent safety practices, operational efficiency, and regulatory compliance.

### 1.2 Scope
Applies to:
- All ADNOC-operated drilling rigs
- All BOP installation operations
- All personnel involved in BOP handling and installation

### 1.3 References
- ADNOC HSE Policy
- OEM Equipment Manuals
- API RP 53 - Blowout Prevention Equipment Systems
- IADC Drilling Safety Guidelines

---

## 2. RESPONSIBILITIES

| Role | Responsibilities |
|------|-----------------|
| **OIM/Rig Superintendent** | Overall authority; approves procedure execution |
| **Driller** | Supervises installation; controls descent rate |
| **Crane Operator** | Operates crane; maintains communication |
| **Tool Pusher** | Leads pre-job briefing; coordinates resources |
| **Floorhands (4)** | Tag line control; assist with connection |
| **Mechanic** | Torque operations; equipment verification |
| **HSE Advisor** | JSA review; safety oversight |

---

## 3. PRE-INSTALLATION REQUIREMENTS

### 3.1 Documentation
- [ ] Current JSA completed and reviewed with all personnel
- [ ] Pre-job briefing sign-off sheet completed
- [ ] Crane daily inspection completed
- [ ] Equipment certification records verified

### 3.2 Equipment Verification

| Equipment | Requirement | Verification |
|-----------|-------------|--------------|
| Slings (4) | Certified, 1.5x BOP weight capacity | Check certification tags |
| Shackles (8) | Certified, color-coded | Visual inspection |
| Tag lines (4) | Minimum 15m, 12mm diameter | Measure and inspect |
| Torque wrench | Calibrated within 6 months | Check calibration sticker |
| Wind meter | Calibrated, functional | Test reading |
| Radios (4) | Intrinsically safe, charged | Communications test |

### 3.3 Environmental Conditions
- **Maximum wind speed:** 25 knots
- **Visibility:** Minimum 100m
- **Wave height:** Per crane operating limits
- **Continuous monitoring required** throughout operation

### 3.4 Personnel Requirements
- Minimum crew: 8 persons
- All personnel must have attended:
  - BOP handling competency training
  - Rigging awareness course
  - Pre-job briefing for this specific operation

---

## 4. PROCEDURE

### Phase 1: Pre-Job Preparation

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 1.1 | Conduct toolbox talk with all personnel | Sign-off sheet | ✓ STAR |
| 1.2 | Review JSA and confirm understanding | Verbal confirmation | |
| 1.3 | Verify all equipment certifications | Checklist | |
| 1.4 | Check weather conditions (wind < 25 knots) | Wind meter reading | ✓ STAR |
| 1.5 | Test radio communication all parties | 3-way comm test | |
| 1.6 | Establish 12m exclusion zone with barriers | Visual confirmation | |
| 1.7 | Position emergency response equipment | Visual confirmation | |

**Checkpoint 1: Pre-job verification complete - Driller and Tool Pusher sign-off**

### Phase 2: BOP Rigging

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 2.1 | Inspect BOP for damage/contamination | Visual inspection | |
| 2.2 | Attach slings to certified lift points | 4-point configuration | ✓ STAR |
| 2.3 | Verify sling angles do not exceed 45° | Angle measurement | |
| 2.4 | Connect shackles - verify pin security | Independent check | |
| 2.5 | Attach tag lines (4) to designated points | Visual confirmation | |
| 2.6 | Clear exclusion zone - all non-essential personnel | Area sweep | |

**Checkpoint 2: Rigging verification complete - Crane Operator and Driller sign-off**

### Phase 3: BOP Lifting

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 3.1 | Signal crane operator: "Take up slack" | Radio confirmation | |
| 3.2 | Perform test lift: 300mm off deck | Height verification | ✓ STAR |
| 3.3 | **HOLD 5 MINUTES** - Inspect all connections | Timer + Inspection | ✓ STAR |
| 3.4 | Verify load stable, no swing | Visual observation | |
| 3.5 | Signal crane: "Continue lift" | Radio confirmation | |
| 3.6 | Maintain 3m minimum clearance from obstructions | Spotter verification | |
| 3.7 | Position tag line handlers at cardinal points | Visual confirmation | |

**Checkpoint 3: Lift verification complete - Crane Operator confirms stable load**

### Phase 4: BOP Positioning

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 4.1 | Guide BOP over wellhead using tag lines | Visual alignment | |
| 4.2 | Confirm BOP centered over wellhead | Driller confirmation | ✓ STAR |
| 4.3 | Begin descent - maximum 0.5m/min | Rate monitoring | |
| 4.4 | At 3m above wellhead: Reduce to 0.3m/min | Rate confirmation | ✓ STAR |
| 4.5 | Verbal confirmation before each descent | 3-way communication | |
| 4.6 | Align BOP studs with wellhead connector | Visual alignment | |

### Phase 5: BOP Landing and Securing

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 5.1 | Land BOP on wellhead connector | Contact confirmation | ✓ STAR |
| 5.2 | Verify proper seating - check gaps | Gap gauge (< 0.005") | |
| 5.3 | Engage hydraulic connector locks | Lock indicator | |
| 5.4 | Apply thread compound to studs | Uniform coverage | |
| 5.5 | Install studs hand-tight | All studs in place | |
| 5.6 | Torque studs - star pattern sequence | See Annex A | ✓ STAR |
| 5.7 | **Independent verification of torque values** | Second person check | ✓ STAR |
| 5.8 | Final gap measurement | Gap gauge record | |

**Checkpoint 4: Installation verification complete - Driller and Mechanic sign-off**

### Phase 6: Post-Installation Testing

| Step | Action | Verification | STAR Point |
|------|--------|--------------|------------|
| 6.1 | Function test all BOP rams | Operate full stroke | |
| 6.2 | Close blind rams | Visual confirmation | |
| 6.3 | Pressure test to rated working pressure | Pressure gauge | ✓ STAR |
| 6.4 | **HOLD PRESSURE 10 MINUTES** | Timer + pressure record | ✓ STAR |
| 6.5 | Verify no leaks | Visual inspection | |
| 6.6 | Release pressure - open rams | Pressure at zero | |
| 6.7 | Complete BOP test record | Documentation | |

**Checkpoint 5: Testing complete - OIM/Superintendent sign-off**

---

## 5. EMERGENCY PROCEDURES

### 5.1 Emergency Stop
**Any person can call STOP at any time without consequence**

| Trigger | Action |
|---------|--------|
| Equipment alarm | STOP - Hold load in position |
| Weather deterioration | STOP - Lower to safe position if able |
| Communication failure | STOP - Re-establish communication |
| Personnel in exclusion zone | STOP - Clear area |
| Load instability | STOP - Stabilize with tag lines |

### 5.2 Emergency Lowering
1. Signal "EMERGENCY LOWER" over radio
2. Crane operator: Lower at controlled rate to deck
3. Clear area - maintain exclusion zone
4. Do not release load until stable on deck
5. Notify OIM immediately
6. Complete incident report

### 5.3 Emergency Contacts
| Role | Extension |
|------|-----------|
| Medic | 2000 |
| OIM | 1001 |
| SIMOPS Coordinator | 1500 |
| Emergency Response Team | 9999 |

---

## 6. DOCUMENTATION REQUIREMENTS

### 6.1 Pre-Operation
- [ ] JSA review signatures
- [ ] Toolbox talk attendance record
- [ ] Equipment inspection checklist
- [ ] Crane inspection record

### 6.2 During Operation
- [ ] Weather log (every 30 minutes)
- [ ] Checkpoint sign-offs
- [ ] Torque value record

### 6.3 Post-Operation
- [ ] BOP function test record
- [ ] Pressure test record with chart
- [ ] Final completion sign-off
- [ ] Lessons learned (if applicable)

---

## 7. ANNEXES

### Annex A: Torque Sequence Diagram
```
Star Pattern Torquing:
        1
    8       2
  7           3
    6       4
        5

Sequence: 1-5-3-7-2-6-4-8
First pass: 50% torque
Second pass: 75% torque
Final pass: 100% torque (verify with calibrated wrench)
```

### Annex B: Equipment Specifications Matrix
| BOP Size | Test Pressure | Stud Torque | Gap Tolerance |
|----------|--------------|-------------|---------------|
| 13-5/8" 10K | 10,000 psi | Per OEM | 0.005" max |
| 13-5/8" 15K | 15,000 psi | Per OEM | 0.003" max |
| 18-3/4" 10K | 10,000 psi | Per OEM | 0.005" max |
| 18-3/4" 15K | 15,000 psi | Per OEM | 0.003" max |

### Annex C: Communication Protocol
- Primary: Channel 5 (Crane operations)
- Backup: Channel 12
- Emergency: Channel 16
- 3-way communication required for all lift commands

---

## 8. REVISION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | ADNOC Standards Team | Initial standardized procedure |

---

## 9. APPROVAL

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Prepared by | | | |
| Reviewed by | | | |
| Approved by | | | |

---

**Document Control:** This is a controlled document. Ensure you have the latest version before use.
"""
}


def simulate_agent_run(agent_name: str, agent_num: int, prompt_size: int) -> Dict[str, Any]:
    """Simulate an agent execution with realistic timing and token counts."""
    # Simulate processing time
    duration = 5.0 + (agent_num * 2.0)  # Agents take progressively longer
    time.sleep(min(duration, 3.0))  # Cap actual wait to 3 seconds for demo

    # Estimate token counts
    prompt_tokens = prompt_size // 4  # Rough estimate: 4 chars per token
    completion_tokens = len(DEMO_OUTPUTS.get(f"agent{agent_num}", "")) // 4

    return {
        "agent": agent_name,
        "backend": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "duration_seconds": round(duration, 2),
        "tokens_prompt": prompt_tokens,
        "tokens_completion": completion_tokens,
        "tokens_total": prompt_tokens + completion_tokens,
    }


def run_demo_workflow(operation: str, documents: Dict[str, str], output_dir: Path) -> None:
    """Run the demo workflow with simulated outputs."""

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_dir / operation / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("ADNOC BOP Standardization Workflow (Claude API Demo)")
    print(f"{'='*60}")
    print(f"Operation: {operation}")
    print(f"Output Directory: {run_dir}")
    print(f"{'='*60}\n")

    # Document summary
    doc_text = "\n".join(documents.values())
    print(f"Documents loaded: {len(documents)} document(s)")
    print(f"Total characters: {len(doc_text):,}\n")

    # Agent definitions
    agents = [
        ("agent1", "Comparison Analyst", "Comparing documents across rigs..."),
        ("agent2", "Gap Detector", "Analyzing gaps in procedures..."),
        ("agent3", "HP Evaluator", "Evaluating human performance factors..."),
        ("agent4", "Equipment Validator", "Validating equipment specifications..."),
        ("agent5", "Standardisation Writer", "Generating standardized procedure..."),
    ]

    # Track cumulative context for each agent
    previous_outputs = {}
    total_tokens = {"prompt": 0, "completion": 0, "total": 0}
    summary_data = {"agents": [], "total_duration_seconds": 0}

    # Run each agent
    for agent_key, agent_name, status_msg in agents:
        agent_num = int(agent_key[-1])

        print(f"[Agent {agent_num}/5] {agent_name}")
        print(f"  Status: {status_msg}")

        # Calculate prompt size (original docs + previous outputs)
        prompt_content = doc_text + "\n".join(previous_outputs.values())

        # Simulate agent execution
        meta = simulate_agent_run(agent_name, agent_num, len(prompt_content))

        # Get demo output
        output_content = DEMO_OUTPUTS.get(agent_key, f"# Agent {agent_num} Output\n\nNo output available.")

        # Save output
        output_file = run_dir / f"{agent_key}_{agent_name.lower().replace(' ', '_')}.md"
        output_file.write_text(output_content, encoding="utf-8")

        # Save metadata
        meta_file = run_dir / f"{agent_key}_{agent_name.lower().replace(' ', '_')}.meta.json"
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Update tracking
        previous_outputs[agent_key] = output_content
        total_tokens["prompt"] += meta["tokens_prompt"]
        total_tokens["completion"] += meta["tokens_completion"]
        total_tokens["total"] += meta["tokens_total"]
        summary_data["total_duration_seconds"] += meta["duration_seconds"]
        summary_data["agents"].append({
            "name": agent_name,
            "output_file": output_file.name,
            "meta": meta
        })

        print(f"  Duration: {meta['duration_seconds']:.1f}s")
        print(f"  Tokens: {meta['tokens_total']:,} (prompt: {meta['tokens_prompt']:,}, completion: {meta['tokens_completion']:,})")
        print(f"  Output: {output_file.name}")
        print()

    # Save summary
    summary_data["total_tokens"] = total_tokens
    summary_data["operation"] = operation
    summary_data["timestamp"] = timestamp
    summary_data["documents_processed"] = len(documents)

    summary_file = run_dir / "summary.json"
    summary_file.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")

    print(f"{'='*60}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"Total Duration: {summary_data['total_duration_seconds']:.1f}s")
    print(f"Total Tokens: {total_tokens['total']:,}")
    print(f"Output Directory: {run_dir}")
    print(f"\nFiles generated:")
    for f in sorted(run_dir.iterdir()):
        print(f"  - {f.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Run BOP standardization workflow demo with simulated Claude API responses.",
    )
    parser.add_argument(
        "--operation",
        default="BOP Installation",
        help="Operation name (default: 'BOP Installation')",
    )
    parser.add_argument(
        "--documents-file",
        default="production-data-bop-real.txt",
        help="Path to documents file (default: production-data-bop-real.txt)",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Base directory for outputs (default: outputs)",
    )
    args = parser.parse_args()

    # Load documents
    doc_path = Path(args.documents_file)
    if not doc_path.exists():
        # Try relative to script directory
        doc_path = Path(__file__).parent.parent / args.documents_file

    if not doc_path.exists():
        print(f"Error: Documents file not found: {args.documents_file}")
        sys.exit(1)

    documents = {"Combined BOP Documents": doc_path.read_text(encoding="utf-8")}

    # Run workflow
    output_dir = Path(args.output_dir)
    run_demo_workflow(args.operation, documents, output_dir)


if __name__ == "__main__":
    main()
