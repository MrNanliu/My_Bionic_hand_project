import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

sns.set_theme(style="whitegrid")

file_path = r'F:\Bionic_hand_project\My_Bionic_hand_project\Software\data_collection\collected_data\raw_datasets\17_04_2026_(4)\il_data_1775547338_labelled.csv'
df = pd.read_csv(file_path)

df = df[df['Label'].isin([1, 2])].copy()

X_train_list, X_test_list, y_train_list, y_test_list = [], [], [], []

for label in [1, 2]:
    df_label = df[df['Label'] == label]
    X_label = df_label.drop(['Label', 'Timestamp', 'Index_Dist', 'Mid_Dist', 'Ring_Dist', 'Pinky_Dist'], axis=1, errors='ignore')
    y_label = df_label['Label']
    
    split_index = int(len(X_label) * 0.7)
    
    X_train_list.append(X_label.iloc[:split_index])
    X_test_list.append(X_label.iloc[split_index:])
    y_train_list.append(y_label.iloc[:split_index])
    y_test_list.append(y_label.iloc[split_index:])

X_train = pd.concat(X_train_list, ignore_index=True)
X_test = pd.concat(X_test_list, ignore_index=True)
y_train = pd.concat(y_train_list, ignore_index=True)
y_test = pd.concat(y_test_list, ignore_index=True)

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

print(f"--- Random Forest Evaluation ---")
print(f"Model accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Fist (1)', 'Open (2)']))

importances = rf_model.feature_importances_
feature_importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': importances}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(8, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance_df, palette='viridis', hue='Feature', legend=False)
plt.title('Feature Importance')
plt.show()