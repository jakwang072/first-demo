import unittest
from account import Account # Assuming account.py is in the same directory or accessible via PYTHONPATH
from decimal import Decimal, getcontext

# Set precision for Decimal calculations if needed, though direct float comparison might be okay for this context if not financial grade
# getcontext().prec = 28 

class TestAccountInitialization(unittest.TestCase):
    def test_initialization(self):
        acc = Account()
        self.assertEqual(acc.dates, [])
        self.assertEqual(acc.daily_cash, {})
        self.assertEqual(acc.daily_total_position_value, {})
        self.assertEqual(acc.daily_position_info, {})
        self.assertEqual(acc.daily_transactions, {})
        self.assertEqual(acc.daily_orders, {})

class TestAddDailyData(unittest.TestCase):
    def setUp(self):
        self.acc = Account()

    def test_add_single_day_data(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [{'sec': 'A'}], [{'tx': '1'}], [{'ord': 'A'}])
        self.assertEqual(self.acc.dates, ['2023-01-01'])
        self.assertEqual(self.acc.daily_cash['2023-01-01'], 1000)
        self.assertEqual(self.acc.daily_total_position_value['2023-01-01'], 500)
        self.assertEqual(self.acc.daily_position_info['2023-01-01'], [{'sec': 'A'}])
        self.assertEqual(self.acc.daily_transactions['2023-01-01'], [{'tx': '1'}])
        self.assertEqual(self.acc.daily_orders['2023-01-01'], [{'ord': 'A'}])

    def test_add_multiple_days_data(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], [])
        self.acc.add_daily_data('2023-01-03', 1200, 600, [], [], [])
        self.acc.add_daily_data('2023-01-02', 1100, 550, [], [], [])
        
        self.assertEqual(self.acc.dates, ['2023-01-01', '2023-01-02', '2023-01-03']) # Test sorting
        self.assertEqual(self.acc.daily_cash['2023-01-01'], 1000)
        self.assertEqual(self.acc.daily_cash['2023-01-02'], 1100)
        self.assertEqual(self.acc.daily_cash['2023-01-03'], 1200)

    def test_overwrite_data_for_existing_day(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], [])
        self.acc.add_daily_data('2023-01-01', 1500, 700, [{'sec': 'B'}], [], [])
        
        self.assertEqual(self.acc.dates, ['2023-01-01'])
        self.assertEqual(self.acc.daily_cash['2023-01-01'], 1500)
        self.assertEqual(self.acc.daily_total_position_value['2023-01-01'], 700)
        self.assertEqual(self.acc.daily_position_info['2023-01-01'], [{'sec': 'B'}])

class TestCalculateDailyTotalAssets(unittest.TestCase):
    def setUp(self):
        self.acc = Account()
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], [])
        self.acc.add_daily_data('2023-01-02', 2000, 0, [], [], [])
        self.acc.add_daily_data('2023-01-03', 0, 1500, [], [], [])

    def test_day_with_data(self):
        self.assertEqual(self.acc.calculate_daily_total_assets('2023-01-01'), 1500)

    def test_day_with_no_data(self):
        self.assertEqual(self.acc.calculate_daily_total_assets('2023-01-04'), 0)

    def test_day_with_cash_zero_position_value(self):
        self.assertEqual(self.acc.calculate_daily_total_assets('2023-01-02'), 2000)

    def test_day_with_position_value_zero_cash(self):
        self.assertEqual(self.acc.calculate_daily_total_assets('2023-01-03'), 1500)

