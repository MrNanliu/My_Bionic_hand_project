import os
import pickle
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class EMGCNN(nn.Module):
    def __init__(self, num_classes=5):
        super(EMGCNN, self).__init__()
        self.conv1 = nn.Conv1d(6, 16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool1d(2)
        self.dropout = nn.Dropout(0.3)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32 * 10, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.pool1(self.relu(self.conv1(x)))
        x = self.pool2(self.relu(self.conv2(x)))
        x = self.dropout(x)
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

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
                    window = window - np.mean(window, axis=0)
                    X.append(window.T)
                    Y.append(label_idx)
            except Exception:
                pass
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.int64)

def train():
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
        print("No valid dataset directory found.")
        return

    print(f"Dataset path located: {base_dir}")

    gestures = ["open_hand", "fist", "pinch", "wrist_up", "wrist_down"]
    X, Y = load_dataset(base_dir, gestures)
    
    if len(X) == 0:
        print("No valid dataset files found.")
        return

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)

    N, C, L = X_train.shape
    X_train_flat = X_train.reshape(-1, C * L)
    X_test_flat = X_test.reshape(-1, C * L)

    scaler = StandardScaler()
    X_train_flat = scaler.fit_transform(X_train_flat)
    X_test_flat = scaler.transform(X_test_flat)

    X_train = X_train_flat.reshape(-1, C, L)
    X_test = X_test_flat.reshape(-1, C, L)

    train_dataset = TensorDataset(torch.tensor(X_train), torch.tensor(Y_train))
    test_dataset = TensorDataset(torch.tensor(X_test), torch.tensor(Y_test))

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    model = EMGCNN(num_classes=5)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(50):
        model.train()
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            out = model(batch_x)
            loss = criterion(out, batch_y)
            loss.backward()
            optimizer.step()

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            out = model(batch_x)
            _, predicted = torch.max(out.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    print(f"Test Accuracy: {100 * correct / total:.2f}%")

    output_dir = os.path.abspath(os.path.join(script_dir, ".."))
    torch.save(model.state_dict(), os.path.join(output_dir, "emg_cnn_model.pth"))
    with open(os.path.join(output_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    print(f"Saved model and scaler to {output_dir}")

if __name__ == "__main__":
    train()