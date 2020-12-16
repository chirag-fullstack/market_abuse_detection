import logging

import pandas as pd

from clean_data import filter_unused_column, merge_stock_data, remove_blank_data
from fetch_external_data import fetch_data


logger = logging.getLogger(__name__)


# TODO
# Move this class to new file
class Rule:
    """This is a base class for rule
    if someone want to define new rule then they need to inherit this class and override filter_data method
    """

    subclasses = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @staticmethod
    def filter_data():
        pass


class PriceRule(Rule):
    """This class filter records according to price"""

    @staticmethod
    def filter_data(processed_df):
        """ The trader has submitted an order above the high price/below the low price for a given day of a stock"""
        filter_data = processed_df.query("price > High or  price < Low")
        return filter_data


class DateRule(Rule):
    """This class filter records according to date"""

    @staticmethod
    def filter_data(processed_df):
        """The trader has submitted an order in a date when the stock was not traded"""
        filter_data = processed_df[processed_df["High"].isnull()]
        return filter_data


class SuspiciousOrders:
    """This is a class to find suspicious trading """

    def __init__(self, symbol, input_filepath, start_date, end_date):
        """Initialize data
        Args:
            symbol(str): It is a symbol code
            input_filepath(str): It is a path of trade file
            start_date(str): Start date from which we need to do analysis
            end_date(str): end date till then we need to do analysis
        """
        self.rules = self.get_all_rules()
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.trade_data = self.get_trade_data(input_filepath)
        self.stock_data = self.get_stock_data()
        self.processed_df = None

    def clean_data(self):
        """This will clean data frame data and merge it"""
        if self.stock_data is None or self.trade_data is None:
            return
        self.trade_data = self.trade_data[self.trade_data["stockSymbol"] == self.symbol]
        self.trade_data = remove_blank_data(
            self.trade_data,
            [
                "tradeDatetime",
                "countryCode",
                "traderId",
                "stockSymbol",
                "price",
                "tradeDatetime",
            ],
        )

        # convert datetime string to date
        self.trade_data["tradeDay"] = pd.to_datetime(
            self.trade_data["tradeDatetime"], format="%Y-%m-%d"
        )
        self.trade_data["tradeDay"] = self.trade_data.tradeDay.values.astype("M8[D]")

        self.trade_data = filter_unused_column(
            self.trade_data, ["stockName", "volume", "stockSymbol", "tradeId"]
        )
        self.stock_data = filter_unused_column(
            self.stock_data, ["Volume", "Open", "Close", "Adj Close"]
        )

        # remove data which is not in given range
        mask = (self.trade_data["tradeDay"] >= self.start_date) & (
            self.trade_data["tradeDay"] <= self.end_date
        )
        self.trade_data = self.trade_data.loc[mask]

        # merge trade and stock data in to one data frame
        merged_df = merge_stock_data(self.trade_data, self.stock_data)

        # fillter dataframe according to define rules
        self.processed_df = self.filter_suspicious_orders(merged_df)

    def get_trade_data(self, input_filepath):
        """This will return data frame which will contain trade related data
        Args:
            input_filepath(str): file path where trade file is saved
        """
        # TODO
        # need to handle exceptions
        df_csv = pd.read_csv(input_filepath)
        return df_csv

    def get_stock_data(self):
        """This will return data frame which has stock related data"""
        return fetch_data(self.symbol, self.start_date, self.end_date)

    def filter_suspicious_orders(self, trade_df):
        """This will filter trade data according to rule define
        Args:
            trade_df(dataframe): It has merged data frame which has both trade and stock data
        """
        suspicious_dfs = []
        for rule in self.rules:
            suspicious_dfs.append(rule.filter_data(trade_df))
        return pd.concat(suspicious_dfs)

    def get_all_rules(self):
        """This will return list of all rule"""
        return Rule.subclasses

    def get_suspicious_traders(self):
        """This will give data related to suspicious trader"""
        if self.processed_df is None:
            logger.error("Data is not ready, so unable to get traders data")
            return
        self.processed_df["suspiciousOrdersCount"] = self.processed_df.groupby(
            "traderId"
        )["traderId"].transform("count")
        suspicious_traders = self.processed_df[
            self.processed_df["suspiciousOrdersCount"] > 1
        ]
        suspicious_traders = suspicious_traders.drop_duplicates(subset=["traderId"])
        return suspicious_traders.sort_values(
            by=["suspiciousOrdersCount"], ascending=False
        )

    def get_suspicious_countries(self):
        """This will give data related to suspicious trading according to countries """
        if self.processed_df is None:
            logger.error("Data is not ready, so unable to get countries data")
            return

        self.processed_df["suspiciousCountryCount"] = self.processed_df.groupby(
            "countryCode"
        )["countryCode"].transform("count")
        suspicious_countries = self.processed_df[
            self.processed_df["suspiciousCountryCount"] > 1
        ]
        suspicious_countries = suspicious_countries.drop_duplicates(
            subset=["countryCode"]
        )
        return suspicious_countries.sort_values(
            by=["suspiciousCountryCount"], ascending=False
        )
