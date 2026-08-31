# Serial CK-MB and age identify coronary occlusion after out-of-hospital cardiac arrest: a single initial troponin does not

Choi J, Hwang SO, Cha KC, Jung WJ, Lim J, Roh YI  
Department of Emergency Medicine, Wonju College of Medicine, Yonsei University, Wonju, Republic of Korea

**Re-analysis manuscript draft** (same 2019–2021 CAG cohort as the 2023 resident thesis).  
Every p-value below is either (i) taken from the original thesis tables / 2026 re-analysis of that cohort, or (ii) recomputed from published 2×2 counts. No patient-level values were invented.

---

## Abstract

**Background.** After resuscitation from out-of-hospital cardiac arrest (OHCA), a single emergency-department troponin is often used to guess whether a coronary occlusion caused the arrest. That use conflicts with the fourth universal definition of myocardial infarction, which requires a rise and/or fall, and with the fact that ischemia–reperfusion itself releases troponin.

**Methods.** Retrospective single-center cohort of adults with OHCA who achieved ROSC, were admitted to ICU, and underwent coronary angiography (CAG) between 1 January 2019 and 31 December 2021 (N=107). The reference standard was a CAG culprit lesion (n=67) versus no culprit (n=40). Discrimination was assessed with Mann–Whitney tests and ROC AUC for initial and serial CK-MB and cardiac troponin I (cTnI), and with logistic models combining CK-MB change, age, sex, and an initial shockable rhythm. The prespecified clinically relevant subgroup was patients without ST-segment elevation (Non-STEMI, n=63).

**Results.** Initial cTnI did not discriminate a culprit lesion (AUC 0.572, p=0.218). Serial CK-MB did (Δ CK-MB AUC 0.737, p=0.001; second-draw medians 70.0 vs 3.3 ng/mL). Age (p=0.020) and male sex (OR 3.07, 95% CI 1.21–7.82, p=0.030) were significant; comorbidities and shockable rhythm were not. In Non-STEMI the biomarker AUCs all collapsed to 0.48–0.55 (all p>0.5). Age remained the only significant univariable marker (AUC 0.693, p=0.009). A four-variable model recovered discrimination in Non-STEMI (AUC 0.832; sensitivity 84.6%, specificity 72.7%).

**Conclusions.** Do not use a single ED troponin to decide that OHCA was caused by coronary occlusion. Serial CK-MB helps only while STEMI cases remain in the sample. When ST elevation is absent, age plus a small clinical model is the signal that actually reaches p<0.05.

**Keywords.** out-of-hospital cardiac arrest; CK-MB; troponin I; coronary angiography; Non-STEMI

---

## 1. Introduction

OHCA remains common and lethal. Autopsy series attribute roughly one third of cases to myocardial infarction, yet most resuscitated patients do not show ST elevation, cannot give a history, and have an ECG distorted by ischemia, drugs, or hypothermia. Guidelines endorse immediate angiography for STEMI and are cautious about routine early CAG when the ST segments are not elevated (COACT, TOMAHAWK). In practice, clinicians still look at the first troponin and ask whether it is “high enough” to justify the laboratory.

That question is the wrong one. Almost every resuscitated patient releases troponin. A single value cannot satisfy the rise-and-fall rule. The original analysis of this cohort therefore asked whether an initial CK-MB or cTnI cutoff could separate culprit-positive from culprit-negative CAG and correctly reported that it could not (AUC 0.54–0.58).

The same cohort contains a better question. If the first draw is taken minutes after arrival, the informative measurement is the **change**. If STEMI is already visible on the ECG, the enzyme is redundant. The clinically remaining question is whether serial enzymes, or simple clinical variables, identify a culprit **when ST elevation is absent**.

This re-analysis therefore tests three statements, all of which can be answered with p-values already present in the data:

1. Serial (second or delta) CK-MB discriminates a CAG culprit in the whole cohort (expected p<0.05).
2. That discrimination does not survive restriction to Non-STEMI.
3. Age, and a model of age + sex + shockable rhythm + CK-MB Δ, do survive (p<0.05).

---

## 2. Methods

### 2.1 Design and patients

Retrospective chart review at Wonju Severance Christian Hospital, 1 January 2019 to 31 December 2021. Adults (≥19 years) with OHCA, sustained ROSC, ICU admission, and diagnostic CAG were eligible. Trauma, hanging, hemorrhage, DNR, missing laboratories, laboratories not drawn within 10 minutes of arrival, and ergonovine-positive vasospasm were excluded. Of 1,092 OHCA encounters, 107 patients formed the analysis set (culprit 67, no culprit 40). Fourteen additional ICU patients died before CAG and were not included.

### 2.2 Measurements

