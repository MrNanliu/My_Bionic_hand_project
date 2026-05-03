import pandas as pd
import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_DIR = '../data_collection/collected_data/raw_datasets/**/*_labelled.csv'
FEATURE_COLS = ['Inner_Env', 'Outer_Env']
LABEL_COL = 'Label'

def apply_simple_dsp(df, window=10):
    proc_df = df.copy()
    for col in FEATURE_COLS:
        proc_df[col] = proc_df[col].rolling(window=window, min_periods=1).mean()
    return proc_df

def evaluate(train_x, test_x, train_y, test_y):
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(train_x, train_y)
    preds = rf.predict(test_x)
    return accuracy_score(test_y, preds)

def main():
    file_paths = glob.glob(DATA_DIR, recursive=True)
    all_raw = []
    all_proc = []
    
    for f in file_paths:
        if f.endswith('_labelled.csv'):
            df = pd.read_csv(f)
            all_raw.append(df)
            all_proc.append(apply_simple_dsp(df))
            
    if not all_raw:
        return

    full_raw = pd.concat(all_raw, ignore_index=True).dropna()
    full_proc = pd.concat(all_proc, ignore_index=True).dropna()

    split_idx = int(len(full_raw) * 0.8)
    
    acc_raw = evaluate(
        full_raw[FEATURE_COLS].iloc[:split_idx], full_raw[FEATURE_COLS].iloc[split_idx:],
        full_raw[LABEL_COL].iloc[:split_idx], full_raw[LABEL_COL].iloc[split_idx:]
    )
    
    acc_proc = evaluate(
        full_proc[FEATURE_COLS].iloc[:split_idx], full_proc[FEATURE_COLS].iloc[split_idx:],
        full_proc[LABEL_COL].iloc[:split_idx], full_proc[LABEL_COL].iloc[split_idx:]
    )

    print("=" * 40)
    print("W18 FINAL BENCHMARK (Time-based Split)")
    print(f"Raw Accuracy: {acc_raw:.2%}")
    print(f"Processed Accuracy (Simple MA): {acc_proc:.2%}")
    print("=" * 40)

if __name__ == "__main__":
    main()