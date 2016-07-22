# SimpleApacheManager

Provides a CLI interface to manage vhosts and SSL keys, , ready to be
released and distributed via setuptools/PyPI/pip for Python 3 for Ubuntu Server 16.04.

## Install

To install required python modules for SimpleApacheManager using setuptools and pip run:

    sudo python3 setup.py install

Afterwards the apllication can be executed with:

    


## Usage

Clone this repository and build the project on your Ubuntu 16.04 server with setuptools / pip.

The application can be run right from the source directory, in two different
ways:

1) Treating the **sam** directory as a package *and* as the main script::

    $ python -m sam arg1 arg2

2) Using the sam-runner.py wrapper::

    $ ./sam_runner.py arg1 arg2


## Installation sets up samcli command


Situation before installation::

    $ samcli
    bash: sam: command not found

Installation right from the source tree:

    $ python setup.py install

Now, the ``samcli`` command is available::

    $ samcli arg1 arg2

On Ubuntu 16.04 systems, the installation places a ``samcli`` script into a
centralized ``bin`` directory, which should be in your ``PATH``.
