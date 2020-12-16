import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

import context  # noqa
from process_data import DateRule, PriceRule, SuspiciousOrders


class TurretTest(unittest.TestCase):
    @patch.object(SuspiciousOrders, "get_stock_data")
    @patch.object(SuspiciousOrders, "get_trade_data")
    def setUp(self, mock_data, mock_stock_data):
        self.symbol = "AMZN"
        self.input_filepath = "/home/test.csv"
        self.start_date = datetime(2020, 2, 1)
        self.end_date = datetime(2020, 3, 31)
        self.sus_order_obj = SuspiciousOrders(
            self.symbol, self.input_filepath, self.start_date, self.end_date
        )

    @patch("process_data.pd.read_csv")
    def test_get_trade_data(self, mock_read_csv):
        """Test get trade data"""
        expected_df = mock_read_csv.return_value = pd.DataFrame(
            {
                "column1": pd.Series([1.0, 2.0, 3.0]),
                "column2": pd.Series([4.0, 5.0, 6.0]),
            }
        )
        df = self.sus_order_obj.get_trade_data(self.input_filepath)
        pd.testing.assert_frame_equal(expected_df, df)
        mock_read_csv.assert_called_with(self.input_filepath)

    @patch("fetch_external_data.web.DataReader")
    def test_get_stock_data(self, mock_read_csv):
        """Test get stock data"""
        expected_df = mock_read_csv.return_value = pd.DataFrame(
            {
                "column1": pd.Series([1.0, 2.0, 3.0]),
                "column2": pd.Series([4.0, 5.0, 6.0]),
            }
        )
        df = self.sus_order_obj.get_stock_data()
        pd.testing.assert_frame_equal(expected_df, df)
        mock_read_csv.assert_called_with(
            data_source="yahoo",
            end=self.end_date.strftime("%Y-%m-%d"),
            name=self.symbol,
            start=self.start_date.strftime("%Y-%m-%d"),
        )

    def test_get_all_rules(self):
        """ Test get all rules"""
        rules = self.sus_order_obj.get_all_rules()
        self.assertListEqual(rules, [PriceRule, DateRule])

    def test_get_suspicious_traders_with_no_data(self):
        """ Test when we don't have data to process"""
        df = self.sus_order_obj.get_suspicious_traders()
        self.assertIsNone(df)

    def test_get_suspicious_traders_with_data(self):
        """test when we have data for process"""
        self.sus_order_obj.processed_df = pd.DataFrame(
            {"traderId": [1, 2, 3, 4, 5, 1, 3, 1, 4]}
        )
        df = self.sus_order_obj.get_suspicious_traders()
        expected_df = pd.DataFrame(
            {"traderId": [1, 3, 4], "suspiciousOrdersCount": [3, 2, 2]}
        )
        pd.testing.assert_frame_equal(
            expected_df.reset_index(drop=True), df.reset_index(drop=True)
        )

    # TODO
    # need to wrtie more testcases for other functions
