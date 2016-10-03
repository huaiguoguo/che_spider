# coding:utf-8
import pymysql


class DB(object):
    def __init__(self, host,port, user, password, dbname, charset='utf-8'):
        if host is None or user is None or password is None or dbname is None:
            return None

        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbname, charset=charset)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)


        # self.cur.execute("select version()")
        #
        # for i in self.cur:
        #     print(i)
        # self.cur.close()

    def execute(self, sql, params):
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.lastrowid

    def executemany(self, sql, params):
        self.cur.executemany(sql, params)
        self.conn.commit()
        return self.cur.lastrowid

    def select(self, sql, param=None):
        self.cur.execute(sql,param)
        return self.cur.fetchall()
