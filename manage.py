import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from fus import create_app, get_dbengine

app = create_app("development")

db = get_dbengine()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
