import logging
from wallet.settings import BASE_DIR
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO,
                    filemode='a',
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    encoding='utf-8')


class BaseLogger(ABC):
    logger = None
    handler = None
    formatter = None

    @classmethod
    @abstractmethod
    def debug(cls, message):
        cls.logger.debug(message)

    @classmethod
    @abstractmethod
    def info(cls, message):
        cls.logger.info(message)

    @classmethod
    @abstractmethod
    def error(cls, message):
        cls.logger.error(message)

    @classmethod
    @abstractmethod
    def warning(cls, message):
        cls.logger.warning(message)

    @classmethod
    @abstractmethod
    def critical(cls, message):
        cls.logger.critical(message)

    @classmethod
    @abstractmethod
    def exception(cls, message):
        cls.logger.exception(message)


class AuthenticationApiLogger(BaseLogger, ABC):
    logger = logging.getLogger('AuthenticationApiLogger')
    handler = logging.FileHandler(BASE_DIR / 'logs' / 'authentication_api.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TransactionApiLogger(BaseLogger, ABC):
    logger = logging.getLogger('TransactionApiLogger')
    handler = logging.FileHandler(BASE_DIR / 'logs' / 'transaction_api.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class PaymentApiLogger(BaseLogger, ABC):
    logger = logging.getLogger('PaymentApiLogger')
    handler = logging.FileHandler(BASE_DIR / 'logs' / 'payment_api.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
