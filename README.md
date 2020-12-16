Market Abuse Detection
==============================

How to install

Create virtual env and activate it.

`pip install requirements.txt`


How to run 

GO into src/data dir and run below command

`python make_dataset.py detect-abuse AMZN /home/deqode/datas/market_abuse_detection/data/raw/traders_data.csv --start-date 2020-02-01  --end-date 2020-03-31`

`detect-abuse` take 4 parama in which two are optional

`python make_dataset.py detect-abuse --help`





