import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def train_model(csv_path, model_out_path):
    df = pd.read_csv(csv_path)
    X = df[['Inner_Env', 'Outer_Env', 'Ratio', 'Inner_Var', 'Outer_Var']]
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    rf_eval = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_eval.fit(X_train, y_train)
    pred = rf_eval.predict(X_test)
    print(f"Validation_Accuracy: {accuracy_score(y_test, pred):.4f}")

    rf_prod = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_prod.fit(X, y)
    
    joblib.dump(rf_prod, model_out_path)

if __name__ == "__main__":
    train_model("../../GUI_application/sEMG_raw_datasets/il_data_1782375915_labelled.csv", "../../GUI_application/emg_gesture_model.pkl")