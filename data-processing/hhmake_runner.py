import os
import util


class HHMakeRunner:
    def __init__(self, config):
        self.config = config

    def run(self):
        print "-" * 60
        print "Running HHMake"
        self._run()
        print "Done\n"

    def _run(self):
        id = self.config['id']

        input_file = os.path.join(self.config['path']['output'], id + '.a3m')
        log_file = os.path.join(self.config['path']['output'], id + '.hhmake')
        hhm_file = os.path.join(self.config['path']['output'], id + '.hhm')

        args = [self.config['hhmake']['command'],
                '-i', input_file,
                '-o', hhm_file]
        util.run_command(args, log_file)
