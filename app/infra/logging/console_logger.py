import logging


class ConsoleLogger:
    def __init__(self, logger_name = 'default', log_level=logging.INFO):
        self.logger_name = logger_name
        self.logger = logging.getLogger(f'{self.logger_name}_console_logger')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)

    def log_debug(self, message: str):
        self.logger.debug(message)