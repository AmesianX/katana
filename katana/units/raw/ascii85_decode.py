import base64
import binascii

import magic
from katana import utilities
from katana.unit import BaseUnit
from katana.units import NotApplicable


class Unit(BaseUnit):
    PRIORITY = 60

    def __init__(self, katana, target):
        super(Unit, self).__init__(katana, target)

        if not self.target.is_printable:
            raise NotApplicable("not printable data")

        if self.target.is_english:
            raise NotApplicable("seemingly english")

    def evaluate(self, katana, case):
        try:
            result = base64.a85decode(self.target.raw)

            if utilities.isprintable(result):
                katana.recurse(self, result)
                katana.add_results(self, result)

            # if it's not printable, we might only want it if it is a file...
            else:
                magic_info = magic.from_buffer(result)
                if utilities.is_good_magic(magic_info):
                    katana.add_results(self, result)

                    filename, handle = katana.create_artifact(self, "decoded", mode='wb', create=True)
                    handle.write(result)
                    handle.close()
                    katana.recurse(self, filename)

        except (UnicodeDecodeError, binascii.Error, ValueError):
            # This won't decode right... must not be right! Ignore it.
            # I return here because we are only trying to decode ONE string
            return
