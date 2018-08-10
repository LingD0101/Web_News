from flask_script import Manager
from info import create_app    # 导入工厂函数

app = create_app('develop')
manage = Manager(app)

if __name__ == "__main__":
    manage.run()
