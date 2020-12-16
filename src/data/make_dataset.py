# -*- coding: utf-8 -*-
import logging
from datetime import date

import click

from process_data import SuspiciousOrders


@click.group()
def cli():
    pass


@click.command()
@click.argument("symbol")
@click.argument("input_filepath", type=click.Path(exists=True))
@click.option(
    "--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today())
)
@click.option(
    "--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today())
)
def detect_abuse(symbol, input_filepath, start_date, end_date):
    """It will help to detect market abuse
    Args:
        symbol(String): It is a stock symbol for which we want to detect abuse
        input_filepath(Path): Location of file which having trade data
        start_date(Date in Y-m-d): Start date for our analysis
        end_date(Date in Y-m-d): End date for our analysis
    """
    # TODO
    # Need to verify file extention should be csv.

    logger = logging.getLogger(__name__)
    suspicious_orders_obj = SuspiciousOrders(
        symbol, input_filepath, start_date, end_date
    )
    suspicious_orders_obj.clean_data()
    # TODO
    # for demo we just print it here we can also save it as a CSV or generate any report or graph
    logger.info("========== Suspicious traders =========== ")
    logger.info(suspicious_orders_obj.get_suspicious_traders())
    logger.info("========== Suspicious Country =========== ")
    logger.info(suspicious_orders_obj.get_suspicious_countries())


cli.add_command(detect_abuse)

if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    cli()
