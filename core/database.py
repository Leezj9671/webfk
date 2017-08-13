from sylfk.dbconnector import BaseDB

db_user = 'root'
db_password = 'toor'
db_database = "shiyanlou"
db_add = '192.168.64.130'

try:
	dbconn = BaseDB(db_user, db_password, db_database, db_add)

except Exception as e:
	code, _ = e.args
	if code == 1049:
		create_table = '''
				CREATE TABLE user (
				id INT PRIMARY KEY AUTO_INCREMENT,
				f_name VARCHAR(50) UNIQUE
				) CHARSET=utf8
				'''

		dbconn = BaseDB(db_user, db_password, '', db_add)
		print('creating database..')
		ret = dbconn.create_db(db_database)
		print(ret.suc)
		if ret.suc:
			print('choose db')
			ret = dbconn.choose_db(db_database)
			if ret.suc:
				# 创建数据表
				print('create table')
				ret = dbconn.execute(create_table)

		else:
			dbconn.drop_db(db_database)
			# LOG
			print(ret.error.args)
			exit()
	else:
		# LOG
		print(e)
		exit()