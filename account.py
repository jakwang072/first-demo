class Account:
    def __init__(self):
        self.dates = []
        self.daily_cash = {}
        self.daily_total_position_value = {}
        self.daily_position_info = {}
        self.daily_transactions = {}
        self.daily_orders = {}

    def add_daily_data(self, date, cash, total_position_value, position_info, transactions, orders):
        if date not in self.dates:
            self.dates.append(date)
            self.dates.sort() # Keep dates sorted
        
        self.daily_cash[date] = cash
        self.daily_total_position_value[date] = total_position_value
        self.daily_position_info[date] = position_info
        self.daily_transactions[date] = transactions
        self.daily_orders[date] = orders

    def calculate_daily_total_assets(self, date):
        cash = self.daily_cash.get(date)
        total_position_value = self.daily_total_position_value.get(date)

        if cash is None or total_position_value is None:
            return 0
        
        return cash + total_position_value

    def calculate_daily_return(self, date):
        current_day_assets = self.calculate_daily_total_assets(date)

        # No data for current date
        if current_day_assets == 0 and date not in self.daily_cash: 
            return 0.0

        try:
            current_date_index = self.dates.index(date)
        except ValueError:
            # Date not in records, implies no assets or data for this date.
            # calculate_daily_total_assets would return 0, but good to handle explicitly.
            return 0.0

        if current_date_index == 0:
            # It's the first date, no previous day to compare against
            return 0.0
        
        previous_date = self.dates[current_date_index - 1]
        previous_day_assets = self.calculate_daily_total_assets(previous_date)

        if previous_day_assets == 0:
            # Avoid division by zero.
            # This could also signify a large influx of assets if previous was genuinely 0.
            # For now, returning 0.0 as per instructions.
            return 0.0
        
        daily_return = (current_day_assets - previous_day_assets) / previous_day_assets
        return daily_return

    def _ensure_date_initialized(self, date):
        if date not in self.dates:
            self.dates.append(date)
            self.dates.sort()
            # Initialize other daily attributes if this is a new date
            self.daily_cash.setdefault(date, 0.0)
            self.daily_total_position_value.setdefault(date, 0.0)
            self.daily_position_info.setdefault(date, [])
            self.daily_transactions.setdefault(date, [])
            self.daily_orders.setdefault(date, []) # Assuming orders might also need initialization

    def _recalculate_daily_total_position_value(self, date):
        total_value = 0.0
        for position in self.daily_position_info.get(date, []):
            total_value += position['quantity'] * position['average_cost'] # Using average_cost as per instruction
        self.daily_total_position_value[date] = total_value

    def record_buy_transaction(self, date, security_code, security_name, quantity, price_per_unit, commission, other_fees):
        self._ensure_date_initialized(date)

        transaction_cost = (quantity * price_per_unit) + commission + other_fees

        if self.daily_cash.get(date, 0) < transaction_cost:
            raise ValueError("Insufficient funds to make purchase.")
        self.daily_cash[date] -= transaction_cost

        positions = self.daily_position_info.setdefault(date, [])
        found_position = False
        for pos in positions:
            if pos['security_code'] == security_code:
                old_quantity = pos['quantity']
                old_average_cost = pos['average_cost']
                pos['quantity'] += quantity
                # Ensure not to divide by zero if new quantity is zero (though for a buy, it shouldn't be)
                if pos['quantity'] != 0:
                    pos['average_cost'] = ((old_quantity * old_average_cost) + (quantity * price_per_unit)) / pos['quantity']
                else:
                    # This case should ideally not happen for a buy unless quantity was negative
                    # Or if old_quantity + quantity results in 0, which means old_quantity was -quantity
                    pos['average_cost'] = 0 
                found_position = True
                break
        
        if not found_position:
            positions.append({
                'security_code': security_code,
                'security_name': security_name,
                'quantity': quantity,
                'average_cost': price_per_unit
            })
        
        self._recalculate_daily_total_position_value(date)

        transaction = {
            'type': 'buy',
            'security_code': security_code,
            'security_name': security_name,
            'quantity': quantity,
            'price': price_per_unit,
            'amount': quantity * price_per_unit,
            'commission': commission,
            'other_fees': other_fees
        }
        self.daily_transactions.setdefault(date, []).append(transaction)

    def record_sell_transaction(self, date, security_code, quantity_sold, price_per_unit, commission, other_fees, stamp_duty, transfer_fee):
        self._ensure_date_initialized(date)

        transaction_proceeds = (quantity_sold * price_per_unit) - commission - other_fees - stamp_duty - transfer_fee
        
        self.daily_cash.setdefault(date, 0.0) # Ensure cash for date exists
        self.daily_cash[date] += transaction_proceeds

        positions = self.daily_position_info.get(date)
        if not positions:
            raise ValueError("No positions found for this date to sell from.")

        found_position_idx = -1
        for idx, pos in enumerate(positions):
            if pos['security_code'] == security_code:
                if pos['quantity'] < quantity_sold:
                    raise ValueError(f"Not enough shares of {security_code} to sell. Available: {pos['quantity']}, Tried to sell: {quantity_sold}")
                pos['quantity'] -= quantity_sold
                if pos['quantity'] == 0:
                    found_position_idx = idx # Mark for removal
                break
        else: # for-else: executed if loop didn't break (security not found)
            raise ValueError(f"Security {security_code} not found in positions for date {date}.")

        if found_position_idx != -1:
            positions.pop(found_position_idx)
        
        self._recalculate_daily_total_position_value(date)

        transaction = {
            'type': 'sell',
            'security_code': security_code,
            'quantity': quantity_sold,
            'price': price_per_unit,
            'amount': quantity_sold * price_per_unit,
            'commission': commission,
            'other_fees': other_fees,
            'stamp_duty': stamp_duty,
            'transfer_fee': transfer_fee
        }
        self.daily_transactions.setdefault(date, []).append(transaction)
