import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def plot_confusion_matrix(csv_path):
    df = pd.read_csv(csv_path)
    X = df[['Inner_Env', 'Outer_Env', 'Ratio', 'Inner_Var', 'Outer_Var']]
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)

    cm = confusion_matrix(y_test, pred, labels=rf.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=rf.classes_)
    disp.plot(cmap=plt.cm.Blues)
    plt.show()

if __name__ == "__main__":
    plot_confusion_matrix("../GUI_application/sEMG_raw_datasets/il_data_1782372689_labelled.csv")