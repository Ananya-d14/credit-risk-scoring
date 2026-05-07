# Data Dictionary

Source: CreditScoring.xlsx (3,000 rows, 30 columns)

## Target

| Column | Values | Meaning |
|--------|--------|---------|
| TARGET | 0 / 1 | 0 = good loan, 1 = bad (default) |

## ID (dropped before modeling)

| Column | Type |
|--------|------|
| ID | Unique identifier |

## Features (28)

### Derogatory / Adverse
| Feature | What it means |
|---------|--------------|
| DerogCnt | Number of derogatory public records |
| CollectCnt | Number of collections |
| BanruptcyInd | Bankruptcy indicator (0/1) |
| TLBadDerogCnt | Derogatory + adverse trade lines combined |
| TLBadCnt24 | Adverse trade lines in last 24 months |

### Inquiries
| Feature | What it means |
|---------|--------------|
| InqCnt06 | Credit inquiries in last 6 months |
| InqTimeLast | Months since last inquiry |
| InqFinanceCnt24 | Finance inquiries in 24 months |

### Trade Line Counts
| Feature | What it means |
|---------|--------------|
| TLCnt03 | Trade lines opened in 3 months |
| TLCnt12 | Trade lines opened in 12 months |
| TLCnt24 | Trade lines opened in 24 months |
| TLCnt | Total trade lines |
| TLSatCnt | Satisfactory trade lines |

### Balances & Utilization
| Feature | What it means |
|---------|--------------|
| TLSum | Total balance |
| TLMaxSum | Max balance |
| TL75UtilCnt | Trade lines >75% utilized |
| TL50UtilCnt | Trade lines >50% utilized |
| TLBalHCPct | Balance-to-high-credit ratio |

### Delinquency
| Feature | What it means |
|---------|--------------|
| TLDel60Cnt | Trade lines 60+ days late |
| TLDel3060Cnt24 | 30-60 days late in 24 months |
| TLDel90Cnt24 | 90+ days late in 24 months |
| TLDel60CntAll | Ever 60+ days late (all time) |
| TLDel60Cnt24 | 60+ days late in 24 months |

### Credit History
| Feature | What it means |
|---------|--------------|
| TLTimeFirst | Months since first trade line |
| TLTimeLast | Months since last trade line |

### Account Status
| Feature | What it means |
|---------|--------------|
| TLSatPct | % satisfactory trade lines |
| TLOpenPct | % open trade lines |
| TLOpen24Pct | % opened in last 24 months |

## Notes

- Missing values in 8 features. InqTimeLast has the most (~6%) — probably applicants with no inquiry history.
- Target is imbalanced: 2500 good (83%) vs 500 bad (17%).
