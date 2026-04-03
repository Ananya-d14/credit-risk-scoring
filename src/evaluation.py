import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve


def ks_statistic(y_true, y_prob):
    """
    KS stat — max separation between good/bad CDFs.
    This is THE standard metric in credit scoring (see Siddiqi ch.8).
    KS > 0.4 is excellent, < 0.2 is basically useless.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    ks_values = tpr - fpr
    ks_idx = np.argmax(ks_values)

    return {
        "ks_statistic": ks_values[ks_idx],
        "ks_threshold": thresholds[ks_idx],
        "fpr": fpr, "tpr": tpr,
        "thresholds": thresholds,
        "ks_values": ks_values,
    }


def expected_profit(y_true, y_prob, threshold, profit_good=100, loss_bad=500):
    """
    Profit at a given threshold.

    If we approve (prob_bad < threshold):
      - actually good -> +profit_good
      - actually bad  -> -loss_bad  (ouch)
    If we reject -> $0
    """
    y_pred = (y_prob >= threshold).astype(int)

    approved_good = ((y_pred == 0) & (y_true == 0)).sum()
    approved_bad  = ((y_pred == 0) & (y_true == 1)).sum()

    profit = approved_good * profit_good - approved_bad * loss_bad
    n_approved = (y_pred == 0).sum()

    return {
        "profit": profit,
        "threshold": threshold,
        "n_approved": n_approved,
        "n_rejected": (y_pred == 1).sum(),
        "approved_good": approved_good,
        "approved_bad": approved_bad,
        "approval_rate": n_approved / len(y_true),
    }


def optimize_threshold(y_true, y_prob, profit_good=100, loss_bad=500,
                       thresholds=None):
    """Brute-force sweep to find profit-maximizing threshold."""
    if thresholds is None:
        thresholds = np.arange(0.05, 0.96, 0.01)

    results = [expected_profit(y_true, y_prob, t, profit_good, loss_bad)
               for t in thresholds]
    return pd.DataFrame(results)


def decile_analysis(y_true, y_prob):
    """
    Standard credit scoring decile table.
    Splits population into 10 risk buckets and checks that bad rate
    increases monotonically (if it doesn't, something's off with the model).
    """
    data = pd.DataFrame({"y_true": y_true, "y_prob": y_prob})
    data["decile"] = pd.qcut(data["y_prob"], q=10, labels=False, duplicates="drop") + 1

    agg = data.groupby("decile").agg(
        count=("y_true", "count"),
        bad_count=("y_true", "sum"),
        avg_prob=("y_prob", "mean"),
        min_prob=("y_prob", "min"),
        max_prob=("y_prob", "max"),
    ).reset_index()

    agg["good_count"] = agg["count"] - agg["bad_count"]
    agg["bad_rate"] = agg["bad_count"] / agg["count"]
    agg = agg.sort_values("decile")

    # cumulative from the riskiest decile downward
    agg_rev = agg.sort_values("decile", ascending=False)
    agg_rev["cum_bad"] = agg_rev["bad_count"].cumsum()
    agg_rev["cum_total"] = agg_rev["count"].cumsum()
    agg_rev["cum_bad_rate"] = agg_rev["cum_bad"] / agg_rev["cum_total"]
    agg_rev["cum_bad_capture"] = agg_rev["cum_bad"] / agg_rev["bad_count"].sum()

    return agg_rev.sort_values("decile")


def gains_chart_data(y_true, y_prob):
    """Cumulative gains for plotting. Returns (pct_population, pct_bad_captured)."""
    data = pd.DataFrame({"y_true": y_true, "y_prob": y_prob})
    data = data.sort_values("y_prob", ascending=False)

    total_bad = data["y_true"].sum()
    data["cum_bad"] = data["y_true"].cumsum()
    data["cum_pct"] = np.arange(1, len(data) + 1) / len(data)
    data["cum_capture"] = data["cum_bad"] / total_bad

    return data["cum_pct"].values, data["cum_capture"].values
