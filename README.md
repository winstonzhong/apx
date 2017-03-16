python 安装
1. pip install xxx

2. https://pypi.python.org/pypi 下载包; cmd进入目录以后, 使用 python setup.py install
==============================================================================


1. 下载项目:
	git clone git@github.com:winstonzhong/apx.git
	
	git pull origin dev
	
2. 导入至IDE

3. 更新数据库:
	python manage.py makemigrations   # 检测数据表的变化
	python manage.py migrate  # 同步数据库

4. 创建管理超级管理员
	python manage.py createsuperuser
	
5. 登录管理后台
	命令: python manage.py runserver
	访问连接: http://localhost:8000/admin/

6. 抓取姓名
	抓取姓名百度指数命令: python manage.py cmd --add <name>  参数: name 姓名

	抓取姓名百科数据及相关人物命令: python manage.py cmd --run <num>  参数: num 抓取条数
	
	英文名补丁: python manage.py cmd --patch

	常用英文名爬取: python manage.py cmd --import_english