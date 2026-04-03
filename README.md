---
title: Credit Risk Scoring API
emoji: 💳
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Credit Risk Scoring API

This app predicts whether a loan applicant is likely to **repay** or **default** on their loan, based on their credit history.

---

## Step-by-Step Guide (No coding needed!)

### Step 1: Open the API page

Click the **"API Docs"** tab at the top of this page. This opens an interactive form where you can test the model.

### Step 2: Find the Predict section

Scroll down until you see a green box that says **POST /predict**. Click on it to expand it.

### Step 3: Click "Try it out"

On the right side, you'll see a button that says **"Try it out"**. Click it. The JSON text box below will now become editable.

### Step 4: Enter applicant details

You'll see a text box with sample data that looks like this:

```json
{
  "DerogCnt": 0,
  "CollectCnt": 0,
  "BanruptcyInd": 0,
  ...
}
```

Change the numbers to match the applicant you want to evaluate. See the **"What do the fields mean?"** section below for what each field represents.

**Don't worry if you don't have all the values** — just leave them as-is or set them to `null`. The model will fill in missing values automatically.

### Step 5: Click "Execute"

Scroll down a little and click the blue **"Execute"** button.

### Step 6: Read the result

Scroll down further. Under **"Responses"**, you'll see something like:

```json
{
  "default_probability": 0.0684,
  "decision": "APPROVE",
  "risk_category": "LOW"
}
```

Here's what this means:

| What you see | What it means |
|-------------|---------------|
| `"default_probability": 0.07` | There is a **7% chance** this person will not repay the loan |
| `"decision": "APPROVE"` | The model recommends **approving** this loan |
| `"risk_category": "LOW"` | This applicant is **low risk** |

### Step 7: Test another person

To check a different applicant, just **change the numbers** in the JSON box and click **"Execute"** again. You can do this as many times as you want.

---

## Understanding the Decision

| Risk Category | Default Probability | Decision |
|--------------|-------------------|----------|
| **LOW** | Less than 15% | APPROVE |
| **MEDIUM** | 15% to 35% | APPROVE |
| **HIGH** | More than 35% | REJECT |

---

## What Do the Fields Mean?

Below is every field you can fill in. **All fields are optional** — skip any you don't know.

### Negative credit history
| Field | Plain English | Example |
|-------|--------------|---------|
| `DerogCnt` | How many negative marks on their credit report? | 0 = clean, 3 = some issues |
| `CollectCnt` | How many debts sent to collection agencies? | 0 = none, 2 = two debts in collection |
| `BanruptcyInd` | Have they ever declared bankruptcy? | 0 = no, 1 = yes |
| `TLBadDerogCnt` | How many severely negative accounts? | 0 = none |
| `TLBadCnt24` | How many bad accounts in the last 2 years? | 0 = none |

### Credit inquiries (how often they apply for credit)
| Field | Plain English | Example |
|-------|--------------|---------|
| `InqCnt06` | How many times their credit was checked in 6 months? | 1 = normal, 8 = a lot |
| `InqTimeLast` | How many months since the last credit check? | 12 = a year ago, 1 = last month |
| `InqFinanceCnt24` | How many finance-related credit checks in 2 years? | 2 = normal |

### Number of accounts (tradelines)
| Field | Plain English | Example |
|-------|--------------|---------|
| `TLCnt` | Total number of credit accounts ever | 8 = moderate |
| `TLCnt03` | New accounts opened in last 3 months | 0 = none recently |
| `TLCnt12` | New accounts opened in last 12 months | 1 = one new account |
| `TLCnt24` | New accounts opened in last 2 years | 2 = two new accounts |
| `TLSatCnt` | How many accounts are in good standing? | 7 out of 8 = good |
| `TLSatPct` | What percentage of accounts are in good standing? | 0.875 = 87.5% |

### Balances and how much credit they use
| Field | Plain English | Example |
|-------|--------------|---------|
| `TLSum` | Total balance across all accounts ($) | 15000 |
| `TLMaxSum` | Largest single account balance ($) | 8000 |
| `TL75UtilCnt` | How many accounts are using more than 75% of their limit? | 1 |
| `TL50UtilCnt` | How many accounts are using more than 50% of their limit? | 2 |
| `TLBalHCPct` | Overall balance-to-limit ratio | 0.45 = using 45% of available credit |