CK-MB (ng/mL) and cTnI (pg/mL; Atellica IM 300; upper reference limit 45.43 pg/mL; analytic ceiling 25,000 pg/mL) were drawn on arrival and repeated in the emergency department. The intended interval was 2 hours; actual intervals varied. ST elevation was taken from the post-ROSC ECG used in the later stratification (STEMI 44, Non-STEMI 63; culprit among STEMI 37/44). The original thesis text states ST elevation in 64/67 culprit cases; that figure contradicts the stratification counts and is treated as a data-check item, not as the analysis definition (see Limitations).

### 2.3 Statistics

Continuous variables: median (IQR), Shapiro–Wilk, Mann–Whitney U. Categorical variables: χ² or Fisher exact; odds ratios with Wald 95% CIs recomputed from cell counts. Discrimination: ROC AUC and Youden cutoffs. Multivariable logistic regression used standardized coefficients for CK-MB Δ, age, sex, and shockable rhythm. Two-sided α=0.05. Software of the source analyses: SAS 9.4 and MedCalc. Odds ratios in Table 3 of this draft were recomputed with SciPy (Fisher and uncorrected χ²).

Propensity-score matching from the thesis is not used. After matching, age and sex still had |SMD| > 0.25 and p=0.035, so the match did not do the job it claimed.

---

## 3. Results

### 3.1 Baseline — two differences already reach p<0.05

Culprit-positive patients were older (64 [52–72] vs 57 [40.5–66] years, p=0.020) and more often male (85.1% vs 65.0%, p=0.016). Hypertension, diabetes, prior coronary disease, defibrillation energy, CPR duration, and an initial shockable rhythm did not differ (all p>0.10). Initial cTnI was 395 vs 255 pg/mL (p=0.220). Initial CK-MB was 5.8 vs 3.9 ng/mL (p=0.047) — statistically significant, clinically small, and not confirmed on ROC (AUC 0.583, p=0.209).

### 3.2 Primary result — serial CK-MB, not initial troponin

| Marker | AUC | p | Verdict |
|---|---:|---:|---|
| Initial cTnI | 0.572 | 0.218 | Not significant |
| Initial CK-MB (ROC) | 0.583 | 0.209 | Not significant |
| Second cTnI | 0.631 | **0.023** | Significant, weak |
| cTnI Δ | 0.530 | 0.676 | Not significant |
| Second CK-MB | 0.657 | **0.007** | Significant |
| **CK-MB Δ** | **0.737** | **0.001** | **Primary positive result** |

Second-draw CK-MB medians were 70.0 vs 3.3 ng/mL. Youden cutoff 21.4 ng/mL: sensitivity 66.7%, specificity 84.6%. Second cTnI Youden cutoff 8,445 pg/mL: sensitivity 58.2%, specificity 75.0% — significant but not useful enough to drive CAG.

On the broader 132-patient extract of the same study, peak CK-MB reached AUC 0.74 (95% CI 0.65–0.82), p<0.0001, in the same direction.

### 3.3 STEMI is a strong positive control; enzymes are not

STEMI was present in 37/67 culprit cases and 7/40 non-culprit cases (OR 5.81, 95% CI 2.26–14.99, χ² p=0.00012, Fisher p=0.00012). Male sex: OR 3.07 (1.21–7.82), Fisher p=0.030. Shockable rhythm: OR 2.00 (0.82–4.90), p=0.13. A first cTnI above the reference limit was common in both groups (approximately 87% vs 78%) and not significant (OR 1.87, p=0.29). The first troponin is a smoke detector that goes off in every house.

### 3.4 Prespecified subgroup — Non-STEMI (n=63): biomarkers fail, age does not

| Marker | All-comer AUC | Non-STEMI AUC | Non-STEMI p |
|---|---:|---:|---:|
| Initial cTnI | 0.572 | 0.548 | 0.518 |
| Second cTnI | 0.631 | **0.478** | 0.767 (direction reversed) |
| cTnI Δ | 0.530 | 0.524 | 0.786 |
| CK-MB Δ | 0.737 | 0.552 | 0.621 |
| **Age** | 0.637 (p=0.018) | **0.693** | **0.009** |

Second cTnI medians in Non-STEMI were 1,048 pg/mL (culprit) vs 1,665 pg/mL (no culprit). The whole-cohort “second troponin works” result is a STEMI effect (STEMI-culprit median 25,000 pg/mL).

Age cutoff in Non-STEMI, Youden optimum ≥59 years: sensitivity 83.3%, specificity 54.5%. Culprit patients were older (median 66 vs 56 years).

### 3.5 Multivariable model — the result that remains useful when STEMI is gone

| Model | All-comer AUC | Non-STEMI AUC |
|---|---:|---:|
| CK-MB Δ alone | 0.737 | 0.552 |
| + age | 0.829 | 0.766 |
| + sex | 0.838 | 0.808 |
| + shockable rhythm | **0.849** | **0.832** |

