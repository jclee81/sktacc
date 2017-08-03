#!/usr/bin/python

import pymysql
import inspect
from singleton_type import SingletonType

class DBManager(object):
    __metaclass__ = SingletonType

    def __init__(self, h,u,p,d,c):
        self._conn = conn = pymysql.connect(host=h,user=u,password=p,db=d,charset=c)
        self._cursor = conn.cursor()
        self._bind_cursor = conn.cursor(pymysql.cursors.DictCursor)

    def __del__(self):
        if self._conn is not None:
            self._conn.close()

    def executeSQL(self, sql):
        try:
            self._cursor.execute(sql)
        except Exception as e:
            print "[== Error occurred in '%s'.'%s' SQL is '%s' ==]" % \
                (self.__class__,inspect.stack()[0][3], sql)
            raise

    def executeSQLWithParams(self, sql, params):
        try:
            self._bind_cursor.execute(sql, params)
        except Exception as e:
            print "[== Error occurred in '%s'.'%s' SQL is '%s' ==]" % \
                (self.__class__,inspect.stack()[0][3], sql)
            raise

    def fetchAll(self):
        return self._cursor.fetchall()

    def fetchAllWithParams(self):
        return self._bind_cursor.fetchall()

    def getCursor(self):
        return self._cursor
