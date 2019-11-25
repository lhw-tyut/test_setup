import os
import logging
import logging.config


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
            'filename': '/root/lhw/test_auto/test.log',
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
        'baremetal': {
            'level': 'DEBUG',
            'handlers': ['file', 'console']
            },
    }
}


def setup(path='/root/lhw/test_auto'):
    if not os.path.exists(path):
        os.makedirs(path)
    logging.config.dictConfig(LOG_SETTINGS)
    logger = logging.getLogger('baremetal')
    return logger
