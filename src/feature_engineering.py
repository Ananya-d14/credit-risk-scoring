import numpy as np
import pandas as pd


def calculate_woe_iv(df, feature, target, bins=10):
    """
    WoE/IV calculation for a single feature.
    Based on Siddiqi (2012) chapter on fine/coarse classing.

    Returns bin-level stats dataframe + total IV.
    """
    df = df[[feature, target]].copy().dropna()

    # bin the feature — use the values directly if there are few unique vals
    if df[feature].nunique() <= bins:
        df["bin"] = df[feature]
    else:
        try:
            df["bin"] = pd.qcut(df[feature], q=bins, duplicates="drop")
        except ValueError:
            # qcut fails when too many tied values, fall back to equal-width
            df["bin"] = pd.cut(df[feature], bins=bins)

    grouped = df.groupby("bin", observed=True)[target].agg(["count", "sum"])
    grouped.columns = ["total", "bad"]
    grouped["good"] = grouped["total"] - grouped["bad"]

    total_good = grouped["good"].sum()
    total_bad = grouped["bad"].sum()

    # laplace smoothing so we don't blow up with log(0)
    grouped["dist_good"] = (grouped["good"] + 0.5) / (total_good + 0.5 * len(grouped))
    grouped["dist_bad"] = (grouped["bad"] + 0.5) / (total_bad + 0.5 * len(grouped))

    grouped["woe"] = np.log(grouped["dist_good"] / grouped["dist_bad"])
    grouped["iv"] = (grouped["dist_good"] - grouped["dist_bad"]) * grouped["woe"]

    total_iv = grouped["iv"].sum()
    grouped["bad_rate"] = grouped["bad"] / grouped["total"]

    return grouped, total_iv


def calculate_all_iv(df, target, bins=10):
    """IV for every feature, sorted descending. Adds a human-readable strength label."""
    features = [c for c in df.columns if c != target]
    iv_results = []
    for feat in features:
        _, iv = calculate_woe_iv(df, feat, target, bins)
        iv_results.append({"Feature": feat, "IV": iv})

    iv_df = pd.DataFrame(iv_results).sort_values("IV", ascending=False).reset_index(drop=True)

    # standard IV interpretation buckets
    conditions = [
        iv_df["IV"] < 0.02,
        iv_df["IV"] < 0.1,
        iv_df["IV"] < 0.3,
        iv_df["IV"] < 0.5,
        iv_df["IV"] >= 0.5,
    ]
    iv_df["Strength"] = np.select(conditions,
        ["Useless", "Weak", "Medium", "Strong", "Suspicious"], default="Unknown")

    return iv_df


def woe_transform(X_train, X_test, y_train, target_col="TARGET", bins=10):
    """WoE-encode all features. Bins fitted on train, applied to both."""
    train_df = X_train.copy()
    train_df[target_col] = y_train.values

    woe_maps = {}
    X_train_woe = pd.DataFrame(index=X_train.index)
    X_test_woe = pd.DataFrame(index=X_test.index)

    for feat in X_train.columns:
        stats, _ = calculate_woe_iv(train_df, feat, target_col, bins)
        woe_map = stats["woe"].to_dict()
        woe_maps[feat] = woe_map

        if train_df[feat].nunique() <= bins:
            train_bins = train_df[feat]
            test_bins = X_test[feat]
        else:
            try:
                train_bins, bin_edges = pd.qcut(
                    train_df[feat], q=bins, duplicates="drop", retbins=True)
                bin_edges[0] = -np.inf
                bin_edges[-1] = np.inf
                test_bins = pd.cut(X_test[feat], bins=bin_edges)
            except ValueError:
                train_bins, bin_edges = pd.cut(
                    train_df[feat], bins=bins, retbins=True)
                bin_edges[0] = -np.inf
                bin_edges[-1] = np.inf
                test_bins = pd.cut(X_test[feat], bins=bin_edges)

        X_train_woe[feat] = train_bins.map(woe_map).fillna(0)
        X_test_woe[feat] = test_bins.map(woe_map).fillna(0)

    return X_train_woe, X_test_woe, woe_maps


def create_interaction_features(df):
    """
    Hand-crafted interaction features.
    These came from thinking about what actually drives credit risk —
    not just individual counts but combinations that tell a story.
    """
    df = df.copy()

    # someone with lots of 60-day lates AND recent 90-day lates = very bad
    df["delinquency_severity"] = df["TLDel60CntAll"] * df["TLDel90Cnt24"]

    # high utilization on many cards = financially stretched
    df["utilization_pressure"] = df["TLBalHCPct"] * df["TL75UtilCnt"]

    # lots of recent inquiries, especially finance-related = red flag
    df["inquiry_intensity"] = df["InqCnt06"] * df["InqFinanceCnt24"]

    # how long they've had credit
    df["credit_history_depth"] = df["TLTimeFirst"] - df["TLTimeLast"]

    # what fraction of their tradelines are bad
    df["bad_to_total_ratio"] = df["TLBadDerogCnt"] / (df["TLCnt"] + 1)

    # are they opening lots of new accounts relative to total? could be risky
    df["recent_activity_ratio"] = df["TLCnt24"] / (df["TLCnt"] + 1)

    return df


INTERACTION_FEATURES = [
    "delinquency_severity",
    "utilization_pressure",
    "inquiry_intensity",
    "credit_history_depth",
    "bad_to_total_ratio",
    "recent_activity_ratio",
]
