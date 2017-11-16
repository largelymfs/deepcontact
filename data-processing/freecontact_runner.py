#################################################################################
#     File Name           :     freecontact_runner.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 16:32]
#     Description         :      
#################################################################################
import util
import os


class FreeContactRunner:
    def __init__(self, config):
        self.config = config

    def run(self):
        print "-" * 60
        print "Running FreeContact"
        self._run()
        print "Done\n"

    def _run(self):
        id = self.config['id']
        aln_file = os.path.join(self.config['path']['output'], id + '.aln')
        output_file = os.path.join(self.config['path']['output'], id + '.evfold')

        args = [self.config['freecontact']['command'],
                '-a', str(self.config['freecontact']['n_threads']),
                '-f', aln_file]

        util.run_command(args, output_file)
