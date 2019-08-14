BitShares workers tests
==============

Contains tests related to BitShares workers


Execute following command for running tests:
$ python -m pytest -vvsl --show-capture=no --logger-logsdir=/path/to/project/logs smoke/

To turn off captured log, use following argument:
--show-capture=no

To show only step logs, use following argument:
--loggers=pytest_logger.STEPS