
from fabric.api import *

@task
def install():
  run('touch ~/zion_test/foreman.install')