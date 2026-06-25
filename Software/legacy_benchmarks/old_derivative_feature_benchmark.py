import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def calculate_ema_features(df, alpha=0.02):
    df_features = df.copy()
    
    df_features['Inner_Baseline'] = df_features['Inner_Env'].ewm(alpha=alpha, adjust=False).mean()
    df_features['Outer_Baseline'] = df_features['Outer_Env'].ewm(alpha=alpha, adjust=False).mean()
    
    df_features['Inner_Net'] = df_features['Inner_Env'] - df_features['Inner_Baseline']
    df_features['Outer_Net'] = df_features['Outer_Env'] - df_features['Outer_Baseline']
    
    df_features['Inner_Net'] = df_features['Inner_Net'].clip(lower=0)
    df_features['Outer_Net'] = df_features['Outer_Net'].clip(lower=0)
    
    return df_features

def run_ema_test(file_path):
    data = pd.read_csv(file_path)
    data_ema = calculate_ema_features(data, alpha=0.02)

    X_absolute = data[['Inner_Env', 'Outer_Env']]
    X_ema = data_ema[['Inner_Net', 'Outer_Net']]
    y = data['Label']

    X_abs_train, X_abs_test, y_train, y_test = train_test_split(X_absolute, y, test_size=0.3, random_state=42)
    X_ema_train, X_ema_test, _, _ = train_test_split(X_ema, y, test_size=0.3, random_state=42)

    rf_abs = RandomForestClassifier(random_state=42)
    rf_abs.fit(X_abs_train, y_train)
    pred_abs = rf_abs.predict(X_abs_test)
    acc_abs = accuracy_score(y_test, pred_abs)

    rf_ema = RandomForestClassifier(random_state=42)
    rf_ema.fit(X_ema_train, y_train)
    pred_ema = rf_ema.predict(X_ema_test)
    acc_ema = accuracy_score(y_test, pred_ema)

    print(f"Absolute_Acc: {acc_abs:.4f}")
    print(f"EMA_Net_Acc: {acc_ema:.4f}")

if __name__ == "__main__":
    run_ema_test("../GUI_application/sEMG_raw_datasets/il_data_1782283149_labelled.csv")