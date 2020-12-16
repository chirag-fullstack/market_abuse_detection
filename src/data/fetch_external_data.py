import logging

from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError


logger = logging.getLogger(__name__)


def fetch_data(symbol, start_date, end_date):
    """This will fetch stock data from yahoo
    Args:
        symbol(str): company code/symbol
        start_date(str): start date from where we need data
        end_date(str): end date till that we need data
    """
    try:
        df = web.DataReader(
            name=symbol,
            data_source="yahoo",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )
        return df
    except RemoteDataError:
        logger.error("No information for stock '%s'" % symbol)
    # TODO
    # Need to handle few more exception like connection error, timeout
    # If we want to do multiple operations or some other option later then we can save this stock data into file
    # df.to_csv("../../data/external/{}.csv".format(symbol))
