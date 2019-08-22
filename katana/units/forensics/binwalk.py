import hashlib
import os
import shutil
import subprocess

from katana import units
from katana import utilities
from katana.units import NotApplicable

DEPENDENCIES = ['binwalk']


def md5sum(path):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5


class Unit(units.FileUnit):
    # JOHN: This MUST be in the class...
    PROTECTED_RECURSE = True
    PRIORITY = 55

    def __init__(self, katana, target):
        super(Unit, self).__init__(katana, target)

        self.completed = True
        if target.is_url:
            raise NotApplicable('target is a URL')

    def evaluate(self, katana, case):

        binwalk_directory = katana.get_artifact_path(self)

        # Run binwalk on the target
        parms = ['binwalk', '-e', self.target.path, '--directory', binwalk_directory, '--dd=.*', '-M']
        p = subprocess.Popen(parms, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        results = utilities.process_output(p)

        # The call failed. We have no results.
        if p.wait() != 0:
            shutil.rmtree(binwalk_directory)
            return

        # Grab the md5 sum of the target file
        target_sum = md5sum(self.target.path)

        # Inspect all the resulting files
        for root, dirs, files in os.walk(binwalk_directory):
            for name in files:
                path = os.path.join(root, name)
                path = os.path.abspath(path)
                md5 = md5sum(path)
                if md5.hexdigest() == target_sum.hexdigest():
                    os.remove(os.path.join(root, name))
                else:
                    katana.add_artifact(self, path)
                    katana.recurse(self, path)

        katana.add_results(self, results)
        return
