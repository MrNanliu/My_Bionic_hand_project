import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

def train_svm_model(data_path):
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Dataset {data_path} not found.")
        return

    df['Diff'] = df['Inner_Env'] - df['Outer_Env']
    df['Ratio'] = df['Inner_Env'] / (df['Outer_Env'] + 1e-5)
    df['Sum'] = df['Inner_Env'] + df['Outer_Env']

    clean_df = df[df['Label'].isin([1, 2, 3, 4])].copy()

    X = clean_df[['Inner_Env', 'Outer_Env', 'Diff', 'Ratio', 'Sum']]
    y = clean_df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training SVM classifier with class balancing...")
    svm_clf = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced')
    svm_clf.fit(X_train_scaled, y_train)

    y_pred = svm_clf.predict(X_test_scaled)

    print("\n--- Model Evaluation ---")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Fist (1)', 'Wrist Up (2)', 'Wrist Down (3)', 'Pinch (4)'], zero_division=0))

if __name__ == "__main__":
    dataset_file = r'YOUR_NEW_CSV_PATH_HERE.csv'
    train_svm_model(dataset_file)