# Parameter Inconsistency Report (15 Sep 2026)

Run ID: `15Sep26_folders`
Reference files: `Reference Parameter_v1.0.xlsx`
Input files: `4G_ConfigurationData_15Sep26.xlsb`, `5G_ConfigurationData_15Sep26.xlsb`
Input Folder: `input`
Reference Folder: `reference`
Output Folder: `reports`

## 1. Overall Report

### 1.1 How many parameter inconsistencies from all reference sheets

| Reference File / Sheet | Network | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Auditable Inconsistency Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| NR Performance | 5G | 182 | 55 | 2 | 53 | 41 | 0 | 86 | 57.3% |
| NR Anchor | 4G | 74 | 24 | 3 | 21 | 44 | 0 | 6 | 35.3% |
| ALL FILES / SHEETS | ALL | 256 | 79 | 5 | 74 | 85 | 0 | 92 | 48.2% |

**Headline:** 79 of 256 reference parameters are inconsistent (5 full mismatch, 74 mixed/partial). 85 match the recommend value on all objects. 92 have no recommend value and were not audited. 0 could not be located in the configuration dumps.

### 1.2 Function-wise Summary for individual sheet

#### NR Performance

| Function | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Data Bearer | 1 | 0 | 0 | 0 | 0 | 0 | 1 | N/A |
| MIMO | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0% |
| Others | 175 | 52 | 2 | 50 | 38 | 0 | 85 | 57.8% |
| Reporting | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 100.0% |
| Scheduling | 3 | 2 | 0 | 2 | 1 | 0 | 0 | 66.7% |

#### NR Anchor

| Function | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| ANR | 14 | 2 | 0 | 2 | 11 | 0 | 1 | 15.4% |
| Blacklisting | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 100.0% |
| Counter | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.0% |
| Data Bearer | 2 | 0 | 0 | 0 | 1 | 0 | 1 | 0.0% |
| LTE CA+NR | 2 | 2 | 0 | 2 | 0 | 0 | 0 | 100.0% |
| NR Logo | 1 | 0 | 0 | 0 | 0 | 0 | 1 | N/A |
| NSA Anchoring | 26 | 13 | 3 | 10 | 11 | 0 | 2 | 54.2% |
| NSA VOLTE | 3 | 0 | 0 | 0 | 2 | 0 | 1 | 0.0% |
| Protocol | 6 | 3 | 0 | 3 | 3 | 0 | 0 | 50.0% |
| Reporting | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 100.0% |
| Retainability | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.0% |
| SCG Addition | 13 | 2 | 0 | 2 | 11 | 0 | 0 | 15.4% |
| SCG Release | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.0% |
| SCG Retain | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.0% |
| Secheduling | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0.0% |

### 1.3 Material inconsistencies

Parameters with 100% mismatch, or at least 10 mismatched objects:

| Sheet | Function | Parameter ID | Recommend | Status | Mismatch | Mismatch % | Actual (top) |
|---|---|---|---|---|---:|---|---|
| NR Anchor | NSA Anchoring | `NSADCPCCA4RSRPTHLD` | -115 | Inconsistent | 1679/1679 | 100.0% | 4G_ConfigurationData_15Sep26.xlsb: -128 (1679) |
| NR Performance | Others | `DL_SRS_CAP_BASED_BF_GAIN_SW@DLMCSSELALGOSW` | 1 | Inconsistent | 673/673 | 100.0% | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:DL_SRS_CAP_BASED_BF_GAIN_SW> (673) |
| NR Performance | Others | `NSA_CELL_SIB1_SW@ALGOCOMPATIBILITYSWITCHEXT` | 1 | Inconsistent | 673/673 | 100.0% | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:NSA_CELL_SIB1_SW> (673) |
| NR Anchor | NSA Anchoring | `DlArfcn` | N41 | Inconsistent | 195/195 | 100.0% | 4G_ConfigurationData_15Sep26.xlsb: 528990 (195) |
| NR Anchor | NSA Anchoring | `FrequencyBand` | NULL | Inconsistent | 195/195 | 100.0% | 4G_ConfigurationData_15Sep26.xlsb: N41 (195) |
| NR Anchor | Blacklisting | `BlacklistControlExtSwitch1@NSA_DC_SWITCH` | 0 | Mixed / Partial | 22/26 | 84.6% | 4G_ConfigurationData_15Sep26.xlsb: 1 (22) / 4G_ConfigurationData_15Sep26.xlsb: 0 (4) |
| NR Anchor | NSA Anchoring | `InterFreqHoA4TimeToTrig` | 640ms | Mixed / Partial | 3072/6946 | 44.2% | 4G_ConfigurationData_15Sep26.xlsb: 640ms (3874) / 4G_ConfigurationData_15Sep26.xlsb: 1024ms (3072) |
| NR Anchor | SCG Addition | `PERIODIC_SCG_ADD_OPT_SW@NsaDcAlgoExtSwitch` | 1 | Mixed / Partial | 1432/3473 | 41.2% | 4G_ConfigurationData_15Sep26.xlsb: 1 (2041) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1432) |
| NR Anchor | LTE CA+NR | `NsaDcLteScellActBfrLenThld` | 1 | Mixed / Partial | 830/3473 | 23.9% | 4G_ConfigurationData_15Sep26.xlsb: 1 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 0 (830) |
| NR Anchor | LTE CA+NR | `NsaDcLteScellActBfrDelThld` | 3 | Mixed / Partial | 830/3473 | 23.9% | 4G_ConfigurationData_15Sep26.xlsb: 3 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 5 (830) |
| NR Anchor | Protocol | `MBOCS_SW@NSADCUELTEFUNACTIVATIONSW` | 0 | Mixed / Partial | 830/3473 | 23.9% | 4G_ConfigurationData_15Sep26.xlsb: 0 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 1 (830) |
| NR Performance | Others | `DL_BIG_PKT_SRS_RES_ALLOC_SW@SRSALGOEXTSWITCH` | 1 | Mixed / Partial | 121/673 | 18.0% | 5G_ConfigurationData_15Sep26.xlsb: 1 (552) / 5G_ConfigurationData_15Sep26.xlsb: 0 (121) |
| NR Anchor | Reporting | `NrDataVolumeRptCfg` | 600 | Mixed / Partial | 540/3473 | 15.5% | 4G_ConfigurationData_15Sep26.xlsb: 600 (2933) / 4G_ConfigurationData_15Sep26.xlsb: 0 (540) |
| NR Anchor | NSA Anchoring | `SCGADDITIONBUFFERLENTHLD` | 10 | Mixed / Partial | 532/3473 | 15.3% | 4G_ConfigurationData_15Sep26.xlsb: 10 (2941) / 4G_ConfigurationData_15Sep26.xlsb: 0 (532) |
| NR Performance | Reporting | `NrDataVolumeRptCfg` | 600 | Mixed / Partial | 96/673 | 14.3% | 5G_ConfigurationData_15Sep26.xlsb: 600 (577) / 5G_ConfigurationData_15Sep26.xlsb: 0 (96) |
| NR Performance | Others | `SRS_RIM_INTRF_AVOID_SW@SRSALGOEXTSWITCH` | 1 | Mixed / Partial | 94/673 | 14.0% | 5G_ConfigurationData_15Sep26.xlsb: 1 (579) / 5G_ConfigurationData_15Sep26.xlsb: 0 (94) |
| NR Performance | Others | `LOW_SNR_CHN_DENOISE_SW@ADAPTIVEEDGEEXPENHSWITCH` | 0 | Mixed / Partial | 54/673 | 8.0% | 5G_ConfigurationData_15Sep26.xlsb: 0 (619) / 5G_ConfigurationData_15Sep26.xlsb: 1 (54) |
| NR Performance | Others | `DL_TD_MCS_ADJ_SW@DLLINKADAPTALGOSWITCH` | ON | Mixed / Partial | 34/673 | 5.1% | 5G_ConfigurationData_15Sep26.xlsb: 1 (639) / 5G_ConfigurationData_15Sep26.xlsb: 0 (34) |
| NR Performance | Others | `PDCCH_RES_ALLOC_ENH_SW@PDCCHALGOSWITCH` | 1 | Mixed / Partial | 31/673 | 4.6% | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| NR Performance | Others | `UE_PDCCH_SYM_NUM_ADAPT_SW@PDCCHALGOEXTSWITCH` | 0 | Mixed / Partial | 31/673 | 4.6% | 5G_ConfigurationData_15Sep26.xlsb: 0 (642) / 5G_ConfigurationData_15Sep26.xlsb: 1 (31) |
| NR Performance | Others | `PUCCH_MRC_IRC_SW@PUCCHRECEIVEENHSWITCH` | 1 | Mixed / Partial | 31/673 | 4.6% | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| NR Performance | Scheduling | `UlPreallocationSwitch@UL_SMART_PREALLOCATION_SWITCH` | 1 | Mixed / Partial | 18/673 | 2.7% | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| NR Performance | Others | `COVERAGESCENARIO` | SCENARIO_8 | Mixed / Partial | 17/673 | 2.5% | 5G_ConfigurationData_15Sep26.xlsb: SCENARIO_8 (656) / 5G_ConfigurationData_15Sep26.xlsb: EXPAND_SCENARIO_1 (17) |
| NR Performance | Others | `PscellA2RsrpThld` | -115 | Mixed / Partial | 13/673 | 1.9% | 5G_ConfigurationData_15Sep26.xlsb: -115 (660) / 5G_ConfigurationData_15Sep26.xlsb: -121 (9) / 5G_ConfigurationData_15Sep26.xlsb: -111 (4) |
| NR Anchor | NSA Anchoring | `SCGADDITIONINTERVAL` | 10 | Mixed / Partial | 20/3473 | 0.6% | 4G_ConfigurationData_15Sep26.xlsb: 10 (3453) / 4G_ConfigurationData_15Sep26.xlsb: 60 (20) |

