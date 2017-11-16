#################################################################################
#     File Name           :     run_pipeline.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 17:09]
#     Description         :      
#################################################################################
import yaml

import sys
import config_parser
import fasta_spliter
import hhblits_runner
import ccmpred_runner
import freecontact_runner
import alnstats_runner
import ss_runner
import jackhmmer_runner
import hhmake_runner
import util

if __name__ == '__main__':
    default_config = sys.argv[1]
    input_sequence = sys.argv[2]
    output_dir = sys.argv[3]

    config = config_parser.parse(default_config, input_sequence, output_dir)

    print "=" * 60
    print "Running Pipeline with the following configuration"
    print yaml.dump(config)

    util.make_dir_if_not_exist(config['path']['output'])

    if config["gen_feature_with_jackhmmer"]:
        r = jackhmmer_runner.Jackhmmer_Runner(config)
        r.run()
    else:
        r = hhblits_runner.HHBlitsRunner(config)
        r.run()

    r = ccmpred_runner.CCMPredRunner(config)
    r.run()

    r = freecontact_runner.FreeContactRunner(config)
    r.run()

    r = alnstats_runner.AlnstatsRunner(config)
    r.run()

    r = ss_runner.SSRunner(config)
    r.run()

    r = hhmake_runner.HHMakeRunner(config)
    r.run()