class TestCalculateDailyReturn(unittest.TestCase):
    def setUp(self):
        self.acc = Account()

    def test_consecutive_days_valid_assets(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], []) # Assets = 1500
        self.acc.add_daily_data('2023-01-02', 1100, 550, [], [], []) # Assets = 1650
        # Return = (1650 - 1500) / 1500 = 150 / 1500 = 0.1
        self.assertAlmostEqual(self.acc.calculate_daily_return('2023-01-02'), 0.1)

    def test_first_day_of_data(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], [])
        self.assertEqual(self.acc.calculate_daily_return('2023-01-01'), 0.0)

    def test_previous_day_assets_zero(self):
        self.acc.add_daily_data('2023-01-01', 0, 0, [], [], []) # Assets = 0
        self.acc.add_daily_data('2023-01-02', 100, 50, [], [], []) # Assets = 150
        self.assertEqual(self.acc.calculate_daily_return('2023-01-02'), 0.0)

    def test_current_day_assets_zero_previous_had_assets(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], []) # Assets = 1500
        self.acc.add_daily_data('2023-01-02', 0, 0, [], [], []) # Assets = 0
        # Return = (0 - 1500) / 1500 = -1.0
        self.assertAlmostEqual(self.acc.calculate_daily_return('2023-01-02'), -1.0)
    
    def test_current_day_no_data_at_all(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], [])
        self.assertEqual(self.acc.calculate_daily_return('2023-01-02'), 0.0)

    def test_missing_day_between_data(self):
        self.acc.add_daily_data('2023-01-01', 1000, 500, [], [], []) # Assets = 1500
        self.acc.add_daily_data('2023-01-03', 1100, 550, [], [], []) # Assets = 1650
        # Previous day for 2023-01-03 is 2023-01-01
        # Return = (1650 - 1500) / 1500 = 0.1
        self.assertAlmostEqual(self.acc.calculate_daily_return('2023-01-03'), 0.1)

class TestRecordBuyTransaction(unittest.TestCase):
    def setUp(self):
        self.acc = Account()
        # Initial cash for some tests
        self.acc.add_daily_data('2023-01-01', 10000, 0, [], [], [])

    def test_simple_buy_transaction(self):
        date = '2023-01-01'
        self.acc.record_buy_transaction(date, 'SEC001', 'TestSec', 10, 50, 5, 1) # Cost = 10*50 + 5 + 1 = 506
        
        self.assertEqual(self.acc.daily_cash[date], 10000 - 506)
        
        position = self.acc.daily_position_info[date][0]
        self.assertEqual(position['security_code'], 'SEC001')
        self.assertEqual(position['quantity'], 10)
        self.assertEqual(position['average_cost'], 50)
        
        self.assertEqual(self.acc.daily_total_position_value[date], 10 * 50)
        
        transaction = self.acc.daily_transactions[date][0]
        self.assertEqual(transaction['type'], 'buy')
        self.assertEqual(transaction['security_code'], 'SEC001')
        self.assertEqual(transaction['quantity'], 10)
        self.assertEqual(transaction['price'], 50)

    def test_buy_more_of_existing_security(self):
        date = '2023-01-01'
        self.acc.record_buy_transaction(date, 'SEC001', 'TestSec', 10, 50, 0, 0) # Initial buy: 10 shares @ 50
        self.acc.record_buy_transaction(date, 'SEC001', 'TestSec', 10, 60, 0, 0) # Second buy: 10 shares @ 60
        
        # Cash: 10000 - (10*50) - (10*60) = 10000 - 500 - 600 = 8900
        self.assertEqual(self.acc.daily_cash[date], 8900)
        
        position = self.acc.daily_position_info[date][0]
        self.assertEqual(position['quantity'], 20)
        # Avg cost: ((10*50) + (10*60)) / 20 = (500 + 600) / 20 = 1100 / 20 = 55
        self.assertEqual(position['average_cost'], 55)
        
        self.assertEqual(self.acc.daily_total_position_value[date], 20 * 55)

    def test_buy_insufficient_funds(self):
        date = '2023-01-01'
        with self.assertRaises(ValueError) as context:
            self.acc.record_buy_transaction(date, 'SEC002', 'TestSec2', 100, 200, 0, 0) # Cost = 20000
        self.assertTrue("Insufficient funds" in str(context.exception))

    def test_buy_on_new_date(self):
        date = '2023-01-02' # New date
        self.acc.record_buy_transaction(date, 'SEC003', 'TestSec3', 5, 100, 0, 0) # Cost = 500
        
        self.assertIn(date, self.acc.dates)
        self.assertEqual(self.acc.daily_cash[date], -500) # Initial cash for new date is 0
        
        position = self.acc.daily_position_info[date][0]
        self.assertEqual(position['quantity'], 5)
        self.assertEqual(position['average_cost'], 100)
        self.assertEqual(self.acc.daily_total_position_value[date], 500)
        self.assertTrue(len(self.acc.daily_transactions[date]) == 1)

