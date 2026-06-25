import os
import numpy as np
from imblearn.under_sampling import RandomUnderSampler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def extract_advanced_features(window):
    features = []
    for i in range(window.shape[1]):
        ch_data = window[:, i]
        mean = np.mean(ch_data)
        std = np.std(ch_data)
        rms = np.sqrt(np.mean(ch_data**2))
        zcr = np.sum(np.diff(np.signbit(ch_data - mean)))
        wl = np.sum(np.abs(np.diff(ch_data)))
        features.extend([mean, std, rms, zcr, wl])
    return features

def build_dual_track_datasets(data_dir, window_size=40, step=10):
    X_cnn, X_ml, Y = [], [], []
    allowed_gestures = {"open_hand", "fist", "pinch", "wrist_up", "wrist_down"}

    for root, dirs, files in os.walk(data_dir):
        if "archive_raw" in dirs:
            dirs.remove("archive_raw")

        gesture_label = os.path.basename(root).lower()
        if gesture_label not in allowed_gestures:
            continue

        for file in files:
            if not file.endswith('.txt'):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, 'r') as f:
                    content = f.read()
                content = content.replace('\\n', ' ').replace('\n', ' ')
                data = np.fromstring(content, sep=' ')
                if data.size == 0 or data.shape[0] % 6 != 0:
                    continue
                data = data.reshape(-1, 6)
                
                n_samples = len(data)
                if n_samples < window_size:
                    continue
                for start in range(0, n_samples - window_size + 1, step):
                    window = data[start:start+window_size]
                    X_cnn.append(window.T)
                    X_ml.append(extract_advanced_features(window))
                    Y.append(gesture_label)
            except Exception:
                pass

    return np.array(X_cnn), np.array(X_ml), np.array(Y)

def visualize_data(X_ml, Y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_ml)
    
    plt.figure(figsize=(12, 6))
    plt.boxplot(X_scaled, showfliers=False)
    plt.title("Feature Distribution")
    plt.xlabel("Feature Index")
    plt.ylabel("Standardised Value")
    plt.show()
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=Y, alpha=0.6)
    plt.title("PCA Projection of Magnetic-based Muscle Deformation Features")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.show()
    
    corr = np.corrcoef(X_scaled.T)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap='coolwarm')
    plt.title("Feature Correlation Heatmap")
    plt.show()

if __name__ == "__main__":
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "EMG_raw_datasets"))
    
    X_cnn, X_ml, Y = build_dual_track_datasets(dataset_path)
    
    visualize_data(X_ml, Y)
    
    rus = RandomUnderSampler(random_state=42)
    
    X_cnn_reshaped = X_cnn.reshape(X_cnn.shape[0], -1)
    X_cnn_res, Y_res = rus.fit_resample(X_cnn_reshaped, Y)
    X_cnn_res = X_cnn_res.reshape(-1, 6, 40)
    
    X_ml_res, _ = rus.fit_resample(X_ml, Y)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    np.save(os.path.join(current_dir, "X_cnn_raw.npy"), X_cnn_res)
    np.save(os.path.join(current_dir, "X_ml_features.npy"), X_ml_res)
    np.save(os.path.join(current_dir, "Y_labels.npy"), Y_res)