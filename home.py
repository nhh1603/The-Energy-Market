class Home:
    def __init__(self, id, production_rate, consumption_rate, trading_policy):
        self.id = int(id)
        self.production_rate = int(production_rate)
        self.consumption_rate = int(consumption_rate)
        self.gap = int(self.production_rate - self.consumption_rate)
        self.trading_policy = int(trading_policy)
        self.exchange_market = 0
        if self.gap < 0:
            self.exchange_market = self.gap
        if self.trading_policy == 2:
            self.exchange_market = self.gap

    def update_home(self, new_production_rate_percentage, new_consumption_rate_percentage):
        self.production_rate = int(self.production_rate * (1 + new_production_rate_percentage))
        self.consumption_rate = int(self.consumption_rate * (1 + new_consumption_rate_percentage))
        self.gap = int(self.production_rate - self.consumption_rate)
        self.exchange_market = 0
        if self.gap < 0:
            self.exchange_market = self.gap
        if self.trading_policy == 2:
            self.exchange_market = self.gap

    def __str__(self):
        return (f"Home {self.id}: \nProduction Rate: {self.production_rate} Wh\nConsumption Rate: {self.consumption_rate} Wh\nGap: {self.gap} Wh\nTrading Policy: {self.trading_policy} \n")
