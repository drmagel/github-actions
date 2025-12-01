import logging
from pythonjsonlogger import jsonlogger


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return '/alive' not in record.getMessage()

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname


appLogger = logging.getLogger()
appLogger.setLevel(logging.DEBUG)
appLogger.addFilter(HealthCheckFilter())

logHandler = logging.StreamHandler()

formatter = CustomJsonFormatter("%(message)s", timestamp=True)
logHandler.setFormatter(formatter)

appLogger.addHandler(logHandler)
