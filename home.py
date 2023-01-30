class Home:
    def __init__(self, id, production_rate, consumption_rate, trading_policy):
        self.id = int(id)
        self.production_rate = round(production_rate, 3)
        self.consumption_rate = round(consumption_rate, 3)
        self.gap = round(self.production_rate - self.consumption_rate, 3)
        self.trading_policy = int(trading_policy)
        self.exchange_market = 0
        if self.gap < 0:
            self.exchange_market = self.gap
        if self.trading_policy == 2:
            self.exchange_market = self.gap

    def update_rates(self, new_production_rate, new_consumption_rate):
        self.production_rate = round(new_production_rate, 3)
        self.consumption_rate = round(new_consumption_rate, 3)
        self.gap = round(new_production_rate - new_consumption_rate, 3)

    def set_exchange_market(self, exchange_market):
        self.exchange_market = exchange_market

    def __str__(self):
        return (f"Home {self.id}: \nProduction Rate: {self.production_rate} \nConsumption Rate: {self.consumption_rate} \nGap: {self.gap} \nTrading Policy: {self.trading_policy} \n")
