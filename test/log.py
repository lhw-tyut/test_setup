import os
import logging
import logging.config

path=os.getcwd()
filename = os.path.join(os.getcwd(), 'test.log')

LOG_SETTINGS = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': filename,
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },

    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(levelname)s %(process)d \
%(name)s.%(lineno)d %(message)s',
        },
        'email': {
            'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n'
            'Line: %(lineno)d\nMessage: %(message)s',
        },
    },
    'loggers': {
        'test': {
            'level': 'DEBUG',
            'handlers': ['file', 'console']
            },
    }
}


def set_up(path=os.getcwd()):
    if not os.path.exists(path):
        os.makedirs(path)
    logging.config.dictConfig(LOG_SETTINGS)
    logger = logging.getLogger('test')
    return logger
