import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = '../data_collection/collected_data/raw_datasets/**/*_labelled.csv'
OUTPUT_DIR = '../data_collection/collected_data/benchmark_results'
FEATURE_COLS = ['Inner_Env', 'Outer_Env']
LABEL_COL = 'Label'

def calculate_rms(signal):
    return np.sqrt(np.mean(signal**2))

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_paths = glob.glob(DATA_DIR, recursive=True)
    labelled_files = [f for f in file_paths if f.endswith('_labelled.csv')]
    
    df_list = [pd.read_csv(f) for f in labelled_files]
    df = pd.concat(df_list, ignore_index=True).dropna(subset=FEATURE_COLS + [LABEL_COL])

    rest_data = df[df[LABEL_COL] == 0]
    noise_metrics = []
    for col in FEATURE_COLS:
        rms_val = calculate_rms(rest_data[col])
        peak_to_peak = rest_data[col].max() - rest_data[col].min()
        noise_metrics.append({'Channel': col, 'RMS_Noise': rms_val, 'Peak_to_Peak': peak_to_peak})
    
    noise_df = pd.DataFrame(noise_metrics)
    noise_df.to_csv(f"{OUTPUT_DIR}/noise_analysis.csv", index=False)
    print(f"Noise analysis saved to: {OUTPUT_DIR}/noise_analysis.csv")

    corr_matrix = df[FEATURE_COLS].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=0, vmax=1)
    plt.title('Channel Cross-talk (Correlation Matrix)')
    plt.savefig(f"{OUTPUT_DIR}/channel_correlation.png", dpi=300)
    print(f"Correlation heatmap saved to: {OUTPUT_DIR}/channel_correlation.png")

    snr_results = []
    active_data = df[df[LABEL_COL].isin([1, 2])]
    for col in FEATURE_COLS:
        signal_power = calculate_rms(active_data[col])
        noise_power = calculate_rms(rest_data[col])
        snr = 20 * np.log10(signal_power / noise_power) if noise_power > 0 else 0
        snr_results.append({'Channel': col, 'SNR_dB': snr})
    
    snr_df = pd.DataFrame(snr_results)
    snr_df.to_csv(f"{OUTPUT_DIR}/snr_analysis.csv", index=False)
    print(f"SNR analysis saved to: {OUTPUT_DIR}/snr_analysis.csv")

if __name__ == "__main__":
    main()