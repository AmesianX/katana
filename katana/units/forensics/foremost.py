import os
import subprocess
from hashlib import md5

from katana import units
from katana.units import NotApplicable

DEPENDENCIES = ['foremost']


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

        # Find/create the output artifact directory
        foremost_directory = katana.get_artifact_path(self)

        p = subprocess.Popen(['foremost', self.target.path, '-o', foremost_directory], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()

        results = {
            "extracted_files": []
        }

        target_hash = md5(open(self.target.path, 'rb').read()).hexdigest()

        for (directory, _, files) in os.walk(foremost_directory):
            for filename in files:

                # Get the relative path
                file_path = os.path.join(directory, filename)
                path_hash = md5(open(file_path, 'rb').read()).hexdigest()

                # Don't recurse on the same file, or the foremost report
                if filename != 'audit.txt' and target_hash != path_hash:
                    file_path = os.path.abspath(file_path)
                    katana.recurse(self, file_path)
                    results["extracted_files"].append(filename)

        if results['extracted_files']:
            results['artifact_directory'] = foremost_directory
            katana.add_results(self, results)

        return
