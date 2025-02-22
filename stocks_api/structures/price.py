from datetime import datetime

class Price:
    def __init__(self, price: float, timestamp: datetime):
        self.price = price
        self.timestamp = timestamp

    def __str__(self):
        return f"Current price {self.price}, current time {self.timestamp}"