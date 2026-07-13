import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler

def extract_advanced_features(window):
    features = []
    for i in range(window.shape[1]):
        ch_data = window[:, i]
        rms = np.sqrt(np.mean(ch_data**2))
        mav = np.mean(np.abs(ch_data))
        wl = np.sum(np.abs(np.diff(ch_data)))
        zcr = np.sum(np.diff(np.sign(ch_data)) != 0)
        std = np.std(ch_data)
        features.extend([rms, mav, wl, zcr, std])
    return features

def load_dataset(base_dir, gestures):
    X = []
    Y = []
    for label_idx, gesture in enumerate(gestures):
        folder_path = os.path.join(base_dir, gesture)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if not fname.endswith(".txt"):
                continue
            file_path = os.path.join(folder_path, fname)
            try:
                data = []
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().replace("\\n", "\n")
                    for line in content.splitlines():
                        line = line.strip()
                        if line:
                            vals = [float(x) for x in line.split()]
                            if len(vals) == 6:
                                data.append(vals)
                data_arr = np.array(data)
                if len(data_arr) < 40:
                    continue
                for i in range(0, len(data_arr) - 40 + 1, 5):
                    window = data_arr[i : i + 40].copy()
                    for ch in range(6):
                        med = np.median(window[:, ch])
                        mask = np.abs(window[:, ch] - med) > 120
                        window[mask, ch] = med
                    
                    feats = extract_advanced_features(window)
                    X.append(feats)
                    Y.append(label_idx)
            except Exception:
                pass
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.int64)

def train_rf_cv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.abspath(os.path.join(script_dir, "..", "..", "EMG_raw_datasets")),
        os.path.abspath(os.path.join(script_dir, "..", "sEMG_raw_datasets")),
        os.path.abspath(os.path.join(script_dir, "..", "EMG_raw_datasets")),
    ]
    base_dir = None
    for path in possible_paths:
        if os.path.exists(path):
            base_dir = path
            break
    if base_dir is None:
        return 0.0

    gestures = ["open_hand", "fist", "pinch", "wrist_up", "wrist_down"]
    X, Y = load_dataset(base_dir, gestures)
    if len(X) == 0:
        return 0.0

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_scaled, Y, cv=cv, n_jobs=-1)
    mean_acc = scores.mean()

    model.fit(X_scaled, Y)

    output_dir = os.path.abspath(os.path.join(script_dir, ".."))
    with open(os.path.join(output_dir, "rf_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    with open(os.path.join(output_dir, "rf_scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
        
    return mean_acc

if __name__ == "__main__":
    acc = train_rf_cv()
    print(f"RF 5-Fold CV Accuracy: {acc * 100:.2f}%")