import joblib
import numpy as np

class ModelHandler:
    def __init__(self, mode='RF'):
        self.mode = mode
        if mode == 'RF':
            self.model = joblib.load('emg_gesture_model.pkl')
        else:
            self.model = joblib.load('svm_emg_model.pkl')

    def predict(self, features):
        feat_array = np.array(features).reshape(1, -1)
        return self.model.predict(feat_array)[0]