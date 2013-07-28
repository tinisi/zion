
from fabric.api import *
from fabric.contrib import *

@task
def setup():
  run('touch ~/zion_test/os.setup')
