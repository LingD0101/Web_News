from flask_script import Manager
from info import create_app, db    # 导入工厂函数
from flask_migrate import Migrate, MigrateCommand

app = create_app('develop')
manage = Manager(app)
Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == "__main__":
    print(app.url_map)
    manage.run()
