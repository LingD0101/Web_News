from flask_script import Manager
from info import create_app

app = create_app('develop')
manage = Manager(app)



if __name__ == "__main__":
    manage.run()
