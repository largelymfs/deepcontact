#################################################################################
#     File Name           :     alnstats_runner.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 16:35]
#     Description         :      
#################################################################################
import util
import os


class AlnstatsRunner:
    def __init__(self, config):
        self.config = config

    def run(self):
        print "-" * 60
        print "Running Alnstats"
        self._run()
        print "Done\n"

    def _run(self):
        id = self.config['id']

        aln_file = os.path.join(self.config['path']['output'], id + '.aln')
        colstats_file = os.path.join(self.config['path']['output'], id + '.colstats')
        pairstat_file = os.path.join(self.config['path']['output'], id + '.pairstats')

        args = [self.config['alnstats']['command'],
                aln_file,
                colstats_file,
                pairstat_file
                ]

        util.run_command(args)
