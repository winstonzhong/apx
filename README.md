1. 下载项目:
	git clone git@github.com:winstonzhong/apx.git
	
2. 导入至IDE

3. 更新数据库:
	python manage.py makemigrations   # 检测数据表的变化
	python manage.py migrate  # 同步数据库

4. 创建管理超级管理员
	python manage.py creatsuperuser
	
5. 登录管理后台
	命令: python manage.py runserver
	访问连接: http://localhost:8000/admin/

6. 抓取姓名
	命令: python manage.py cmd --name <name>  参数: name 姓名