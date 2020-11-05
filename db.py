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
        
    def new_node(self,id):
        sql = "INSERT INTO info(id,ssoin) VALUES(%s,%s)"
        self.curs.execute(sql,(id,))
        self.conn.commit()
        
        
    def mineing(self):
        sql = "UPDATE info SET "
    
    
    def trade(self,sender,recipient):
        # 보낸이의 코인을 빼주자
        # 받는이의 코인을 더해주자
        sql = "UPDATE info SET sender = sender.ssoin + "
