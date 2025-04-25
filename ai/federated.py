import numpy as np
import tensorflow as tf

class FederatedTrainer:
    def __init__(self):
        self.global_model = self._build_model()
        
    def _build_model(self):
        """Simple model for demonstration"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(16, activation='relu', input_shape=(10,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        return model
    
    def aggregate(self, client_weights):
        """Proper weight averaging"""
        # Convert to numpy arrays first
        client_weights = [np.array(w, dtype=np.float32) for w in client_weights]
        return np.mean(client_weights, axis=0).tolist()
