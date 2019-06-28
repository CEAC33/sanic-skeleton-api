import os
from sanic.log import logger

async def check_connection(config):
    hostname = config.ES_HOST
    response = os.system("ping -c 1 " + hostname)

    #and then check the response...
    if response == 0:
        logger.info('{} is available'.format(hostname))
        return 'up'
    else:
        logger.info('{} is not available'.format(hostname))
        return 'down'