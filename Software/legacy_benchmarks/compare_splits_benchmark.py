import pandas as pd
import numpy as np
import glob
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = '../data_collection/collected_data/raw_datasets/**/*_labelled.csv'
OUTPUT_DIR = '../data_collection/collected_data/benchmark_results_engineered'
FEATURE_COLS = ['Inner_Env', 'Outer_Env', 'Diff', 'Ratio', 'Sum']
LABEL_COL = 'Label'

def load_and_preprocess_data():
    file_paths = glob.glob(DATA_DIR, recursive=True)
    labelled_files = [f for f in file_paths if f.endswith('_labelled.csv')]
    
    if not labelled_files:
        raise FileNotFoundError("No labelled datasets found. Please check DATA_DIR.")

    df_list = []
    for file in labelled_files:
        df = pd.read_csv(file)
        df_list.append(df)
        
    combined_df = pd.concat(df_list, ignore_index=True)
    
    combined_df['Diff'] = combined_df['Inner_Env'] - combined_df['Outer_Env']
    combined_df['Ratio'] = combined_df['Inner_Env'] / (combined_df['Outer_Env'] + 1e-5)
    combined_df['Sum'] = combined_df['Inner_Env'] + combined_df['Outer_Env']

    combined_df = combined_df.dropna(subset=FEATURE_COLS + [LABEL_COL])
    
    X = combined_df[FEATURE_COLS].values
    y = combined_df[LABEL_COL].values
    
    return X, y

def evaluate_model(model, X_test, y_test, model_name, split_strategy):
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        'Split_Strategy': split_strategy,
        'Model': model_name,
        'Accuracy': acc,
        'Precision (Macro)': precision,
        'Recall (Macro)': recall,
        'F1-Score (Macro)': f1
    }
    
    return metrics, cm

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Loading datasets and calculating engineered features...")
    X, y = load_and_preprocess_data()
    
    strategies = {
        'Random_Split': train_test_split(X, y, test_size=0.2, random_state=42, stratify=y),
        'Time_Based_Split': train_test_split(X, y, test_size=0.2, shuffle=False)
    }
    
    all_metrics = []
    all_cms = {}
    
    for strategy_name, (X_train, X_test, y_train, y_test) in strategies.items():
        print(f"\n--- Running Pipeline for: {strategy_name} ---")
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        svm_clf = SVC(kernel='rbf', class_weight='balanced', random_state=42)
        rf_clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
        
        print("Training SVM...")
        svm_clf.fit(X_train_scaled, y_train)
        svm_metrics, svm_cm = evaluate_model(svm_clf, X_test_scaled, y_test, 'SVM', strategy_name)
        all_metrics.append(svm_metrics)
        all_cms[f"{strategy_name}_SVM"] = svm_cm
        
        print("Training Random Forest...")
        rf_clf.fit(X_train_scaled, y_train)
        rf_metrics, rf_cm = evaluate_model(rf_clf, X_test_scaled, y_test, 'Random Forest', strategy_name)
        all_metrics.append(rf_metrics)
        all_cms[f"{strategy_name}_RF"] = rf_cm

    metrics_df = pd.DataFrame(all_metrics)
    metrics_csv_path = f"{OUTPUT_DIR}/comprehensive_metrics_summary.csv"
    metrics_df.to_csv(metrics_csv_path, index=False)
    print(f"\nComprehensive metrics saved to: {metrics_csv_path}")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    gesture_labels = ['Rest', 'Fist', 'Open']
    
    plot_configs = [
        ('Random_Split_SVM', axes[0, 0], 'Blues', 'Random Split: SVM'),
        ('Random_Split_RF', axes[0, 1], 'Greens', 'Random Split: Random Forest'),
        ('Time_Based_Split_SVM', axes[1, 0], 'Blues', 'Time-Based Split: SVM'),
        ('Time_Based_Split_RF', axes[1, 1], 'Greens', 'Time-Based Split: Random Forest')
    ]
    
    for key, ax, cmap, title in plot_configs:
        try:
            sns.heatmap(all_cms[key], annot=True, fmt='d', cmap=cmap, ax=ax, 
                        xticklabels=gesture_labels, yticklabels=gesture_labels)
        except ValueError:
            sns.heatmap(all_cms[key], annot=True, fmt='d', cmap=cmap, ax=ax)
        ax.set_title(title)
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
        
    plt.tight_layout()
    cm_plot_path = f"{OUTPUT_DIR}/comparison_confusion_matrices.png"
    plt.savefig(cm_plot_path, dpi=300)
    print(f"Comparison confusion matrices saved to: {cm_plot_path}")

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=metrics_df, x='Model', y='Accuracy', hue='Split_Strategy', palette='Set2')
    plt.title('Accuracy Drop: Random Split vs Time-Based Split (Signal Drift Impact)')
    plt.ylim(0, 1)

    for container in ax.containers:
        ax.bar_label(container, fmt='%.3f', padding=3)
    
    bar_plot_path = f"{OUTPUT_DIR}/accuracy_drop_comparison.png"
    plt.savefig(bar_plot_path, dpi=300)
    print(f"Accuracy drop bar chart saved to: {bar_plot_path}")

if __name__ == "__main__":
    main()