class TestRecordSellTransaction(unittest.TestCase):
    def setUp(self):
        self.acc = Account()
        # Initial setup: 10000 cash, 20 shares of SEC001 @ 50 (total value 1000)
        self.acc.add_daily_data('2023-01-01', 10000, 1000, 
                                [{'security_code': 'SEC001', 'security_name': 'TestSec', 'quantity': 20, 'average_cost': 50}], 
                                [], [])

    def test_sell_part_of_position(self):
        date = '2023-01-01'
        # Sell 10 shares @ 60. Proceeds = 10*60 - 5 - 1 - 2 - 2 = 600 - 10 = 590
        self.acc.record_sell_transaction(date, 'SEC001', 10, 60, 5, 1, 2, 2) 
        
        self.assertEqual(self.acc.daily_cash[date], 10000 + 590)
        
        position = self.acc.daily_position_info[date][0]
        self.assertEqual(position['quantity'], 10) # 20 - 10
        self.assertEqual(position['average_cost'], 50) # Average cost doesn't change on sell
        
        # Total position value = 10 * 50 = 500
        self.assertEqual(self.acc.daily_total_position_value[date], 500)
        
        transaction = self.acc.daily_transactions[date][0]
        self.assertEqual(transaction['type'], 'sell')
        self.assertEqual(transaction['quantity'], 10)
        self.assertEqual(transaction['price'], 60)

    def test_sell_entire_position(self):
        date = '2023-01-01'
        # Sell all 20 shares @ 60. Proceeds = 20*60 = 1200 (assuming no fees for simplicity here)
        self.acc.record_sell_transaction(date, 'SEC001', 20, 60, 0,0,0,0) 
        
        self.assertEqual(self.acc.daily_cash[date], 10000 + 1200)
        self.assertEqual(self.acc.daily_position_info[date], []) # Position removed
        self.assertEqual(self.acc.daily_total_position_value[date], 0)

    def test_sell_security_not_owned(self):
        date = '2023-01-01'
        with self.assertRaises(ValueError) as context:
            self.acc.record_sell_transaction(date, 'SEC002', 10, 60, 0,0,0,0)
        self.assertTrue("Security SEC002 not found" in str(context.exception))

    def test_sell_more_shares_than_owned(self):
        date = '2023-01-01'
        with self.assertRaises(ValueError) as context:
            self.acc.record_sell_transaction(date, 'SEC001', 25, 60, 0,0,0,0) # Own 20, try to sell 25
        self.assertTrue("Not enough shares of SEC001 to sell" in str(context.exception))

    def test_sell_on_new_date(self):
        # This scenario is tricky: you can't sell if positions are not carried over or re-initialized for the new date.
        # The current _ensure_date_initialized sets up empty positions for a new date.
        # So, selling on a new date without prior positions for that date should fail.
        new_date = '2023-01-02'
        with self.assertRaises(ValueError) as context:
            self.acc.record_sell_transaction(new_date, 'SEC001', 5, 60, 0,0,0,0)
        # This will be "No positions found for this date to sell from." OR "Security SEC001 not found..."
        # depending on exact path in record_sell_transaction for a new date.
        # _ensure_date_initialized creates empty daily_position_info for new_date.
        # So, positions = self.daily_position_info.get(date) will return []
        self.assertTrue("No positions found for this date to sell from." in str(context.exception) or \
                        "Security SEC001 not found" in str(context.exception))

        # To properly test selling on a new date, one might first need to carry over positions or add_daily_data for that new date.
        # For example:
        self.acc.add_daily_data(new_date, self.acc.daily_cash['2023-01-01'], 
                                self.acc.daily_total_position_value['2023-01-01'],
                                list(self.acc.daily_position_info['2023-01-01']), # Deep copy if mutable elements
                                [], [])
        
        # Now sell on new_date
        self.acc.record_sell_transaction(new_date, 'SEC001', 5, 60, 0,0,0,0) # Proceeds = 300
        self.assertEqual(self.acc.daily_cash[new_date], self.acc.daily_cash['2023-01-01'] + 300)
        position_on_new_date = self.acc.daily_position_info[new_date][0]
        self.assertEqual(position_on_new_date['quantity'], 15) # 20 - 5


if __name__ == '__main__':
    unittest.main()
```
