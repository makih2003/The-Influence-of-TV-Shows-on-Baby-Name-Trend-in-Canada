import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu
import os
import matplotlib.pyplot as plt
import seaborn as sns
from config import RESULTS_DIR, PROCESSED_DATA_DIR


def run_mannwhitney(group, alpha=0.05):
    """
    Run Mann-Whitney U test to identify specific TV shows with increasing or decreasing trends 
    """
    pre = group[group['years_from_release'] < 0]['count']
    post = group[group['years_from_release'] >= 0]['count']

    # Test for increase (post > pre)
    _, p_greater = mannwhitneyu(post, pre, alternative='greater')
    # Test for decrease (post < pre)
    _, p_less = mannwhitneyu(post, pre, alternative='less')

    return pd.Series({
        'p_greater': p_greater,
        'significant_increase': p_greater < alpha,
        'p_less': p_less,
        'significant_decrease': p_less < alpha,
        'median_pre': pre.median(),
        'median_post': post.median()
    })


def analyze_name_trends(alpha=0.05):
    """
    1. A log-transformed two-sample t-test comparing all pre-release vs. post-release baby name counts to analyze overall trend.
    2. Mann-Whitney U tests for each (firstName, title) pair to detect significant individual increases or decreases in name usage.
    """
    filename = os.path.join(PROCESSED_DATA_DIR, 'name_trends.csv')
    df = pd.read_csv(filename)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Pre and post counts (raw)
    pre_all = df[df['years_from_release'] < 0]['count']
    post_all = df[df['years_from_release'] >= 0]['count']

    # Use log1p b/c values could be 0
    pre_log = np.log1p(pre_all)
    post_log = np.log1p(post_all)

    t_stat_log, p_val_log = ttest_ind(post_log, pre_log)
    print("\n########## Log-Transformed T-Test (Pre vs Post) ##########")
    print(f"p_value: {p_val_log}\n")
    print(f"Pre log-mean: {pre_log.mean():.2f}, Post log-mean: {post_log.mean():.2f}")

    # Run per-show Mann-Whitney tests
    grouped = df.groupby(['firstName', 'title'], group_keys=False)
    mannwhitney_results = grouped.apply(run_mannwhitney, alpha=alpha, include_groups=False).dropna().reset_index()

    # Filter significant increases
    significant_increase = mannwhitney_results[mannwhitney_results['significant_increase']]
    print(f"{len(significant_increase)} TV shows have a significant increase in baby name usage after release")
    print(significant_increase[['firstName', 'title', 'p_greater']].sort_values(by='p_greater', ascending=True).head(10))

    # Filter significant decreases
    significant_decrease = mannwhitney_results[mannwhitney_results['significant_decrease']]
    print(f"{len(significant_decrease)} TV shows have a significant decrease in baby name usage after release")
    print(significant_decrease[['firstName', 'title', 'p_less']].sort_values(by='p_less', ascending=True).head(10))

    # Save all results
    ind_trend = "individual_name_trend_results.csv"
    increase = "significant_name_increases.csv"
    decrease = "significant_name_decreases.csv"
    mannwhitney_results.to_csv(os.path.join(RESULTS_DIR, ind_trend), index=False)
    significant_increase.to_csv(os.path.join(RESULTS_DIR, increase), index=False)
    significant_decrease.to_csv(os.path.join(RESULTS_DIR, decrease), index=False)

    print("\nResults saved to:")
    print(f"- {RESULTS_DIR}/{ind_trend}")
    print(f"- {RESULTS_DIR}/{increase}")
    print(f"- {RESULTS_DIR}/{decrease}")

if __name__ == '__main__':
    analyze_name_trends()