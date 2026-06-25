import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def process_dataset(input_filepath):
    try:
        df = pd.read_csv(input_filepath)
    except FileNotFoundError:
        print(f"Error: The file {input_filepath} could not be found.")
        return

    df['Label'] = 0

    fist_threshold = 0.18
    open_threshold = 0.28

    fist_condition = (df['Index_Dist'] < fist_threshold) & (df['Mid_Dist'] < fist_threshold)
    df.loc[fist_condition, 'Label'] = 1

    open_condition = (df['Index_Dist'] > open_threshold) & (df['Mid_Dist'] > open_threshold)
    df.loc[open_condition, 'Label'] = 2

    base_dir = os.path.dirname(input_filepath)
    base_name = os.path.basename(input_filepath).replace('.csv', '')
    
    output_csv = os.path.join(base_dir, f"{base_name}_labelled.csv")
    output_png = os.path.join(base_dir, f"{base_name}_preview.png")

    df.to_csv(output_csv, index=False)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    time_axis = df['Timestamp'] - df['Timestamp'].iloc[0]

    ax1.plot(time_axis, df['Inner_Env'], label='Inner_Env (Flexor)', color='red', alpha=0.7)
    ax1.plot(time_axis, df['Outer_Env'], label='Outer_Env (Extensor)', color='blue', alpha=0.7)
    ax1.set_ylabel('sEMG Envelope')
    ax1.legend(loc='upper right')
    ax1.set_title('sEMG Envelopes over Time')
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.plot(time_axis, df['Index_Dist'], label='Index Distance', color='green')
    ax2.plot(time_axis, df['Mid_Dist'], label='Mid Distance', color='orange')
    ax2.axhline(y=fist_threshold, color='black', linestyle='--', alpha=0.5, label='Fist Threshold (0.15)')
    ax2.axhline(y=open_threshold, color='grey', linestyle='--', alpha=0.5, label='Open Threshold (0.35)')
    ax2.set_ylabel('Distance (Ground Truth)')
    ax2.legend(loc='upper right')
    ax2.set_title('Finger Distances with Thresholds')
    ax2.grid(True, linestyle='--', alpha=0.6)

    ax3.plot(time_axis, df['Label'], label='Discrete Label (0=Rest, 1=Fist, 2=Open)', color='purple', drawstyle='steps-post')
    ax3.set_ylabel('Label')
    ax3.set_xlabel('Time (s)')
    ax3.set_yticks([0, 1, 2])
    ax3.legend(loc='upper right')
    ax3.set_title('Generated SVM Labels')
    ax3.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_png)
    plt.close()

    total_rows = len(df)
    fist_count = len(df[df['Label'] == 1])
    open_count = len(df[df['Label'] == 2])
    rest_count = len(df[df['Label'] == 0])
    
    print(f"Processed file: {input_filepath}")
    print(f"Total rows: {total_rows}")
    print(f"Fist states (1): {fist_count}")
    print(f"Open states (2): {open_count}")
    print(f"Transition/Rest (0): {rest_count}")
    print(f"Outputs saved to: {base_dir}")
    print("-" * 40)

if __name__ == "__main__":
    target_file = r'E:\Bionic_hand\My_Bionic_hand_project\Software\data_collection\collected_data\raw_datasets\07_04_2026_(5)\il_data_1775547338.csv'
    process_dataset(target_file)