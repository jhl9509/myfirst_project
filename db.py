import pymysql
import pandas as pd


class MysqlController:
    def __init__(self, host, id, pw, db_name):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    user='root',
                                    password='',
                                    db='wallet',
                                    charset='utf8')  # 데이터베이스 기본정보
        curs = self.conn.cursor()    
        sql = "select * from info"   
        curs.execute(sql)