## 2. All Parameter-wise Report (function wise)

Full line-by-line table is in `reports/runs/15Sep26_folders/Parameter_Inconsistency_Report.xlsx` sheet `2_All_Parameter_Report`.
Below: every parameter grouped by reference sheet and function.

### NR Anchor — ANR

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `EutranNcellDelPunNum` | ANR | 50 | Mixed / Partial | 239 | 1 | 4G_ConfigurationData_15Sep26.xlsb: 50 (239) / 4G_ConfigurationData_15Sep26.xlsb: 100 (1) |
| `NR_DELREDUNDANCENCELL@NrtDelMode` | ANR | ON | Mixed / Partial | 239 | 1 | 4G_ConfigurationData_15Sep26.xlsb: 1 (239) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `NcellDelPunishPeriod` | ANR | 10080 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 10080 (240) |
| `StaNumForIRatNRTDel` | ANR | 50 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 50 (240) |
| `StaPeriodForIRatNRTDel` | ANR | 1440 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1440 (240) |
| `NR_EVENT_ANR_SW@AnrFunctionSwitch` | CELLALGOSWITCH |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (1929) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1544) |
| `NsaDcPccAnchoringEventAnrSw@AnrSwitch` | ENodeBAlgoSwitch | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `LTE_NR_X2_SON_SETUP_SW@INTERFACESETUPPOLICYSW` | GLOBALPROCSWITCH | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `X2_SON_INTER_OP_SETUP_FBD_SW@INTERFACESETUPPOLICYSW` | GLOBALPROCSWITCH | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
| `X2_SON_SETUP_NO_NR_NRT_SW@InterfaceSetupPolicySw` | GLOBALPROCSWITCH | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `NR_COV_PCC_ANCHOR_ANR_OPT_SW@NsaDcAlgoSwitch` | NsaDcAlgoParam | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `DEL_NR_NCELL_CFG_SW` | X2BasedUptNcellCfgSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
| `MOD_NR_NCELL_CFG_SW` | X2BasedUptNcellCfgSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
| `UPT_NR_EXT_CELL_NW_OPT_CFG_SW` | X2BasedUptNcellCfgSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
### NR Anchor — Blacklisting

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `BlacklistControlExtSwitch1@NSA_DC_SWITCH` | UeCompat | 0 | Mixed / Partial | 4 | 22 | 4G_ConfigurationData_15Sep26.xlsb: 1 (22) / 4G_ConfigurationData_15Sep26.xlsb: 0 (4) |
### NR Anchor — Counter

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `SCG_REL_MEAS_OPT_SW@ENODEBCOUNTERALGOSWITCH` | ENODEBCOUNTERPARAGRP | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
### NR Anchor — Data Bearer

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NSADCDEFAULTBEARERMODE` | CELLQCIPARA |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: MCG_BEARER_EUTRA_PDCP (27730) / 4G_ConfigurationData_15Sep26.xlsb: SCG_SPLIT_BEARER (24365) |
| `NsaArpOverride` | CellRacThd | 0 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3473) |
### NR Anchor — LTE CA+NR

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NsaDcLteScellActBfrDelThld` | NsaDcMgmtConfig | 3 | Mixed / Partial | 2643 | 830 | 4G_ConfigurationData_15Sep26.xlsb: 3 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 5 (830) |
| `NsaDcLteScellActBfrLenThld` | NsaDcMgmtConfig | 1 | Mixed / Partial | 2643 | 830 | 4G_ConfigurationData_15Sep26.xlsb: 1 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 0 (830) |
### NR Anchor — NR Logo

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `UPPERLAYERINDICATIONSWITCH` | NSADCMGMTCONFIG |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: OFF (2081) / 4G_ConfigurationData_15Sep26.xlsb: ON (1392) |
### NR Anchor — NSA Anchoring

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NSADCUESELECTIONSTRATEGY` | CELLMLBUESEL | LTE_UE_PREFERRED | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: LTE_UE_PREFERRED (3467) / 4G_ConfigurationData_15Sep26.xlsb: LTE_NSA_DC_FAIR (6) |
| `InterFreqHoA4TimeToTrig` | InterFreqHoGroup | 640ms | Mixed / Partial | 3874 | 3072 | 4G_ConfigurationData_15Sep26.xlsb: 640ms (3874) / 4G_ConfigurationData_15Sep26.xlsb: 1024ms (3072) |
| `InterFreqHoA4TrigQuan` | IntraRatHoComm | RSRP  | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: RSRP (240) |
| `SMART_CARRIER_SELECTION_SW@MultiCarrierUnifiedSchSw` | MultiCarrUnifiedSch | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `IDLE_MODE_NSA_PCC_ANCHORING_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `IDLE_NSA_PCC_ANCHORING_OPT_SW@NSADCALGOEXTSWITCH` | NSADCMGMTCONFIG | 1 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3473) |
| `INSTANT_JUDGEMENT_SW@NSADCALGOEXTSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `NR_COV_PCC_ANCHORING_OPT_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 0 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3473) |
| `NSADCPCCANCHORA1RSRPTHLD` | NSADCMGMTCONFIG | 255 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 255 (3473) |
| `NSADCPCCANCHORINGPOLICY` | NSADCMGMTCONFIG | BASED_ON_NR_COVERAGE | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: BASED_ON_NR_COVERAGE (3467) / 4G_ConfigurationData_15Sep26.xlsb: DEFAULT (6) |
| `NSA_DC_CAPABILITY_SWITCH@NSADCALGOSWITCH` | NSADCMGMTCONFIG |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (1929) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1544) |
| `NSA_DC_COV_HO_ENH_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `NSA_DC_STATE_PCC_ANCHORING_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3473) |
| `NSA_DC_VOLUME_BASED_SCG_ADD_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 0 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3473) |
| `NSA_PCC_ANCHORING_SWITCH@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `PERIODIC_PCC_ANCHORING_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `SCGADDITIONBUFFERDELAYTHLD` | NSADCMGMTCONFIG | 5 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 5 (3473) |
| `SCGADDITIONBUFFERLENTHLD` | NSADCMGMTCONFIG | 10 | Mixed / Partial | 2941 | 532 | 4G_ConfigurationData_15Sep26.xlsb: 10 (2941) / 4G_ConfigurationData_15Sep26.xlsb: 0 (532) |
| `SCGADDITIONINTERVAL` | NSADCMGMTCONFIG | 10 | Mixed / Partial | 3453 | 20 | 4G_ConfigurationData_15Sep26.xlsb: 10 (3453) / 4G_ConfigurationData_15Sep26.xlsb: 60 (20) |
| `VOLUME_BASED_PCC_ANCHORING_SW@NSADCALGOEXTSWITCH` | NSADCMGMTCONFIG | 1 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3473) |
| `VOLUME_BASED_PERIODIC_TRIG_SW@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 1 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3473) |
| `NrNetworkingOption` | NrExternalCell | NSA | Consistent | 10764 | 0 | 4G_ConfigurationData_15Sep26.xlsb: NSA (10764) |
| `DlArfcn` | NrMfbiFreq | N41 | Inconsistent | 0 | 195 | 4G_ConfigurationData_15Sep26.xlsb: 528990 (195) |
| `FrequencyBand` | NrMfbiFreq | NULL | Inconsistent | 0 | 195 | 4G_ConfigurationData_15Sep26.xlsb: N41 (195) |
| `NSADCPCCA4RSRPTHLD` | PCCFREQCFG | -115 | Inconsistent | 0 | 1679 | 4G_ConfigurationData_15Sep26.xlsb: -128 (1679) |
| `NSAPCCANCHORINGPRIORITY` | PCCFREQCFG |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (912) / 4G_ConfigurationData_15Sep26.xlsb: 5 (240) / 4G_ConfigurationData_15Sep26.xlsb: 2 (240) / 4G_ConfigurationData_15Sep26.xlsb: 4 (239) / 4G_ConfigurationData_15Sep26.xlsb: 1 (48) |
### NR Anchor — NSA VOLTE

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `QCI_REL_BASED_PCC_ANCHORING_SW@NsaDcOptSwitch` | CellQciPara |  | No Recommend Value | 0 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (46611) / 4G_ConfigurationData_15Sep26.xlsb: 1 (5484) |
| `QCI_VOLTE_SCG_COEXIST_SW@NsaDcOptSwitch` | CellQciPara | 0 | Consistent | 52095 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (52095) |
| `VolteUeScgMgmtStrategy` | NsaDcMgmtConfig | VOLTE_PREFERRED | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: VOLTE_PREFERRED (3473) |
### NR Anchor — Protocol

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `LNRCOMEASLTEMEASDURATION` | NSADCALGOPARAM | 2 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 2 (240) |
| `COV_BASED_DIRECTIONAL_HO_SW@NSADCUELTEFUNACTIVATIONSW` | NSADCMGMTCONFIG | 0 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 1 (6) |
| `FREQ_PRI_HO_SW@NSADCUELTEFUNACTIVATIONSW` | NSADCMGMTCONFIG | 0 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 1 (6) |
| `MBOCS_SW@NSADCUELTEFUNACTIVATIONSW` | NSADCMGMTCONFIG | 0 | Mixed / Partial | 2643 | 830 | 4G_ConfigurationData_15Sep26.xlsb: 0 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 1 (830) |
| `SPCT_COORD_INTER_FREQ_HO_SW@NSADCUELTEFUNACTIVATIONSW` | NSADCMGMTCONFIG | 1 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3473) |
| `NsaS1ProcConflCompatPolicy` | NsaDcAlgoParam | RETRANSMIT | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: RETRANSMIT (240) |
### NR Anchor — Reporting

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NrDataVolumeRptCfg` | NsaDcMgmtConfig | 600 | Mixed / Partial | 2933 | 540 | 4G_ConfigurationData_15Sep26.xlsb: 600 (2933) / 4G_ConfigurationData_15Sep26.xlsb: 0 (540) |
### NR Anchor — Retainability

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `ProtocolCompatibilityExtSw@RRC_REEST_FULL_CONFIG_SW` | EnodebAlgoExtSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
### NR Anchor — SCG Addition

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `ProtocolCompatibilitySw@LteNrCapbParallelQuerySw` | GlobalProcSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
| `ProtocolCompatibilitySw@NrB1MeasOptSw` | GlobalProcSwitch | 0 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (240) |
| `ProtocolCompatibilitySw@NrCapabilityParallelQuerySw` | GlobalProcSwitch | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `BLINDCONFIGINDICATOR` | NRNRELATIONSHIP | False | Consistent | 40529 | 0 | 4G_ConfigurationData_15Sep26.xlsb: FALSE (40529) |
| `NRB1REPORTWAITINGTIMER` | NRSCGFREQCONFIG | 3 | Consistent | 1678 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 3 (1678) |
| `NRB1TIMETOTRIGGER` | NRSCGFREQCONFIG | 40MS | Consistent | 1678 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 40MS (1678) |
| `NSADCB1THLDRSRP` | NRSCGFREQCONFIG | -110 | Consistent | 1678 | 0 | 4G_ConfigurationData_15Sep26.xlsb: -110 (1678) |
| `SCGDLARFCNPRIORITY` | NRSCGFREQCONFIG | 7 | Consistent | 1678 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 7 (1678) |
| `NSADCSCGADDITIONPOLICY` | NSADCMGMTCONFIG | HIGHEST_PRIORITY_FREQ | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: HIGHEST_PRIORITY_FREQ (3473) |
| `NSA_BLIND_SCG_ADDITION_SWITCH@NSADCALGOSWITCH` | NSADCMGMTCONFIG | 0 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3473) |
| `SCGADDPENALTYPERIODCOUNT` | NSADCMGMTCONFIG | 0 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3473) |
| `SCG_ADD_PCC_ANCHOR_VOL_OPT_SW@NSADCALGOEXTSWITCH` | NSADCMGMTCONFIG | 1 | Mixed / Partial | 3467 | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| `PERIODIC_SCG_ADD_OPT_SW@NsaDcAlgoExtSwitch` | NsaDcMgmtConfig | 1 | Mixed / Partial | 2041 | 1432 | 4G_ConfigurationData_15Sep26.xlsb: 1 (2041) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1432) |
### NR Anchor — SCG Release

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NRSCGINACTIVITYRELSTRATEGY` | ENODEBALGOEXTSWITCH | REL_UPON_LTE_INACTVTY_TMR_EXPN | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: REL_UPON_LTE_INACTVTY_TMR_EXPN (240) |
### NR Anchor — SCG Retain

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `FULL_CONFIG_FOR_SCG_FAIL_SW@NSADCALGOSWITCH` | NSADCALGOPARAM | 1 | Consistent | 240 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 1 (240) |
### NR Anchor — Secheduling

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `MCGHIGHLOADTHRESHOLD` | CELLDLSCHALGO | 100 | Consistent | 3473 | 0 | 4G_ConfigurationData_15Sep26.xlsb: 100 (3473) |
### NR Performance — Data Bearer

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `DLDATAPDCPSPLITMODE` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: SCG_ONLY (4560) / 5G_ConfigurationData_15Sep26.xlsb: SCG_AND_MCG (240) |
### NR Performance — MIMO

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `DL_PMI_SRS_ADAPT_SW@ADAPTIVEEDGEEXPENHSWITCH` | NRDUCELLALGOSWITCH | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `SrsPreSinrJudgeThld` | NRDUCellPdsch | -100 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: -100 (673) |
### NR Performance — Others

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `ABNUEULDATAERRORJUDGETHLD` | GNBOAMPARAM | 5 | Mixed / Partial | 239 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 5 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DLPDCPDISCARDTIMER` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: MS150 (1920) / 5G_ConfigurationData_15Sep26.xlsb: MS300 (1200) / 5G_ConfigurationData_15Sep26.xlsb: INFINITY (1200) / 5G_ConfigurationData_15Sep26.xlsb: MS50 (480) |
| `DLPDCPSNSIZE` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: BITS18 (2640) / 5G_ConfigurationData_15Sep26.xlsb: BITS12 (2160) |
| `GNBPDCPREORDERINGTIMER` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: MS15 (1200) / 5G_ConfigurationData_15Sep26.xlsb: MS50 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS180 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS200 (480) / 5G_ConfigurationData_15Sep26.xlsb: MS20 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS1500 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS300 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS500 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS100 (240) |
| `UEPDCPREORDERINGTIMER` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: MS15 (1200) / 5G_ConfigurationData_15Sep26.xlsb: MS50 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS180 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS200 (480) / 5G_ConfigurationData_15Sep26.xlsb: MS20 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS1500 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS300 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS500 (240) / 5G_ConfigurationData_15Sep26.xlsb: MS100 (240) |
| `ULDATASPLITPRIMARYPATH` | GNBPDCPPARAMGROUP | SCG | Consistent | 4800 | 0 | 5G_ConfigurationData_15Sep26.xlsb: SCG (4800) |
| `ULDATASPLITTHRESHOLD` | GNBPDCPPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: INFINITY (4560) / 5G_ConfigurationData_15Sep26.xlsb: BYTE1600 (211) / 5G_ConfigurationData_15Sep26.xlsb: BYTE204800 (10) / 5G_ConfigurationData_15Sep26.xlsb: BYTE51200 (10) / 5G_ConfigurationData_15Sep26.xlsb: BYTE102400 (9) |
| `RLCMODE` | GNBRLCPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: AM (2400) / 5G_ConfigurationData_15Sep26.xlsb: UM (1200) |
| `UEAMSTATUSRPTPROHIBITTMR` | GNBRLCPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: <EMPTY> (1200) / 5G_ConfigurationData_15Sep26.xlsb: MS40 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS15 (960) / 5G_ConfigurationData_15Sep26.xlsb: MS0 (480) |
| `UERLCREASSEMBLYTIMER` | GNBRLCPARAMGROUP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: MS15 (1920) / 5G_ConfigurationData_15Sep26.xlsb: MS40 (1680) |
| `X2SON_SETUP_SWITCH@X2SONCONFIGSWITCH` | GNBX2SONCONFIG | 1 | Consistent | 240 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (240) |
| `INTRASITEMAXX2TRANSRATE` | GNODEBPARAM | 5 | Consistent | 240 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 5 (240) |
| `MAXX2TRANSRATE` | GNODEBPARAM | 4 | Consistent | 240 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 4 (240) |
| `PDCP_SN_ABN_FULL_CONFIG_SW@COMPATIBILITYALGOSWITCH` | GNODEBPARAM | 1 | Mixed / Partial | 239 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `UL_PDCP_SN_ABN_COMPT_OPT_SW@COMPATIBILITYALGOSWITCH` | GNODEBPARAM | 1 | Mixed / Partial | 239 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `AUTO_NR_FREQ_RELATION_SW@AnrSwitch` | NRCELLALGOSWITCH | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `NR_NR_ANR_AUTO_NO_HO_SW@AnrSwitch` | NRCELLALGOSWITCH | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `NR_NR_ANR_SW@AnrSwitch` | NRCELLALGOSWITCH | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `NR_NR_FAST_ANR_SW@AnrSwitch` | NRCELLALGOSWITCH | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `NSADCSWITCH` | NRCELLALGOSWITCH | ON | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ON (673) |
| `AutoDelNCellPenaltyNum` | NRCELLANR | 50 | Mixed / Partial | 666 | 7 | 5G_ConfigurationData_15Sep26.xlsb: 50 (666) / 5G_ConfigurationData_15Sep26.xlsb: 1 (7) |
| `AutoDelNCellPenaltyPeriod` | NRCELLANR | 10080 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10080 (673) |
| `N2NNoHoConsecPrdThld` | NRCELLANR | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `N2NNoHoSuccRateThld` | NRCELLANR | 80 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 80 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `NR_NR_ANR_NO_HO_AUTO_RES_SW@AnrAlgoSwitch` | NRCELLANR | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `NrNCellHoNumThld` | NRCELLANR | 100 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 100 (673) |
| `NrNCellNoHoResIntvl` | NRCELLANR | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 30 (3) |
| `PeriodForDelNrt` | NRCELLANR | 7 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 7 (673) |
| `PscellA2RsrpThld` | NRCELLNSADCCONFIG | -115 | Mixed / Partial | 660 | 13 | 5G_ConfigurationData_15Sep26.xlsb: -115 (660) / 5G_ConfigurationData_15Sep26.xlsb: -121 (9) / 5G_ConfigurationData_15Sep26.xlsb: -111 (4) |
| `UL_FALLBACK_TO_LTE_SWITCH@NSADCALGOSWITCH` | NRCELLNSADCCONFIG | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `RLCMODE` | NRCELLQCIBEARER |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: UM (5990) / 5G_ConfigurationData_15Sep26.xlsb: AM (5317) |
| `NR_NR_ANR_DEL_SW@AnrSwitch` | NRCellAlgoSwitch | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `DLSUPREDICTERRORUPPERLIMIT` | NRDUCELLAIALGO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 5 (673) |
| `DL_SU_MCS_INTEL_OPT_SW@AIAMCALGOSWITCH` | NRDUCELLAIALGO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL256QAMSWITCH` | NRDUCELLALGOSWITCH | ON | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ON (673) |
| `DL_MU_MIMO_SW@MUMIMOSWITCH` | NRDUCELLALGOSWITCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `DL_SU_MULTI_LAYER_PWR_CTRL_SW@SUMIMOMULTIPLELAYERSW` | NRDUCELLALGOSWITCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_SU_MULTI_LAYER_SW@SUMIMOMULTIPLELAYERSW` | NRDUCELLALGOSWITCH | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DL_SU_PREDICT_MOBILITY_ENH_SW@SUMIMOMULTIPLELAYERSW` | NRDUCELLALGOSWITCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_SU_PWR_CTRL_ENH_SW@SUMIMOMULTIPLELAYERSW` | NRDUCELLALGOSWITCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `LOW_SNR_CHN_DENOISE_SW@ADAPTIVEEDGEEXPENHSWITCH` | NRDUCELLALGOSWITCH | 0 | Mixed / Partial | 619 | 54 | 5G_ConfigurationData_15Sep26.xlsb: 0 (619) / 5G_ConfigurationData_15Sep26.xlsb: 1 (54) |
| `NSA_CELL_SIB1_SW@ALGOCOMPATIBILITYSWITCHEXT` | NRDUCELLALGOSWITCH | 1 | Inconsistent | 0 | 673 | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:NSA_CELL_SIB1_SW> (673) |
| `PDCCH_MU_SW@MUMIMOSWITCH` | NRDUCELLALGOSWITCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `PUSCH_BEAM_DOMAIN_ENH_SW@FULLCHANNELCOVENHSWITCH` | NRDUCELLALGOSWITCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `PUSCH_TIME_DOMAIN_ENH_SW@FULLCHANNELCOVENHSWITCH` | NRDUCELLALGOSWITCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `UL256QAMSWITCH` | NRDUCELLALGOSWITCH | UL_256QAM_FIXED | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: UL_256QAM_FIXED (673) |
| `UL_MU_MIMO_SW@MUMIMOSWITCH` | NRDUCELLALGOSWITCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `UL_SU_MULTI_LAYER_SW@SUMIMOMULTIPLELAYERSW` | NRDUCELLALGOSWITCH | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DMRS_PWR_ADAPT_SW@ChnPwrAlgoSwitch` | NRDUCELLCHNPWR | 1 | Mixed / Partial | 664 | 9 | 5G_ConfigurationData_15Sep26.xlsb: 1 (664) / 5G_ConfigurationData_15Sep26.xlsb: 0 (9) |
| `COMMONCTRLRESRBNUM` | NRDUCELLCORESET |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: RB96 (572) / 5G_ConfigurationData_15Sep26.xlsb: RB48 (99) / 5G_ConfigurationData_15Sep26.xlsb: RB24 (2) |
| `CSIPERIOD` | NRDUCELLCSIRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: SLOT40 (656) / 5G_ConfigurationData_15Sep26.xlsb: SLOT10 (17) |
| `CSIRSBEAMTYPE` | NRDUCELLCSIRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: TYPE0 (673) |
| `CSIRSCELLRESOURCENUM` | NRDUCELLCSIRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: FD_RESOURCE (672) / 5G_ConfigurationData_15Sep26.xlsb: 4_RESOURCE (1) |
| `CSIRS_INTRF_STATIC_AVOID_SW@CSISWITCH` | NRDUCELLCSIRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `CSIUSERPERIOD` | NRDUCELLCSIRS | SLOT40 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: SLOT40 (673) |
| `NCELLCSIRSINTRFAVOID` | NRDUCELLCSIRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: P_CELL (655) / 5G_ConfigurationData_15Sep26.xlsb: NO_AVOID (18) |
| `TRSPERIOD` | NRDUCELLCSIRS | MS20 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: MS20 (673) |
| `DLMUMIMOSIRSCALEFACTOR` | NRDUCELLDLAMC |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `DL_MCS_ADJ_OPT_SW@DLAMCALGOSW` | NRDUCELLDLAMC |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `DL_MCS_ADJ_OPT_WT_CHANGE_SW@DLMCSSELALGOSW` | NRDUCELLDLAMC | 1 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| `DL_SRS_CAP_BASED_BF_GAIN_SW@DLMCSSELALGOSW` | NRDUCELLDLAMC | 1 | Inconsistent | 0 | 673 | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:DL_SRS_CAP_BASED_BF_GAIN_SW> (673) |
| `DLMUBACKTOSUSETHLD` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 5 (673) |
| `DLMUMIMOSRSPRESINRTHLD` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: -50 (673) |
| `DLMUPMIBEAMNUMTHLD` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 3 (673) |
| `DLMUPRBUSAGETHLD` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `DL_MCS_TABLE_ADAPT_ENH_SW@DLMUMIMOSCHSUPPLEMENTSW` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_SE_SU_MU_MIMO_ADAPT_SW@DLMUMIMOSCHSUPPLEMENTSW` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DL_SMALL_PACKET_MERGE_SW@DLMUMIMOSCHSUPPLEMENTSW` | NRDUCELLDLMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DLPMIMUMIMORANK` | NRDUCELLDLRANK |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: RANK_2 (673) |
| `DLRANK2INCSPCTEFFTHLD` | NRDUCELLDLRANK | 95 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 95 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| `DLRANK3DECSPCTEFFTHLD` | NRDUCELLDLRANK | 150 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 150 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| `DLRANK3INCSPCTEFFTHLD` | NRDUCELLDLRANK | 95 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 95 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| `DLRANK4DECSPCTEFFTHLD` | NRDUCELLDLRANK | 150 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 150 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| `DLRANKADAPTLAYERGAPTHLD` | NRDUCELLDLRANK | 13 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 13 (672) / 5G_ConfigurationData_15Sep26.xlsb: 15 (1) |
| `DLRANKADAPTMCSTHLD` | NRDUCELLDLRANK | 8 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 8 (672) / 5G_ConfigurationData_15Sep26.xlsb: 9 (1) |
| `DLRANKADAPTSPCTEFFCOEFF` | NRDUCELLDLRANK | 14 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 14 (672) / 5G_ConfigurationData_15Sep26.xlsb: 8 (1) |
| `DLRANKDETECTCORRTHLD` | NRDUCELLDLRANK | 80 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 80 (673) |
| `DLSRSMUMIMORANK` | NRDUCELLDLRANK |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: RANK_2 (673) |
| `DLSRSMUMIMORANKMODE` | NRDUCELLDLRANK |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: RI_BASED_MU_RANK (619) / 5G_ConfigurationData_15Sep26.xlsb: ENHANCE_MU_RANK (54) |
| `RANK_AND_SINR_ESTIMATE_OPT_SW@DLRANKSELALGOSW` | NRDUCELLDLRANK |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_RETRANS_PRECISE_RB_CTRL_SW@DLSCHALGOSWITCH` | NRDUCELLDLSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_RLC_STATUS_RPT_AWARE_SCH_SW@DLSCHALGOSWITCH` | NRDUCELLDLSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DL_SLOT_AWARE_SCH_SW@DLSCHALGOSWITCH` | NRDUCELLDLSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `HEAVY_LOAD_SCH_PRI_OPT_SW@DLSCHALGOSWITCH` | NRDUCELLDLSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DLMUESTRBPOLICY` | NRDUCELLDMRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: PSEUDOORTHOG_DMRS_ADAPT_DEDUCT (673) |
| `AHR_EXP_TURBO_PHASE2_SW@AHRSWITCH` | NRDUCELLFEATURESW |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `AHR_PHASE1_SW@AHRSWITCH` | NRDUCELLFEATURESW |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `MAXPAIRLAYERNUM` | NRDUCELLPDCCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: LAYER_2 (673) |
| `OCCUPIEDRBNUM` | NRDUCELLPDCCH | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `OCCUPIEDSYMBOLNUM` | NRDUCELLPDCCH | 2SYM | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 2SYM (673) |
| `PDCCH_AGG_LVL_OPT_SW@PDCCHALGOENHSWITCH` | NRDUCELLPDCCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `PDCCH_RES_ALLOC_ENH_SW@PDCCHALGOSWITCH` | NRDUCELLPDCCH | 1 | Mixed / Partial | 642 | 31 | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| `UE_PDCCH_SYM_NUM_ADAPT_SW@PDCCHALGOEXTSWITCH` | NRDUCELLPDCCH | 0 | Mixed / Partial | 642 | 31 | 5G_ConfigurationData_15Sep26.xlsb: 0 (642) / 5G_ConfigurationData_15Sep26.xlsb: 1 (31) |
| `PDCCHEDGEPWRCTRLPOLICY` | NRDUCELLPDCCHALGO | BASED_ON_CSI_RPT | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: BASED_ON_CSI_RPT (672) / 5G_ConfigurationData_15Sep26.xlsb: BASED_ON_AGG_LVL (1) |
| `PDCCHMAXAGGLEVEL` | NRDUCELLPDCCHALGO | AGG_LVL_8_16_ADAPT | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: AGG_LVL_8_16_ADAPT (672) / 5G_ConfigurationData_15Sep26.xlsb: AGG_LVL_16 (1) |
| `PDCCHPRECODEENHPOLICY` | NRDUCELLPDCCHALGO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ENH_PMI (672) / 5G_ConfigurationData_15Sep26.xlsb: ENH_OFF (1) |
| `CCE_BASED_SU_PDSCH_BAL_SCH_SW@DLPDSCHALGOSWITCH` | NRDUCELLPDSCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `CSIRS_RATEMATCH_SW@RATEMATCHSWITCH` | NRDUCELLPDSCH | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DLADDITIONALDMRSPOS` | NRDUCELLPDSCH | POS1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: POS1 (673) |
| `DLDELAYSCHBUFFERTHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `DLDMRSCONFIGTYPE` | NRDUCELLPDSCH | TYPE2 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: TYPE2 (673) |
| `DLDMRSMAXLENGTH` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 2SYMBOL (673) |
| `DLINITIALMCSADJVALUE` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (672) / 5G_ConfigurationData_15Sep26.xlsb: -4 (1) |
| `DLINITMCS` | NRDUCELLPDSCH | 4 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 4 (673) |
| `DLINITRANK` | NRDUCELLPDSCH | RANK1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: RANK1 (673) |
| `DLLOWTIMECORRMUSW` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ON (672) / 5G_ConfigurationData_15Sep26.xlsb: OFF (1) |
| `DLMIMOMCSOPTPOLICY` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: OFF (673) |
| `DLMUGATHEROPTSW` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: OFF (619) / 5G_ConfigurationData_15Sep26.xlsb: ON (54) |
| `DLMUINITIALMCSADJVALUE` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: -2 (672) / 5G_ConfigurationData_15Sep26.xlsb: -4 (1) |
| `DLMUMIMOGROUPMODE` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ISOLATION_CORRELATION (673) |
| `DLPMIMUMIMOSPACEISOTHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 140 (673) |
| `DLSCHOPTTIMETHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 300 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DLSRSMUMIMOCHANISOTHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 30 (673) |
| `DLSRSMUMIMOFREQSELTHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10 (673) |
| `DLSRSMUMIMOSPACEISOTHLD` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 50 (673) |
| `DLTARGETIBLER` | NRDUCELLPDSCH | 10 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10 (673) |
| `DL_INIT_MCS_ADJ_SW@DLLINKADAPTALGOSWITCH` | NRDUCELLPDSCH | 1 | Mixed / Partial | 669 | 4 | 5G_ConfigurationData_15Sep26.xlsb: 1 (669) / 5G_ConfigurationData_15Sep26.xlsb: 0 (4) |
| `DL_TD_MCS_ADJ_SW@DLLINKADAPTALGOSWITCH` | NRDUCELLPDSCH | ON | Mixed / Partial | 639 | 34 | 5G_ConfigurationData_15Sep26.xlsb: 1 (639) / 5G_ConfigurationData_15Sep26.xlsb: 0 (34) |
| `FIXEDAMCSTEPVALUE` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 40 (672) / 5G_ConfigurationData_15Sep26.xlsb: 20 (1) |
| `FIXEDWEIGHTTYPE` | NRDUCELLPDSCH | SRS_WEIGHT | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: SRS_WEIGHT (673) |
| `MAXMIMOLAYERNUM` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: LAYER_16 (652) / 5G_ConfigurationData_15Sep26.xlsb: LAYER_DEFAULT (21) |
| `PDCCH_RATEMATCH_SW@RATEMATCHSWITCH` | NRDUCELLPDSCH | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `SSB_RATEMATCH_SW@RATEMATCHSWITCH` | NRDUCELLPDSCH | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `TAIL_PKT_SCH_OPT_SW@DLPDSCHALGOSWITCH` | NRDUCELLPDSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `TRS_RATEMATCH_SW@RATEMATCHSWITCH` | NRDUCELLPDSCH | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `SRSPRECODEUPTDELAYREDUPOL` | NRDUCELLPDSCHPRECODE |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: ALL (555) / 5G_ConfigurationData_15Sep26.xlsb: OFF (118) |
| `HARQ_ACK_RES_SET0_SCH_OPT_SW@PUCCHPERFORMANCESW` | NRDUCELLPUCCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `PUCCH_MRC_IRC_SW@PUCCHRECEIVEENHSWITCH` | NRDUCELLPUCCH | 1 | Mixed / Partial | 642 | 31 | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| `DCI_EXTEND_UL_CONGEST_SW@ULPUSCHALGOSWITCH` | NRDUCELLPUSCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `MAXMIMOLAYERCNT` | NRDUCELLPUSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: LAYER_8 (588) / 5G_ConfigurationData_15Sep26.xlsb: LAYER_4 (67) / 5G_ConfigurationData_15Sep26.xlsb: LAYER_2 (18) |
| `PUSCHSHAREPUCCHRESPOL` | NRDUCELLPUSCH | FULLY_SHARED_TIGHT_CONTROL | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: FULLY_SHARED_TIGHT_CONTROL (672) / 5G_ConfigurationData_15Sep26.xlsb: NOT_SHARED (1) |
| `PUSCH_SHR_PRACH_FREQ_RES_SW@ULPUSCHALGOSWITCH` | NRDUCELLPUSCH | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `ULADDITIONALDMRSPOS` | NRDUCELLPUSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: POS1 (673) |
| `ULTARGETIBLER` | NRDUCELLPUSCH | 10 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10 (673) |
| `UL_INTRF_RANDOMIZED_SCH_ENH_SW@ULPUSCHALGOSWITCH` | NRDUCELLPUSCH |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `UEINACTIVITYTIMER` | NRDUCELLQCIBEARER |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 10 (11307) |
| `EXP_BASED_MM_ADAPT_SCH_SW@SERVICEEXPALGOSWITCH` | NRDUCELLSERVEXP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `FULLBUFFERUEULPRBUSAGETHLD` | NRDUCELLSERVEXP | 50 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 50 (672) / 5G_ConfigurationData_15Sep26.xlsb: 30 (1) |
| `RES_BASED_MM_ADAPT_SCH_SW@SERVICEEXPALGOSWITCH` | NRDUCELLSERVEXP |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |
| `BEAM_SPECIFIC_SRS_DENOISE_SW@SRSDETECTIONALGOSWITCH` | NRDUCELLSRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (565) / 5G_ConfigurationData_15Sep26.xlsb: 0 (108) |
| `DL_BIG_PKT_SRS_RES_ALLOC_SW@SRSALGOEXTSWITCH` | NRDUCELLSRS | 1 | Mixed / Partial | 552 | 121 | 5G_ConfigurationData_15Sep26.xlsb: 1 (552) / 5G_ConfigurationData_15Sep26.xlsb: 0 (121) |
| `SRS_INTRF_COORD_S_SLOT_SW@SRSALGOEXTSWITCH` | NRDUCELLSRS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `SRS_PERIOD_ADAPT_SW@SRSALGOSWITCH` | NRDUCELLSRS | 0 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 0 (673) |
| `SRS_RIM_INTRF_AVOID_SW@SRSALGOEXTSWITCH` | NRDUCELLSRS | 1 | Mixed / Partial | 579 | 94 | 5G_ConfigurationData_15Sep26.xlsb: 1 (579) / 5G_ConfigurationData_15Sep26.xlsb: 0 (94) |
| `USER_CHARACTER_SRS_ADAPT_SW@SRSALGOSWITCH` | NRDUCELLSRS | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `NSAULFACKTOLTESINRHYST` | NRDUCELLSRSMEAS | 30 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 30 (673) |
| `NSAULFACKTOLTESINRTHLD` | NRDUCELLSRSMEAS | 110 | Mixed / Partial | 668 | 5 | 5G_ConfigurationData_15Sep26.xlsb: 110 (668) / 5G_ConfigurationData_15Sep26.xlsb: 30 (5) |
| `SRSINTRFTHLD` | NRDUCELLSRSMEAS |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 5 (673) |
| `SRS_CORRECTION_BASED_ON_PHR_SW@NSAULFBTOLTESINROPTSW` | NRDUCELLSRSMEAS | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `SRS_EQUALIZATION_SW@NSAULFBTOLTESINROPTSW` | NRDUCELLSRSMEAS | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `ULSRSMEASUSAGESWITCH` | NRDUCELLSRSMEAS | DTX_DETECT | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: DTX_DETECT (672) / 5G_ConfigurationData_15Sep26.xlsb: OFF (1) |
| `COVERAGESCENARIO` | NRDUCELLTRPBEAM | SCENARIO_8 | Mixed / Partial | 656 | 17 | 5G_ConfigurationData_15Sep26.xlsb: SCENARIO_8 (656) / 5G_ConfigurationData_15Sep26.xlsb: EXPAND_SCENARIO_1 (17) |
| `MU_AMC_OPT_SW@ULAMCALGOSW` | NRDUCELLULAMC |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `UL_SCH_AVG_SINR_OPT_SW@ULAMCALGOSW` | NRDUCELLULAMC | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `ALIGNPAIRBIGPKTRBREDRATIO` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 50 (673) |
| `ALIGNPAIRBIGSMLPKTRBTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 20 (673) |
| `ALIGNPAIRSMLPKTRBEXTRATIO` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 200 (673) |
| `BIG_PKT_ALIGN_PAIR_OPT_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `BIG_PKT_UE_FREQ_SEL_SCH_OPT_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `DIFF_FLDMRS_MAX_LENGTH_PAIR_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `MUFREQSELSCHRBRATIOTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 40 (673) |
| `MURBRATIOTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 40 (673) |
| `MU_BEAM_PAIR_OPT_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `MU_MULTI_SLOT_PAIR_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `SML_PKT_ALIGN_PAIR_OPT_SW@ULMUMIMOALGOSWITCH` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `ULMUGATHEROPTGAINTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 100 (673) |
| `ULMUMIMOCORRTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 9 (673) |
| `ULMUMIMOSINRTHLD` | NRDUCELLULMIMO |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: -20 (673) |
| `INTRFUESRSPCMINSINRTARGET` | NRDUCELLULPCCONFIG |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 50 (672) / 5G_ConfigurationData_15Sep26.xlsb: 10 (1) |
| `MAXSRSPOADJUSTAMOUNT` | NRDUCELLULPCCONFIG |  | No Recommend Value | 0 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 6 (672) / 5G_ConfigurationData_15Sep26.xlsb: 10 (1) |
| `PUSCH_NEARPOINT_PWR_PROTECT_SW@ULPWRCTRLALGOSWITCH` | NRDUCELLULPCCONFIG | 1 | Mixed / Partial | 672 | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| `PoNominalPucch` | NRDUCELLULPCCONFIG | -54 | Mixed / Partial | 664 | 9 | 5G_ConfigurationData_15Sep26.xlsb: -54 (664) / 5G_ConfigurationData_15Sep26.xlsb: -50 (9) |
| `PoNominalPusch` | NRDUCELLULPCCONFIG | -52 | Mixed / Partial | 664 | 9 | 5G_ConfigurationData_15Sep26.xlsb: -52 (664) / 5G_ConfigurationData_15Sep26.xlsb: -37 (9) |
| `PoSrs` | NRDUCELLULPCCONFIG | -55 | Mixed / Partial | 664 | 9 | 5G_ConfigurationData_15Sep26.xlsb: -55 (664) / 5G_ConfigurationData_15Sep26.xlsb: -37 (9) |
| `PreambleInitRxTargetPwr` | NRDUCELLULPCCONFIG | -55 | Mixed / Partial | 664 | 9 | 5G_ConfigurationData_15Sep26.xlsb: -55 (664) / 5G_ConfigurationData_15Sep26.xlsb: -50 (9) |
### NR Performance — Reporting

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NrDataVolumeRptCfg` | NRCellNsaDcConfig | 600 | Mixed / Partial | 577 | 96 | 5G_ConfigurationData_15Sep26.xlsb: 600 (577) / 5G_ConfigurationData_15Sep26.xlsb: 0 (96) |
### NR Performance — Scheduling

| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |
|---|---|---|---|---:|---:|---|
| `NsaDcAlgoSwitch@NSA_DC_PREALLOCATION_SW` | NRCellNsaDcConfig | 0 | Mixed / Partial | 670 | 3 | 5G_ConfigurationData_15Sep26.xlsb: 0 (670) / 5G_ConfigurationData_15Sep26.xlsb: 1 (3) |
| `UlPreallocationSwitch@UL_REDCAP_PREALLOCATION_SW` | NRDUCellPusch | 1 | Consistent | 673 | 0 | 5G_ConfigurationData_15Sep26.xlsb: 1 (673) |
| `UlPreallocationSwitch@UL_SMART_PREALLOCATION_SWITCH` | NRDUCellPusch | 1 | Mixed / Partial | 655 | 18 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |

## 3. Sheet-wise Report

### NR Performance (5G)

- Total parameters: **182**
- Inconsistent: **55**
- Consistent: **41**
- Not found: **0**
- No recommend value: **86**
- Auditable inconsistency rate: **57.3%**

Inconsistent parameters:

| Function | Parameter ID | Recommend | Status | Mismatch Count | Actual (top) |
|---|---|---|---|---:|---|
| Others | `ABNUEULDATAERRORJUDGETHLD` | 5 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 5 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PDCP_SN_ABN_FULL_CONFIG_SW@COMPATIBILITYALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `UL_PDCP_SN_ABN_COMPT_OPT_SW@COMPATIBILITYALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (239) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `NR_NR_ANR_AUTO_NO_HO_SW@AnrSwitch` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `NR_NR_ANR_SW@AnrSwitch` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `AutoDelNCellPenaltyNum` | 50 | Mixed / Partial | 7 | 5G_ConfigurationData_15Sep26.xlsb: 50 (666) / 5G_ConfigurationData_15Sep26.xlsb: 1 (7) |
| Others | `N2NNoHoSuccRateThld` | 80 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 80 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `NR_NR_ANR_NO_HO_AUTO_RES_SW@AnrAlgoSwitch` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `NrNCellNoHoResIntvl` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 30 (3) |
| Others | `PscellA2RsrpThld` | -115 | Mixed / Partial | 13 | 5G_ConfigurationData_15Sep26.xlsb: -115 (660) / 5G_ConfigurationData_15Sep26.xlsb: -121 (9) / 5G_ConfigurationData_15Sep26.xlsb: -111 (4) |
| Others | `NR_NR_ANR_DEL_SW@AnrSwitch` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `DL_SU_MULTI_LAYER_PWR_CTRL_SW@SUMIMOMULTIPLELAYERSW` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `DL_SU_PREDICT_MOBILITY_ENH_SW@SUMIMOMULTIPLELAYERSW` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `DL_SU_PWR_CTRL_ENH_SW@SUMIMOMULTIPLELAYERSW` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `LOW_SNR_CHN_DENOISE_SW@ADAPTIVEEDGEEXPENHSWITCH` | 0 | Mixed / Partial | 54 | 5G_ConfigurationData_15Sep26.xlsb: 0 (619) / 5G_ConfigurationData_15Sep26.xlsb: 1 (54) |
| Others | `NSA_CELL_SIB1_SW@ALGOCOMPATIBILITYSWITCHEXT` | 1 | Inconsistent | 673 | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:NSA_CELL_SIB1_SW> (673) |
| Others | `PUSCH_BEAM_DOMAIN_ENH_SW@FULLCHANNELCOVENHSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PUSCH_TIME_DOMAIN_ENH_SW@FULLCHANNELCOVENHSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `DMRS_PWR_ADAPT_SW@ChnPwrAlgoSwitch` | 1 | Mixed / Partial | 9 | 5G_ConfigurationData_15Sep26.xlsb: 1 (664) / 5G_ConfigurationData_15Sep26.xlsb: 0 (9) |
| Others | `DL_MCS_ADJ_OPT_WT_CHANGE_SW@DLMCSSELALGOSW` | 1 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 1 (670) / 5G_ConfigurationData_15Sep26.xlsb: 0 (3) |
| Others | `DL_SRS_CAP_BASED_BF_GAIN_SW@DLMCSSELALGOSW` | 1 | Inconsistent | 673 | 5G_ConfigurationData_15Sep26.xlsb: <BIT_MISSING:DL_SRS_CAP_BASED_BF_GAIN_SW> (673) |
| Others | `DLRANK2INCSPCTEFFTHLD` | 95 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 95 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| Others | `DLRANK3DECSPCTEFFTHLD` | 150 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 150 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| Others | `DLRANK3INCSPCTEFFTHLD` | 95 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 95 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| Others | `DLRANK4DECSPCTEFFTHLD` | 150 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 150 (672) / 5G_ConfigurationData_15Sep26.xlsb: 110 (1) |
| Others | `DLRANKADAPTLAYERGAPTHLD` | 13 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 13 (672) / 5G_ConfigurationData_15Sep26.xlsb: 15 (1) |
| Others | `DLRANKADAPTMCSTHLD` | 8 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 8 (672) / 5G_ConfigurationData_15Sep26.xlsb: 9 (1) |
| Others | `DLRANKADAPTSPCTEFFCOEFF` | 14 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 14 (672) / 5G_ConfigurationData_15Sep26.xlsb: 8 (1) |
| Others | `PDCCH_AGG_LVL_OPT_SW@PDCCHALGOENHSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PDCCH_RES_ALLOC_ENH_SW@PDCCHALGOSWITCH` | 1 | Mixed / Partial | 31 | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| Others | `UE_PDCCH_SYM_NUM_ADAPT_SW@PDCCHALGOEXTSWITCH` | 0 | Mixed / Partial | 31 | 5G_ConfigurationData_15Sep26.xlsb: 0 (642) / 5G_ConfigurationData_15Sep26.xlsb: 1 (31) |
| Others | `PDCCHEDGEPWRCTRLPOLICY` | BASED_ON_CSI_RPT | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: BASED_ON_CSI_RPT (672) / 5G_ConfigurationData_15Sep26.xlsb: BASED_ON_AGG_LVL (1) |
| Others | `PDCCHMAXAGGLEVEL` | AGG_LVL_8_16_ADAPT | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: AGG_LVL_8_16_ADAPT (672) / 5G_ConfigurationData_15Sep26.xlsb: AGG_LVL_16 (1) |
| Others | `CCE_BASED_SU_PDSCH_BAL_SCH_SW@DLPDSCHALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `DL_INIT_MCS_ADJ_SW@DLLINKADAPTALGOSWITCH` | 1 | Mixed / Partial | 4 | 5G_ConfigurationData_15Sep26.xlsb: 1 (669) / 5G_ConfigurationData_15Sep26.xlsb: 0 (4) |
| Others | `DL_TD_MCS_ADJ_SW@DLLINKADAPTALGOSWITCH` | ON | Mixed / Partial | 34 | 5G_ConfigurationData_15Sep26.xlsb: 1 (639) / 5G_ConfigurationData_15Sep26.xlsb: 0 (34) |
| Others | `HARQ_ACK_RES_SET0_SCH_OPT_SW@PUCCHPERFORMANCESW` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PUCCH_MRC_IRC_SW@PUCCHRECEIVEENHSWITCH` | 1 | Mixed / Partial | 31 | 5G_ConfigurationData_15Sep26.xlsb: 1 (642) / 5G_ConfigurationData_15Sep26.xlsb: 0 (31) |
| Others | `DCI_EXTEND_UL_CONGEST_SW@ULPUSCHALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PUSCHSHAREPUCCHRESPOL` | FULLY_SHARED_TIGHT_CONTROL | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: FULLY_SHARED_TIGHT_CONTROL (672) / 5G_ConfigurationData_15Sep26.xlsb: NOT_SHARED (1) |
| Others | `PUSCH_SHR_PRACH_FREQ_RES_SW@ULPUSCHALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `FULLBUFFERUEULPRBUSAGETHLD` | 50 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 50 (672) / 5G_ConfigurationData_15Sep26.xlsb: 30 (1) |
| Others | `DL_BIG_PKT_SRS_RES_ALLOC_SW@SRSALGOEXTSWITCH` | 1 | Mixed / Partial | 121 | 5G_ConfigurationData_15Sep26.xlsb: 1 (552) / 5G_ConfigurationData_15Sep26.xlsb: 0 (121) |
| Others | `SRS_RIM_INTRF_AVOID_SW@SRSALGOEXTSWITCH` | 1 | Mixed / Partial | 94 | 5G_ConfigurationData_15Sep26.xlsb: 1 (579) / 5G_ConfigurationData_15Sep26.xlsb: 0 (94) |
| Others | `NSAULFACKTOLTESINRTHLD` | 110 | Mixed / Partial | 5 | 5G_ConfigurationData_15Sep26.xlsb: 110 (668) / 5G_ConfigurationData_15Sep26.xlsb: 30 (5) |
| Others | `ULSRSMEASUSAGESWITCH` | DTX_DETECT | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: DTX_DETECT (672) / 5G_ConfigurationData_15Sep26.xlsb: OFF (1) |
| Others | `COVERAGESCENARIO` | SCENARIO_8 | Mixed / Partial | 17 | 5G_ConfigurationData_15Sep26.xlsb: SCENARIO_8 (656) / 5G_ConfigurationData_15Sep26.xlsb: EXPAND_SCENARIO_1 (17) |
| Others | `PUSCH_NEARPOINT_PWR_PROTECT_SW@ULPWRCTRLALGOSWITCH` | 1 | Mixed / Partial | 1 | 5G_ConfigurationData_15Sep26.xlsb: 1 (672) / 5G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Others | `PoNominalPucch` | -54 | Mixed / Partial | 9 | 5G_ConfigurationData_15Sep26.xlsb: -54 (664) / 5G_ConfigurationData_15Sep26.xlsb: -50 (9) |
| Others | `PoNominalPusch` | -52 | Mixed / Partial | 9 | 5G_ConfigurationData_15Sep26.xlsb: -52 (664) / 5G_ConfigurationData_15Sep26.xlsb: -37 (9) |
| Others | `PoSrs` | -55 | Mixed / Partial | 9 | 5G_ConfigurationData_15Sep26.xlsb: -55 (664) / 5G_ConfigurationData_15Sep26.xlsb: -37 (9) |
| Others | `PreambleInitRxTargetPwr` | -55 | Mixed / Partial | 9 | 5G_ConfigurationData_15Sep26.xlsb: -55 (664) / 5G_ConfigurationData_15Sep26.xlsb: -50 (9) |
| Reporting | `NrDataVolumeRptCfg` | 600 | Mixed / Partial | 96 | 5G_ConfigurationData_15Sep26.xlsb: 600 (577) / 5G_ConfigurationData_15Sep26.xlsb: 0 (96) |
| Scheduling | `NsaDcAlgoSwitch@NSA_DC_PREALLOCATION_SW` | 0 | Mixed / Partial | 3 | 5G_ConfigurationData_15Sep26.xlsb: 0 (670) / 5G_ConfigurationData_15Sep26.xlsb: 1 (3) |
| Scheduling | `UlPreallocationSwitch@UL_SMART_PREALLOCATION_SWITCH` | 1 | Mixed / Partial | 18 | 5G_ConfigurationData_15Sep26.xlsb: 1 (655) / 5G_ConfigurationData_15Sep26.xlsb: 0 (18) |

