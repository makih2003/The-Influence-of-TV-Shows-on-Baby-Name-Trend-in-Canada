import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import normaltest, levene
from config import PLOTS_DIR, PROCESSED_DATA_DIR

def check_ttest_assumptions(transform=None):
    """
    Test for normality and equal variance
    Support transformations: None, sqrt, or log
    Generate histograms to visualize distributions and assess normality
    """
    filename = os.path.join(PROCESSED_DATA_DIR, "name_trends.csv")
    df = pd.read_csv(filename)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    if transform == 'sqrt':
        df['target'] = np.sqrt(df['count'])
    elif transform == 'log':
        df['target'] = np.log1p(df['count'])
    else:
        df['target'] = df['count']

    pre = df[df['years_from_release'] < 0]['target']
    post = df[df['years_from_release'] >= 0]['target']

    label = 'original' if transform is None else transform

    print(f"\nTesting Assumptions for T-Test ({label})")

    ### Normality Tests
    stat_pre, p_pre = normaltest(pre)
    stat_post, p_post = normaltest(post)

    print(f"Normality test (Pre-release): p-value = {p_pre}")
    print(f"Normality test (Post-release): p-value = {p_post}")

    ### Levene’s Test for Equal Variance
    stat_lev, p_lev = levene(pre, post)
    print(f"Levene test for equal variance: p-value = {p_lev}")

    ## Plot histogram to visualize normality
    plt.figure(figsize=(6, 4))
    sns.histplot(pre, bins=30, kde=True, color='darkblue', label='Pre-Release')
    sns.histplot(post, bins=30, kde=True, color='red', label='Post-Release ')
    plt.title(f'Baby Name Counts Pre vs Post ({label})')
    plt.xlabel('Transformed Baby Name Count' if transform else 'Baby Name Count')
    plt.ylabel('Frequency of Name-Year Entries')
    plt.legend()
    plt.savefig(os.path.join(PLOTS_DIR, f"histogram_{label}.png"))

if __name__ == '__main__':
    check_ttest_assumptions(transform=None)
    check_ttest_assumptions(transform='log')
    check_ttest_assumptions(transform='sqrt')