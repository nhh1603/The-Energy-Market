class Market:

    current_price = 0.15
    atten_coeff = 0.99

    def calculate_price(self, int_factors, ext_factors):
        for int in int_factors:
            int_term += int.coeff * int

        self.current_price = self.atten_coeff * self.current_price

    def deal(self, home, type):
        if type == 'buy':
            
    

    