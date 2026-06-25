import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def extract_new_features(df, window=15):
    df_feat = df.copy()
    
    df_feat['Ratio'] = df_feat['Inner_Env'] / (df_feat['Outer_Env'] + 1e-6)
    
    df_feat['Inner_Var'] = df_feat['Inner_Env'].rolling(window=window, min_periods=1).var().fillna(0)
    df_feat['Outer_Var'] = df_feat['Outer_Env'].rolling(window=window, min_periods=1).var().fillna(0)
    
    return df_feat

def run_advanced_test(file_path):
    data = pd.read_csv(file_path)
    data_advanced = extract_new_features(data, window=15)

    X_abs = data[['Inner_Env', 'Outer_Env']]
    X_adv = data_advanced[['Inner_Env', 'Outer_Env', 'Ratio', 'Inner_Var', 'Outer_Var']]
    y = data['Label']

    X_abs_train, X_abs_test, y_train, y_test = train_test_split(X_abs, y, test_size=0.3, random_state=42)
    X_adv_train, X_adv_test, _, _ = train_test_split(X_adv, y, test_size=0.3, random_state=42)

    rf_abs = RandomForestClassifier(random_state=42)
    rf_abs.fit(X_abs_train, y_train)
    pred_abs = rf_abs.predict(X_abs_test)
    
    rf_adv = RandomForestClassifier(random_state=42)
    rf_adv.fit(X_adv_train, y_train)
    pred_adv = rf_adv.predict(X_adv_test)

    print(f"Absolute_Acc: {accuracy_score(y_test, pred_abs):.4f}")
    print(f"Advanced_Features_Acc: {accuracy_score(y_test, pred_adv):.4f}")

if __name__ == "__main__":
    run_advanced_test("../GUI_application/sEMG_raw_datasets/il_data_1782287796_labelled.csv")