### NR Anchor (4G)

- Total parameters: **74**
- Inconsistent: **24**
- Consistent: **44**
- Not found: **0**
- No recommend value: **6**
- Auditable inconsistency rate: **35.3%**

Inconsistent parameters:

| Function | Parameter ID | Recommend | Status | Mismatch Count | Actual (top) |
|---|---|---|---|---:|---|
| ANR | `EutranNcellDelPunNum` | 50 | Mixed / Partial | 1 | 4G_ConfigurationData_15Sep26.xlsb: 50 (239) / 4G_ConfigurationData_15Sep26.xlsb: 100 (1) |
| ANR | `NR_DELREDUNDANCENCELL@NrtDelMode` | ON | Mixed / Partial | 1 | 4G_ConfigurationData_15Sep26.xlsb: 1 (239) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1) |
| Blacklisting | `BlacklistControlExtSwitch1@NSA_DC_SWITCH` | 0 | Mixed / Partial | 22 | 4G_ConfigurationData_15Sep26.xlsb: 1 (22) / 4G_ConfigurationData_15Sep26.xlsb: 0 (4) |
| LTE CA+NR | `NsaDcLteScellActBfrDelThld` | 3 | Mixed / Partial | 830 | 4G_ConfigurationData_15Sep26.xlsb: 3 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 5 (830) |
| LTE CA+NR | `NsaDcLteScellActBfrLenThld` | 1 | Mixed / Partial | 830 | 4G_ConfigurationData_15Sep26.xlsb: 1 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 0 (830) |
| NSA Anchoring | `NSADCUESELECTIONSTRATEGY` | LTE_UE_PREFERRED | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: LTE_UE_PREFERRED (3467) / 4G_ConfigurationData_15Sep26.xlsb: LTE_NSA_DC_FAIR (6) |
| NSA Anchoring | `InterFreqHoA4TimeToTrig` | 640ms | Mixed / Partial | 3072 | 4G_ConfigurationData_15Sep26.xlsb: 640ms (3874) / 4G_ConfigurationData_15Sep26.xlsb: 1024ms (3072) |
| NSA Anchoring | `IDLE_MODE_NSA_PCC_ANCHORING_SW@NSADCALGOSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| NSA Anchoring | `INSTANT_JUDGEMENT_SW@NSADCALGOEXTSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| NSA Anchoring | `NSADCPCCANCHORINGPOLICY` | BASED_ON_NR_COVERAGE | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: BASED_ON_NR_COVERAGE (3467) / 4G_ConfigurationData_15Sep26.xlsb: DEFAULT (6) |
| NSA Anchoring | `NSA_DC_COV_HO_ENH_SW@NSADCALGOSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| NSA Anchoring | `NSA_PCC_ANCHORING_SWITCH@NSADCALGOSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| NSA Anchoring | `PERIODIC_PCC_ANCHORING_SW@NSADCALGOSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| NSA Anchoring | `SCGADDITIONBUFFERLENTHLD` | 10 | Mixed / Partial | 532 | 4G_ConfigurationData_15Sep26.xlsb: 10 (2941) / 4G_ConfigurationData_15Sep26.xlsb: 0 (532) |
| NSA Anchoring | `SCGADDITIONINTERVAL` | 10 | Mixed / Partial | 20 | 4G_ConfigurationData_15Sep26.xlsb: 10 (3453) / 4G_ConfigurationData_15Sep26.xlsb: 60 (20) |
| NSA Anchoring | `DlArfcn` | N41 | Inconsistent | 195 | 4G_ConfigurationData_15Sep26.xlsb: 528990 (195) |
| NSA Anchoring | `FrequencyBand` | NULL | Inconsistent | 195 | 4G_ConfigurationData_15Sep26.xlsb: N41 (195) |
| NSA Anchoring | `NSADCPCCA4RSRPTHLD` | -115 | Inconsistent | 1679 | 4G_ConfigurationData_15Sep26.xlsb: -128 (1679) |
| Protocol | `COV_BASED_DIRECTIONAL_HO_SW@NSADCUELTEFUNACTIVATIONSW` | 0 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 1 (6) |
| Protocol | `FREQ_PRI_HO_SW@NSADCUELTEFUNACTIVATIONSW` | 0 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 0 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 1 (6) |
| Protocol | `MBOCS_SW@NSADCUELTEFUNACTIVATIONSW` | 0 | Mixed / Partial | 830 | 4G_ConfigurationData_15Sep26.xlsb: 0 (2643) / 4G_ConfigurationData_15Sep26.xlsb: 1 (830) |
| Reporting | `NrDataVolumeRptCfg` | 600 | Mixed / Partial | 540 | 4G_ConfigurationData_15Sep26.xlsb: 600 (2933) / 4G_ConfigurationData_15Sep26.xlsb: 0 (540) |
| SCG Addition | `SCG_ADD_PCC_ANCHOR_VOL_OPT_SW@NSADCALGOEXTSWITCH` | 1 | Mixed / Partial | 6 | 4G_ConfigurationData_15Sep26.xlsb: 1 (3467) / 4G_ConfigurationData_15Sep26.xlsb: 0 (6) |
| SCG Addition | `PERIODIC_SCG_ADD_OPT_SW@NsaDcAlgoExtSwitch` | 1 | Mixed / Partial | 1432 | 4G_ConfigurationData_15Sep26.xlsb: 1 (2041) / 4G_ConfigurationData_15Sep26.xlsb: 0 (1432) |

## 4. Final Summary

The reference files contain **256** parameters. **79** parameters are inconsistent against the input configuration dumps (5 fully mismatched, 74 mixed). NR Performance: 55 inconsistent of 182 NR Anchor: 24 inconsistent of 74. **85** parameters fully match the recommend value. **92** parameters have no recommend value in the reference and were excluded from the inconsistency rate. **0** parameters could not be mapped to the dumps.

Largest function-level inconsistency counts:

- **NR Performance / Others**: 52 of 175 parameters inconsistent
- **NR Anchor / NSA Anchoring**: 13 of 26 parameters inconsistent
- **NR Anchor / Protocol**: 3 of 6 parameters inconsistent
- **NR Performance / Scheduling**: 2 of 3 parameters inconsistent
- **NR Anchor / SCG Addition**: 2 of 13 parameters inconsistent
- **NR Anchor / LTE CA+NR**: 2 of 2 parameters inconsistent
- **NR Anchor / ANR**: 2 of 14 parameters inconsistent
- **NR Performance / Reporting**: 1 of 1 parameters inconsistent
- **NR Anchor / Reporting**: 1 of 1 parameters inconsistent
- **NR Anchor / Blacklisting**: 1 of 1 parameters inconsistent

Detailed workbook: `reports/runs/15Sep26_folders/Parameter_Inconsistency_Report.xlsx`