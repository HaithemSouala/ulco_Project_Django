from __future__ import with_statement
from fabric.api import *
import cookbook


@task
def test():
    local("./manage.py test")



@task
def requirements():
    local("pip install -r REQUIREMENTS")


@task
def commit():
    local("git add -p && git commit")


@task
def push():
    local("git push origin master")


@task
def pull():
    local("git pull origin master")


@task
def sync_db():
    local("./manage.py syncdb")


@task
def create_migration(initial=False):
    if initial:
        local("./manage.py schemamigration recipes --initial")
    else:
        local("./manage.py schemamigration recipes --auto --update")


@task
def migrate():
    local("./manage.py migrate recipes")


@task
def devel_environment():
    local("mkvirtualenv cookbook")
    requirements()
    sync_db()
    migrate()


@task
def prepare_commit():
    test()
    create_migration()
    commit()
    push()