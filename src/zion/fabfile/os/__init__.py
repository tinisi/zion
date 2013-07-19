
from fabric.api import *

@task
def setup():
  run('touch ~/zion_test/os.setup')
