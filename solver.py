from __future__ import division
from timeit import default_timer as time
from cylp.cy import CyClpSimplex
import numpy as np
import scipy.sparse as sp


class FootruleRanking():
    def __init__(self, fp, verbose=True):
        self.verbose = verbose
        self.parse_file(fp)

    def parse_file(self, fp):
        """ Reads and preprocesses input """
        # TODO add checks
        # TODO add specification
        if self.verbose:
            print('Parse input')

        # TODO refactor!
        content = None
        with open(fp) as file:
                content = file.readlines()

        content = [x.strip() for x in content]                          # remove newlines
        content = [x.replace(':', '') for x in content]                 # remove ":"
        content = [np.array(x.split(), dtype=object) for x in content]  # split line into list
                                                                            # -> array

        raw_arr = np.array(content)
        self.raw_arr = raw_arr

        self.voters_raw = raw_arr[:, 0]
        self.votes_raw = raw_arr[:, 1:]

        # Map to 0, N -> only votes!
        self.orig2id = {}
        self.id2orig = {}
        id_ = 0
        for i in np.unique(self.votes_raw):
            self.orig2id[i] = id_
            self.id2orig[id_] = i
            id_ += 1
        self.votes_arr = np.vectorize(self.orig2id.get)(self.votes_raw)

        if self.verbose:
            print('     ... finished')

            print('Problem statistics')
            print('  {} votes'.format(self.votes_arr.shape[0]))
            print('  {} candidates'.format(self.votes_arr.shape[1]))

    def solve_lp(self, init=None):
        """ Solves problem exactly using LP approach
            Used solver: CoinOR CLP
        """
        if self.verbose:
            print('Solve: build model')

        N_CANDS = self.votes_arr.shape[1]
        N_VOTES = self.votes_arr.shape[0]
        rank_arr = np.array(self.votes_arr)
        N_VARS = N_CANDS * N_CANDS
        W = np.empty(N_VARS)

        """ Bipartite graph """
        # TODO vectorize!
        for c in range(N_CANDS):
            indices = np.where(rank_arr == c)[1]
            for p in range(N_CANDS):  # positions
                weight_c_p = (2 / N_VARS) * np.linalg.norm(indices - p, 1)      # sum of abs values
                W[c * N_CANDS + p] = weight_c_p

        """ LP """
        model = CyClpSimplex()                                           # MODEL
        x = model.addVariable('x', N_VARS)                               # VARS
        model.objective = W                                              # OBJ

        # vars in [0,1]
        # TODO use dedicated bounds within Simplex-alg!
        model += sp.eye(N_VARS) * x >= np.zeros(N_VARS)
        model += sp.eye(N_VARS) * x <= np.ones(N_VARS)

        # naive approach first
        # TODO vectorize this!
        helper = np.arange(N_VARS).reshape(N_CANDS, N_CANDS)

        for row in range(N_CANDS):
            lhs = np.zeros(N_VARS)
            lhs[helper[row, :]] = 1
            model += sp.csc_matrix(lhs) * x == 1

        for col in range(N_CANDS):
            lhs = np.zeros(N_VARS)
            lhs[helper[:, col]] = 1
            model += sp.csc_matrix(lhs) * x == 1

        # SOLVE
        if self.verbose:
            print('Solve')

        model.logLevel = self.verbose
        model.initialSolve()

        x_mat = np.isclose(model.primalVariableSolution['x'].reshape(N_CANDS, N_CANDS), 1.)
        sol = x_mat.nonzero()[1]
        self.obj_sol = model.objectiveValue
        self.aggr_rank = sol

    def postprocess(self):
        if self.verbose:
            print('Postprocessing')
        self.final_solution = np.vectorize(self.id2orig.get)(self.aggr_rank)
        if self.verbose:
            print('    ... finished')

    def print_sol(self):
        print('--------')
        print('SOLUTION')
        print('  objective: ', self.obj_sol)
        print('  aggregation: ')
        print(self.final_solution)
