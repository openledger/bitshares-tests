import logging
from utils.step_generator import StepGenerator


msg_fmt = '%(asctime)s |  %(funcName)-25s |  %(levelname)-5s |%(message)s'


class PrettyFormatter(logging.Formatter):
    def __init__(self):
        super(PrettyFormatter, self).__init__(msg_fmt,
                                              datefmt='%Y/%m/%d %H:%M:%S')


setattr(logging, 'STEPS', 25)
logging.addLevelName(logging.STEPS, 'STEPS')
logger = logging.getLogger('pytest_logger')
logger.setLevel(logging.DEBUG)


def log_step(message):
    step_generator = StepGenerator()
    step_number = step_generator.increment()
    logger.log(25, '=== Step %s. %s' % (step_number, message))


# Add key that below to CLI command for showing only test steps messages
# --loggers=pytest_logger.STEPS
