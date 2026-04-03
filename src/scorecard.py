import numpy as np
import pandas as pd


def build_scorecard(woe_bins_dict, lr_model, feature_names,
                    base_score=600, pdo=20, target_odds=50):
    """
    Turn WoE logistic regression into a points scorecard.

    The math here follows Siddiqi (2012) ch.10:
        factor = PDO / ln(2)
        offset = base_score - factor * ln(target_odds)
        points_i = -(WoE_i * beta_i + alpha/n) * factor + offset/n

    I spent way too long debugging the sign conventions on this...
    """
    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(target_odds)

    intercept = lr_model.intercept_[0]
    coefficients = dict(zip(feature_names, lr_model.coef_[0]))
    n = len(feature_names)

    rows = []
    for feat in feature_names:
        coef = coefficients[feat]
        if feat not in woe_bins_dict:
            continue

        woe_data = woe_bins_dict[feat]
        for bin_label, row in woe_data.iterrows():
            woe = row["woe"]
            points = -(woe * coef + intercept / n) * factor + offset / n
            rows.append({
                "Feature": feat,
                "Bin": str(bin_label),
                "WoE": round(woe, 4),
                "Coefficient": round(coef, 4),
                "Points": round(points, 1),
            })

    return pd.DataFrame(rows)


# TODO: this function is kind of janky with the bin matching.
# works fine for the notebooks but would need cleanup for production use.
def score_applicant(applicant_row, scorecard_df, feature_bins_dict):
    """Score a single applicant using the points scorecard."""
    total = 0
    for feat in scorecard_df["Feature"].unique():
        feat_card = scorecard_df[scorecard_df["Feature"] == feat]
        val = applicant_row.get(feat, None)
        if val is None:
            continue
        matched = False
        for _, row in feat_card.iterrows():
            bin_str = row["Bin"]
            try:
                interval = pd.Interval(
                    *[float(x) for x in bin_str.strip("()[]").split(",")]
                )
                if val in interval:
                    total += row["Points"]
                    matched = True
                    break
            except (ValueError, TypeError):
                if str(val) == bin_str:
                    total += row["Points"]
                    matched = True
                    break
        if not matched:
            total += feat_card["Points"].median()  # fallback
    return round(total)


def score_to_probability(score, base_score=600, pdo=20, target_odds=50):
    """Convert score back to P(default). Useful for sanity checking."""
    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(target_odds)
    odds = np.exp((score - offset) / factor)
    prob_good = odds / (1 + odds)
    return 1 - prob_good
