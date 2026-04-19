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

    clean_df = df[df['Label'] != 0].copy()

    X = clean_df[['Inner_Env', 'Outer_Env']]
    y = clean_df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
    print(classification_report(y_test, y_pred, target_names=['Fist (1)', 'Open (2)'], zero_division=0))

if __name__ == "__main__":
    dataset_file = r'E:\Bionic_hand\My_Bionic_hand_project\Software\data_collection\collected_data\raw_datasets\07_04_2026_(5)\il_data_1775547338_labelled.csv'
    train_svm_model(dataset_file)