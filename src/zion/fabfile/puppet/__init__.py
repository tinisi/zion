
from fabric.api import *

@task
def install():
    # puppet and dependencies
    sudo("yum --assumeyes install ruby")
    sudo("yum --assumeyes install puppet")
