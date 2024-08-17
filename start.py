import subprocess

# 执行一个简单的命令
result = subprocess.run(['./stock-rest/manage.py runserver'], capture_output=True, text=True)