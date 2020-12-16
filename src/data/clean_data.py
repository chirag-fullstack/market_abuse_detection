# This is a utility file to clean our dataframes


def remove_blank_data(df, columns):
    """It is a generic function which remove null rows from data frame
    Agrs:
        df(DataFrame): It is data frame
        columns(list): It is a list of column name from which we need to remove missing data
    """
    for column in columns:
        df = df[df[column].notnull()]
    return df


def filter_unused_column(df, columns):
    """It is a generic function which remove column from given data frame
    Args:
        df(DataFrame): It is data frame
        columns(list): It is a list of column name which we want to remove
    """

    return df.drop(columns=columns)


def merge_stock_data(trade_df, stock_df):
    """This function will merge stock data with trade data
    Args:
        trade_df(DataFrame): Trade related dataframe
        stock_df(DataFrame): stock related dataframe

    """
    merged_df = trade_df.merge(
        stock_df, left_on="tradeDay", right_on="Date", how="left"
    )
    return merged_df
