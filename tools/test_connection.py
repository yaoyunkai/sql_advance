"""
https://peps.python.org/pep-0249/
https://dev.mysql.com/doc/dev/mysql-server/latest/ server - client protocol


Cursor 是一个什么概念????
    总结起来，不同的 cursor 对象在 MySQL 中并不代表不同的会话，
    它们只是在同一个会话中的不同游标，用于执行并行的查询和操作，共享同一个连接状态。

DictCursor的概念

怎么样开启事务  Transaction
    以cursor为单位


怎么样获取autocommit flag: get_autocommit


dictfetchall

executemany:

c.executemany(
      "INSERT INTO breakfast (name, spam, eggs, sausage, price)
      VALUES (%s, %s, %s, %s, %s)",
      [
      ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
      ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
      ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
      ] )



Created at 2023/7/24
"""
import pprint

import MySQLdb


def test_character_set():
    conn = MySQLdb.connect(host='localhost', port=3306, db='sql_adv',
                           user='root', password='password')
    # print('Connection autocommit mode: {}'.format(conn.autocommit()))
    # op(conn)

    # 获取什么变量??
    # print(conn.character_set_name())

    # conn.begin()

    # get autocommit
    print('Conn autocommit mode: {}'.format(conn.get_autocommit()))

    try:
        cursor = conn.cursor()
        cursor.execute(r"SHOW SESSION VARIABLES LIKE 'character\_set\_%';")
        rows = cursor.fetchall()
        pprint.pprint(rows)
    except:
        pass
    finally:
        conn.close()


if __name__ == '__main__':
    test_character_set()
