"""
connect to relative db
"""

def connect(type, connect_info_dic):
	return {
		"mysql": connect_mysql,
	}.get(type, connect_mysql)(connect_info_dic)

def connect_mysql(connect_info_dic):
        host = connect_info_dic['host']
        port = connect_info_dic['port']
        user = connect_info_dic['user']
        passwd = connect_info_dic['passwd']
        charset = connect_info_dic['charset']
        db = connect_info_dic['db']
    
        from webspider.utils.MysqlApi import MysqlApi
        conn = MysqlApi()
        conn.Connect(host=host, port=port, user=user, passwd=passwd,
                db=db, charset=charset)
        return conn

