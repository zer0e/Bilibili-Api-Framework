import logging
import logging.config

logging.config.fileConfig('logger.conf')
logger = logging.getLogger(__name__)