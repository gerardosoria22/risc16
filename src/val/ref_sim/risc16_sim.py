#!/usr/bin/python3

import argparse
from risc16_sim_class import Risc16sim


def parse_args():
    """_summary_
    """
    parser = argparse.ArgumentParser(prog="Risc16sim",
                                     description="Golden reference risc16 simulator for validating hw RTL \
                                     implementations")
    parser.add_argument("-p", "--program_file", required=True)
    parser.add_argument("-n", "--nsteps", required=True, type=int)
    parser.add_argument("-s", "--stop_on_halt", action="store_true", default=False)
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    return parser.parse_args()


def main(args):
    sim = Risc16sim(args)
    sim.reset()
    sim.run(args.nsteps)
    #print(sim.mem.mem)
    #print(sim.args.stop_on_halt)


if __name__ == "__main__":
    main(parse_args())
