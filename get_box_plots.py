import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from config import PLOTS_DIR, RESULTS_DIR, PROCESSED_DATA_DIR

def plot_boxplots(top_df, title, filename):
    # I referred code from: 
    # https://seaborn.pydata.org/generated/seaborn.boxplot.html?utm_source=chatgpt.com
    # https://stackoverflow.com/questions/45475962/how-to-add-value-labels-to-a-boxplot-using-the-hue-argument?utm_source=chatgpt.com
    labels = top_df[['firstName', 'title']].copy()
    labels['label'] = labels['firstName'] + '\n(' + labels['title'] + ')'

    merged = pd.merge(df, labels, on=['firstName', 'title'])
    merged['Period'] = np.where(merged['years_from_release'] < 0, 'Pre-Release', 'Post-Release')
    merged['Label'] = merged['firstName'] + '\n(' + merged['title'] + ')'

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=merged, x='Label', y='count', hue='Period')
    plt.title(title)
    plt.xlabel("Character Name (TV Show)")
    plt.ylabel("Baby Name Count")
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, filename))


if __name__ == '__main__':
    df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'name_trends.csv'))
    increase_df = pd.read_csv(os.path.join(RESULTS_DIR, 'significant_name_increases.csv'))
    decrease_df = pd.read_csv(os.path.join(RESULTS_DIR, 'significant_name_decreases.csv'))

    # Get top 5 based on lowest p-values
    top_inc = increase_df.sort_values(by='p_greater').head(5)
    top_dec = decrease_df.sort_values(by='p_less').head(5)
    plot_boxplots(top_inc, "Top 5 Increases in Baby Name Usage After Show Release", "top5_increases_boxplot.png")
    plot_boxplots(top_dec, "Top 5 Decreases in Baby Name Usage After Show Release", "top5_decreases_boxplot.png")