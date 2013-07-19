
from fabric.api import *

@task
def create():
  run('touch ~/zion_test/user.create')