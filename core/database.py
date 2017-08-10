from sylfk.dbconnector import BaseDB

db_user = 'root'
db_password = ''
db_database = "shiyanlou"

try:
	dbconn = BaseDB(db_user, db_password, db_database)

except Exception as e:
	code, _ = e.args
	print('code %s' % code)
	if code == 1049 or code == 1146:
		create_table = '''
				CREATE TABLE user (
				id INT PRIMARY KEY AUTO_INCREMENT,
				f_name VARCHAR(50) UNIQUE
				) CHARSET=utf8
				'''

		dbconn = BaseDB(db_user, db_password)
		ret = dbconn.create_db(db_database)

		if ret.suc:
			ret = dbconn.choose_db(db_database)
			if ret.suc:
				# 创建数据表
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