import sys
from solver import *
from footrule_dist import *


if __name__ == '__main__':
    fp = sys.argv[1]

    kemeny = FootruleRanking(fp)
    kemeny.solve_lp()
    kemeny.postprocess()
    kemeny.print_sol()