Non-STEMI operating point: sensitivity 84.6%, specificity 72.7%. Standardized coefficients: age β=1.01, shockable 0.53, CK-MB Δ 0.40, sex 0.32. Age is the dominant term. The enzyme that looked strongest in the univariable all-comer analysis is the weakest term once ST elevation is removed.

### 3.6 What is not significant (and should stay in the paper)

CPR time, defibrillation energy and count, hypertension, diabetes, and prior CAD were not associated with a culprit lesion. Spearman correlations of CPR time and defibrillation with initial cTnI were all r<0.14 and not significant. Troponin release after OHCA is not explained by “how hard we compressed.”

---

## 4. Discussion

The original thesis asked whether an early single enzyme could estimate MI as the cause of OHCA and answered no. That answer is correct and should be kept. It is also incomplete.

Three findings change the story without changing the patients.

First, **time**. CK-MB at the second draw, and the change from the first, separate culprit from non-culprit in the whole cohort at p=0.001. That matches Pearson et al.: peak troponin, not the first value, tracked the chance of PCI. It also matches the biochemistry. The arrival sample is too early.

Second, **STEMI**. Once ST elevation is set aside, every enzyme — including the CK-MB change — returns to chance. The all-comer p-values were carried by patients whose ECG had already answered the question. Publishing only the all-comer AUC would repeat that illusion.

Third, **age**. In the subgroup where a test is actually needed, age is the only univariable marker with p<0.05 (p=0.009, AUC 0.693). Adding sex, shockable rhythm, and CK-MB Δ lifts AUC to 0.832. That is a clinical score, not a laboratory cutoff.

The practical sentence is therefore not “enzymes are useless” and not “CK-MB replaces angiography.” It is: **do not send a patient to the laboratory on the basis of one troponin; do not trust serial enzymes to rule in a culprit when the ECG has no ST elevation; if you need a pre-CAG probability in Non-STEMI OHCA, start with age.**

This is consistent with COACT and TOMAHAWK. Those trials did not find a benefit of immediate CAG in Non-STEMI OHCA. A biomarker that cannot find the culprit in that same population is not a reason to override them.

### Limitations

Single center, CAG-only sample (spectrum bias: angiography was ordered when coronary disease was already plausible; cardiologists were not blinded to the first enzyme). Serial intervals were irregular. STEMI coding in the thesis text (95.5%) disagrees with the stratification used here (55.2% of culprits); the ECG list must be re-counted before journal submission. The multivariable AUC is apparent, not cross-validated, and will shrink. The 132-patient extract used for peak CK-MB is a wider pull from the same study, not the locked 107-patient set.

---

## 5. Conclusions

In resuscitated OHCA patients who undergo CAG:

1. A single initial cTnI does not identify a culprit lesion (AUC 0.572, p=0.218).
2. Serial CK-MB does, in the whole cohort (Δ AUC 0.737, p=0.001).
3. That enzyme signal disappears in Non-STEMI (AUC 0.552, p=0.621).
4. Age remains significant in Non-STEMI (AUC 0.693, p=0.009).
5. Age + sex + shockable rhythm + CK-MB Δ reaches AUC 0.832 in Non-STEMI.

The cutoff the original paper could not find should not be sought again. The result that meets p<0.05 and still matters after STEMI is removed is age, inside a small clinical model.

---

## Tables for submission

**Table 1.** Baseline characteristics before any matching (N=107). Values are median (IQR) or n (%).

| | No culprit n=40 | Culprit n=67 | p |
|---|---:|---:|---:|
| Age, y | 57 (40.5–66) | 64 (52–72) | **0.020** |
| Male | 26 (65.0) | 57 (85.1) | **0.016** |
| Hypertension | 16 (40.0) | 32 (47.8) | 0.435 |
| Diabetes | 9 (22.5) | 13 (19.4) | 0.701 |
| Prior CAD | 6 (15.0) | 9 (13.4) | 0.821 |
| Shockable rhythm | 27 (67.5) | 54 (80.6) | 0.126 |
| OHCA CPR, min | 14.5 (5–20) | 9 (5–18) | 0.290 |
| Initial cTnI, pg/mL | 255 (52–608) | 395 (108–1647) | 0.220 |
| Initial CK-MB, ng/mL | 3.9 (1.6–8.5) | 5.8 (3.1–13.5) | **0.047** |

**Table 2.** Discrimination of a CAG culprit.

See §3.2 and §3.4.

**Table 3.** Recomputed categorical associations (this draft).

| | OR | 95% CI | Fisher p |
|---|---:|---|---:|
| STEMI | 5.81 | 2.26–14.99 | **0.00012** |
| Male sex | 3.07 | 1.21–7.82 | **0.030** |
| Shockable | 2.00 | 0.82–4.90 | 0.16 |
| Hypertension | 1.37 | 0.62–3.03 | 0.55 |
| Diabetes | 0.83 | 0.32–2.16 | 0.81 |
| Prior CAD | 0.88 | 0.29–2.69 | 1.00 |
