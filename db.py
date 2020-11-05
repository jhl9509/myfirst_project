import pymysql
import pandas as pd


class MysqlController:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost',
                                    user='root',
                                    password='',
                                    db='wallet',
                                    charset='utf8')  # 데이터베이스 기본정보
        self.curs = self.conn.cursor()

    def new_node(self,id,ssoin):
        sql = "INSERT INTO info VALUES('"+id+"',0);"
        self.curs.execute(sql)
        self.conn.commit()
        
        
    def mining(self,address):
        self.myamount = "select ssoin from info where id = '"+address+"';"
        self.curs.execute(self.myamount)
        self.row=self.curs.fetchone()
        # fetchone()
        # fetchmany()
        # fetchall()
        self.real = int(self.row[0]) + 1
        sql = "UPDATE info SET ssoin = " + str(self.real) + " WHERE id = '"+address+"';"
        self.curs.execute(sql)
        self.conn.commit()
        return self.real
    
    def trade(self,sender,recipient,ssoin):
        sql1 = "update info set ssoin = ssoin + "+ssoin+" where id = '"+recipient+"';"
        self.curs.execute(sql1)       
        sql2 = "update info set ssoin = ssoin - "+ssoin+" where id = '"+sender+"';"
        self.curs.execute(sql2)
        self.conn.commit()
        