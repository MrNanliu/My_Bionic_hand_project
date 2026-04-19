import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def extract_window_features(df_label, window_size=50, step_size=25):
    features = []
    inner_data = df_label['Inner_Env'].values
    outer_data = df_label['Outer_Env'].values
    label = df_label['Label'].iloc[0]

    for i in range(0, len(df_label) - window_size, step_size):
        inner_window = inner_data[i : i + window_size]
        outer_window = outer_data[i : i + window_size]

        inner_rms = np.sqrt(np.mean(inner_window**2))
        outer_rms = np.sqrt(np.mean(outer_window**2))
        
        inner_mav = np.mean(np.abs(inner_window))
        outer_mav = np.mean(np.abs(outer_window))

        features.append([inner_rms, outer_rms, inner_mav, outer_mav, label])

    columns = ['Inner_RMS', 'Outer_RMS', 'Inner_MAV', 'Outer_MAV', 'Label']
    return pd.DataFrame(features, columns=columns)

file_path = r'E:\Bionic_hand\My_Bionic_hand_project\Software\data_collection\collected_data\raw_datasets\07_04_2026_(5)\il_data_1775547338_labelled.csv' # Specify the file path for the labelled dataset here.
df = pd.read_csv(file_path)

X_train_list, X_test_list, y_train_list, y_test_list = [], [], [], []

for label in df['Label'].unique():
    df_label = df[df['Label'] == label]
    
    feature_df = extract_window_features(df_label, window_size=50, step_size=25)
    
    X_label = feature_df.drop('Label', axis=1)
    y_label = feature_df['Label']
    
    split_index = int(len(X_label) * 0.7)
    
    X_train_list.append(X_label.iloc[:split_index])
    X_test_list.append(X_label.iloc[split_index:])
    
    y_train_list.append(y_label.iloc[:split_index])
    y_test_list.append(y_label.iloc[split_index:])

X_train = pd.concat(X_train_list, ignore_index=True)
X_test = pd.concat(X_test_list, ignore_index=True)
y_train = pd.concat(y_train_list, ignore_index=True)
y_test = pd.concat(y_test_list, ignore_index=True)

rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy after sliding window: {accuracy:.4f}")
print("\nClassification report:")
print(classification_report(y_test, y_pred))