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
FEATURE_COLS = ['Inner_Env', 'Outer_Env']
LABEL_COL = 'Label'

OUTPUT_DIR = '../data_collection/collected_data/benchmark_results'
OUTPUT_METRICS_PATH = f'{OUTPUT_DIR}/metrics_summary.csv'
OUTPUT_PLOT_PATH = f'{OUTPUT_DIR}/confusion_matrices.png'

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
    combined_df = combined_df.dropna(subset=FEATURE_COLS + [LABEL_COL])
    
    X = combined_df[FEATURE_COLS].values
    y = combined_df[LABEL_COL].values
    
    return X, y

def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        'Model': model_name,
        'Accuracy': acc,
        'Precision (Macro)': precision,
        'Recall (Macro)': recall,
        'F1-Score (Macro)': f1
    }
    
    return metrics, cm

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading datasets...")
    X, y = load_and_preprocess_data()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    svm_clf = SVC(kernel='rbf', class_weight='balanced', random_state=42)
    rf_clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    
    print("Training SVM...")
    svm_clf.fit(X_train_scaled, y_train)
    svm_metrics, svm_cm = evaluate_model(svm_clf, X_test_scaled, y_test, 'SVM')
    
    print("Training Random Forest...")
    rf_clf.fit(X_train_scaled, y_train)
    rf_metrics, rf_cm = evaluate_model(rf_clf, X_test_scaled, y_test, 'Random Forest')
    
    metrics_df = pd.DataFrame([svm_metrics, rf_metrics])
    metrics_df.to_csv(OUTPUT_METRICS_PATH, index=False)
    print(f"Metrics saved to: {OUTPUT_METRICS_PATH}")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    gesture_labels = ['Rest', 'Fist', 'Open']
    
    sns.heatmap(svm_cm, annot=True, fmt='d', cmap='Blues', ax=axes[0], 
                xticklabels=gesture_labels, yticklabels=gesture_labels)
    axes[0].set_title('SVM Confusion Matrix')
    axes[0].set_ylabel('True Label')
    axes[0].set_xlabel('Predicted Label')
    
    sns.heatmap(rf_cm, annot=True, fmt='d', cmap='Greens', ax=axes[1], 
                xticklabels=gesture_labels, yticklabels=gesture_labels)
    axes[1].set_title('Random Forest Confusion Matrix')
    axes[1].set_ylabel('True Label')
    axes[1].set_xlabel('Predicted Label')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_PATH, dpi=300)
    print(f"Confusion matrices saved to: {OUTPUT_PLOT_PATH}")

if __name__ == "__main__":
    main()