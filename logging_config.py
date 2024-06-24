import logging
import sys

class Logging:

    @staticmethod
    def set_logging():
        logging.basicConfig(level=logging.INFO, 
            format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
            stream=sys.stdout)
        logger = logging.getLogger('vara-backend')

        return logger
        