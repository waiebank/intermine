"""
The test and clean code is shamelessly stolen from
http://da44en.wordpress.com/2002/11/22/using-distutils/
"""

import os
import sys
import time
from distutils.core import Command, setup
from distutils import log
from distutils.fancy_getopt import fancy_getopt
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin
from warnings import warn


class TestCommand(Command):
    user_options = [('verbose', 'v', "produce verbose output", 1)]

    def initialize_options(self):
        self._dir = os.getcwd()
        self.test_prefix = 'test'

    def finalize_options(self):
       args, obj = fancy_getopt(self.user_options, {}, None, None)
       # Ugly as sin, but distutils forced me to do it :(
       # All I wanted was this command to default to quiet...
       if "--verbose" not in args and "-v" not in args:
           self.verbose = 0

    def run(self):
       '''
       Finds all the tests modules in tests/, and runs them, exiting after they are all done
       '''
       from tests.testserver import TestServer
       from tests.test import WebserviceTest

       log.set_verbosity(self.verbose)

       server = TestServer()
       server.start()
       WebserviceTest.TEST_PORT = server.port

       self.announce("Waiting for test server to start on port " + str(server.port), level=2)
       time.sleep(1)

       testfiles = [ ]
       for t in glob(pjoin(self._dir, 'tests', self.test_prefix + '*.py')):
           if not t.endswith('__init__.py'):
               testfiles.append('.'.join(
                   ['tests', splitext(basename(t))[0]])
               )

       self.announce("Test files:" + str(testfiles), level=2)
       tests = TestLoader().loadTestsFromNames(testfiles)
       t = TextTestRunner(verbosity = self.verbose)
       t.run(tests)
       exit()

class LiveTestCommand(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.test_prefix = 'live'

class CleanCommand(Command):
    """
    Remove all build files and all compiled files
    =============================================

    Remove everything from build, including that
    directory, and all .pyc files
    """
    user_options = [('verbose', 'v', "produce verbose output", 1)]

    def initialize_options(self):
        self._files_to_delete = [ ]
        self._dirs_to_delete = [ ]

        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.pyc'):
                    self._files_to_delete.append(pjoin(root, f))
        for root, dirs, files in os.walk(pjoin('build')):
            for f in files:
                self._files_to_delete.append(pjoin(root, f))
            for d in dirs:
                self._dirs_to_delete.append(pjoin(root, d))
        # reverse dir list to only get empty dirs
        self._dirs_to_delete.reverse()
        self._dirs_to_delete.append('build')

    def finalize_options(self):
        args, obj = fancy_getopt(self.user_options, {}, None, None)
        # Ugly as sin, but distutils forced me to do it :(
        # All I wanted was this command to default to quiet...
        if "--verbose" not in args and "-v" not in args:
            self.verbose = 0

    def run(self):
        for clean_me in self._files_to_delete:
            if self.dry_run:
                log.info("Would have unlinked " + clean_me)
            else:
                try:
                    self.announce("Deleting " + clean_me, level=2)
                    os.unlink(clean_me)
                except:
                    message = " ".join(["Failed to delete file", clean_me])
                    log.warn(message)
        for clean_me in self._dirs_to_delete:
            if self.dry_run:
                log.info("Would have rmdir'ed " + clean_me)
            else:
                if os.path.exists(clean_me):
                    try:
                        self.announce("Going to remove " + clean_me, level=2)
                        os.rmdir(clean_me)
                    except:
                        message = " ".join(["Failed to delete dir", clean_me])
                        log.warn(message)
                elif clean_me != "build":
                    log.warn(clean_me + " does not exist")

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
        name = "intermine",
        packages = ["intermine", "intermine.lists"],
        provides = ["intermine"],
        cmdclass = { 'clean': CleanCommand, 'test': TestCommand,  'livetest': LiveTestCommand },
        version = "1.00.01",
        description = "InterMine WebService client",
        author = "Alex Kalderimis",
        author_email = "dev@intermine.org",
        url = "http://www.intermine.org",
        download_url = "http://www.intermine.org/lib/python-webservice-client-0.98.02.tar.gz",
        keywords = ["webservice", "genomic", "bioinformatics"],
        classifiers = [
            "Programming Language :: Python",
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Operating System :: OS Independent",
            ],
        license = "LGPL",
        long_description = """\
InterMine Webservice Client
----------------------------

Provides access routines to datawarehouses powered
by InterMine technology.

""",
        **extra
)
