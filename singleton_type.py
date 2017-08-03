#!/usr/bin/python

class SingletonType(type):

    def __call__(cls, *args, **kargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kargs)
            return cls.__instance
