import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

class ComplaintPredictor:
    def __init__(self):
        self.model = Prophet(seasonality_mode='multiplicative')
        
    def train(self, complaints_data):
        """Train with historical data: [['date', 'complaints']]"""
        df = pd.DataFrame(complaints_data, columns=['ds', 'y'])
        self.model.fit(df)
    
    def predict_next_week(self):
        future = self.model.make_future_dataframe(periods=7)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat']].tail(7).to_dict('records')

# Sample Ahmednagar data
ahmednagar_data = [
    {'ds': '2024-01-01', 'y': 12},
    {'ds': '2024-01-02', 'y': 15},
    # Add minimum 30 days data
]