### Late payments
| Field | Plain English | Example |
|-------|--------------|---------|
| `TLDel60Cnt` | Accounts currently 60+ days late | 0 = none |
| `TLDel3060Cnt24` | Times 30-60 days late in past 2 years | 0 = never |
| `TLDel90Cnt24` | Times 90+ days late in past 2 years | 0 = never |
| `TLDel60CntAll` | Total times 60+ days late ever | 0 = never |
| `TLDel60Cnt24` | Times 60+ days late in past 2 years | 0 = never |

### Credit history age and status
| Field | Plain English | Example |
|-------|--------------|---------|
| `TLTimeFirst` | How many months since their first account was opened? | 120 = 10 years of history |
| `TLTimeLast` | How many months since their most recent account? | 6 = opened one 6 months ago |
| `TLOpenPct` | What percentage of accounts are still open? | 0.75 = 75% |
| `TLOpen24Pct` | What percentage were opened in the last 2 years? | 0.25 = 25% |

---

## Example: Testing a Good Applicant

Use these values (long credit history, no late payments, low utilisation):

```json
{
  "DerogCnt": 0, "CollectCnt": 0, "BanruptcyInd": 0,
  "InqCnt06": 1, "InqTimeLast": 6, "InqFinanceCnt24": 2,
  "TLTimeFirst": 180, "TLTimeLast": 12,
  "TLCnt": 12, "TLCnt03": 0, "TLCnt12": 1, "TLCnt24": 2,
  "TLSatCnt": 11, "TLSatPct": 0.92,
  "TLSum": 10000, "TLMaxSum": 5000,
  "TL75UtilCnt": 0, "TL50UtilCnt": 1, "TLBalHCPct": 0.25,
  "TLDel60Cnt": 0, "TLDel3060Cnt24": 0, "TLDel90Cnt24": 0,
  "TLDel60CntAll": 0, "TLDel60Cnt24": 0,
  "TLBadDerogCnt": 0, "TLBadCnt24": 0,
  "TLOpenPct": 0.6, "TLOpen24Pct": 0.15
}
```

**Expected result**: APPROVE, LOW risk

## Example: Testing a Risky Applicant

Use these values (bankruptcy, many late payments, high utilisation):

```json
{
  "DerogCnt": 5, "CollectCnt": 3, "BanruptcyInd": 1,
  "InqCnt06": 8, "InqTimeLast": 1, "InqFinanceCnt24": 10,
  "TLTimeFirst": 24, "TLTimeLast": 1,
  "TLCnt": 10, "TLCnt03": 3, "TLCnt12": 5, "TLCnt24": 8,
  "TLSatCnt": 2, "TLSatPct": 0.2,
  "TLSum": 50000, "TLMaxSum": 30000,
  "TL75UtilCnt": 7, "TL50UtilCnt": 8, "TLBalHCPct": 0.95,
  "TLDel60Cnt": 4, "TLDel3060Cnt24": 2, "TLDel90Cnt24": 3,
  "TLDel60CntAll": 6, "TLDel60Cnt24": 4,
  "TLBadDerogCnt": 5, "TLBadCnt24": 3,
  "TLOpenPct": 0.9, "TLOpen24Pct": 0.8
}
```

**Expected result**: REJECT, HIGH risk

---

## For Developers

You can also call this API from code:

**Python:**
```python
import requests

response = requests.post(
    "https://ananyajoshids-credit-risk-scorer.hf.space/predict",
    json={"DerogCnt": 0, "BanruptcyInd": 0, "TLCnt": 8, "TLSatPct": 0.9}
)
print(response.json())
```

**cURL:**
```bash
curl -X POST "https://ananyajoshids-credit-risk-scorer.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{"DerogCnt": 0, "BanruptcyInd": 0, "TLCnt": 8, "TLSatPct": 0.9}'
```

---

## About the Model

- **Algorithm**: XGBoost (tuned with cross-validation)
- **Accuracy metric**: ROC-AUC = 0.78
- **Decision threshold**: 0.35 (optimised for profit given $100 profit per good loan, $500 loss per default)
- **Training data**: 3,000 loan applications with 28 credit bureau features
