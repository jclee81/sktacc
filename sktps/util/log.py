# -*- coding: utf-8 -*-

import logging.config

from colorer import ColorStreamHandler

logging.ColorStreamHandler = ColorStreamHandler

log = logging.getLogger('sktps')
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem

    'formatters': {
        'old': {
            'format': '%(asctime)s [%(levelname)7s] -- %(message)s (%(filename)s:%(lineno)s)'
        },
        'standard': {
            'format': '%(asctime)s %(levelname)7s (%(filename)16s:%(lineno)4s): %(message)s'
        },
    },
    'handlers': {
        'console': {
            # 'level': 'WARNING',
            'level': 'INFO',
            'class': 'logging.ColorStreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'log.txt',
            'mode': 'a',
            # 'maxBytes': 10485760,
            # 'backupCount': 1,
        },
    },
    'loggers': {
        'sktps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
})

# coloredlogs.install(level='DEBUG')
# coloredlogs.install(level='DEBUG', logger=log)
