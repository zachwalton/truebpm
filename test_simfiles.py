from app import PROJECT_ROOT
from simfile import SMParser

import logging
import os
import unittest

class SimfileTestCase(unittest.TestCase):

    def test_no_simfile_errors(self):
        errors = []

        simfiles_location = PROJECT_ROOT + '/simfiles'
        simfiles = os.listdir(simfiles_location)

        logging.info('Processing {} simfiles...'.format(len(simfiles)))
        for sim in simfiles:
            try:
                SMParser(open(simfiles_location + '/' + sim).read()).analyze(
                    'Single', 'Hard', preferred_rate=570, speed_change_threshold=1)
            except Exception as e:
                errors.append("error in {}: {}: {}".format(sim, e.__class__.__name__, e.message))
                logging.error(errors[-1])

        assert len(errors) == 0, "there were one or more simfile errors"
