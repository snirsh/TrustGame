# Copyright 2014 Alistair Muldal <alistair.muldal@pharm.ox.ac.uk>

import numpy as np
import jgraph
from itertools import combinations, product


def bansal_shuffle(G, target_gcc, tol=1E-3, maxiter=None, inplace=True,
                   require_connected=False, seed=None, verbose=False):
    r"""
    Bansal et al's Markov chain method for generating random graphs with
    prescribed global clustering coefficients.

    On each iteration a motif consisting of 5 nodes and 4 edges is randomly
    selected from the set of all such motifs, and two of the outer edges are
    rewired to produce a new candidate graph, G', which has the same degree
    sequence as G:
                           x                       x
                          / \                     / \
                        y1   y2      <===>      y1---y2
                        |    |
                        z1   z2                 z1---z2

    The rewiring step can either introduce a new triangle or break up an
    existing one depending on whether the current GCC is greater or smaller
    than the target value. If rewiring brings the GCC closer to the target
    value then G' is used in the next iteration. The algorithm halts either
    when the GCC is sufficiently close to the target value, or when a maximum
    number of iterations is reached.

    Arguments:
    ----------
        G: igraph.Graph
            input graph to be shuffled; can be either undirected or directed
        target_gcc: float
            target global clustering coefficient
        tol: float
            halting tolerance: abs(gcc - target_gcc) < tol
        maxiter: int
            maximum number of rewiring steps to perform (default is no limit)
        inplace: bool
            modify G in place
        require_connected: bool
            impose the additional constraint that G' must be connected on each
            rewiring step, in which case the input graph must also be connected
        seed: int
            seed for the random number generator, see numpy.random.RandomState
        verbose: bool
            print convergence messages

    Returns:
    --------
        G_shuf: igraph.Graph
            shuffled graph, has the same same degree sequence(s) as G
        niter: int
            total rewiring iterations performed
        gcc_best: float
            final global clustering coefficient

    Reference:
    ----------
    Bansal, S., Khandelwal, S., & Meyers, L. A. (2009). Exploring biological
    network structure with clustered random networks. BMC Bioinformatics, 10,
    405. doi:10.1186/1471-2105-10-405

    """

    if maxiter is None:
        maxiter = np.inf

    if require_connected:
        if not G.is_connected():
            raise ValueError(
                'if require_connected, the input graph must also be connected')

    if not inplace:
        G = G.copy()

    # seed RNG
    gen = np.random.RandomState(seed)

    # get initial GCC and loss
    gcc_initial = 0
    gcc = gcc_best = gcc_initial
    loss = loss_best = target_gcc - gcc

    # if we're already close enough, return immediately
    if abs(loss_best) < tol:
        return G, 0, gcc

    # find all nodes with degrees >= 2 (ignoring direction). each of these must
    # be part of at least one triplet motif
    degrees = G.degree()
    candidate_x = _filter_by_degree(range(G.vcount()), degrees, 2)

    niter = 0
    terminating = False

    while not terminating:

        # for moderately-sized graphs it's faster to modify a deep copy of G
        # than to undo the rewiring whenever the GCC does not improve
        G_prime = G.copy()

        if loss > 0:
            _make_triangle(G_prime, candidate_x, gen)

        elif loss < 0:
            _break_triangle(G_prime, candidate_x, gen)

        # compute the new clustering coefficient and loss
        gcc = G_prime.transitivity_undirected()
        loss = target_gcc - gcc

        # did we improve?
        improved = abs(loss) < abs(loss_best)

        # if desired, we also confirm that the new graph is connected
        if require_connected:
            improved &= G_prime.is_connected()

        if improved:
            gcc_best = gcc
            loss_best = loss
            G = G_prime

        # print progress
        if verbose:
            print("iter=%-6i GCC=%-8.3g loss=%-8.3g improved=%-5s"
                  % (niter, gcc, loss, improved))

        niter += 1

        # check termination conditions
        if abs(loss_best) < tol:
            terminating = True
        elif niter >= maxiter:
            print('failed to reach targed GCC within maxiter')
            terminating = True

    return G, niter, gcc_best


def _make_triangle(G, candidate_x, gen):
    """
    create at least one triangle motif by rewiring two edges
    """

    have_rewire_candidates = False

    # get candidate edges to rewire
    while not have_rewire_candidates:

        # a random node with a degree of at least 2
        x = gen.choice(candidate_x)

        # find all neighbors of this node with a degree of at least 2 (ignoring
        # direction)
        x_neighbors = G.neighbors(x)
        x_valid_neighbors = _filter_by_degree(
            x_neighbors, G.degree(x_neighbors), 2
        )

        # skip this candidate if there aren't at least two neighbors with
        # degrees >= 2
        if len(x_valid_neighbors) < 2:
            continue

        else:

            # shuffle the valid neighbors of x, iterate over every possible
            # pair
            gen.shuffle(x_valid_neighbors)

            for (y1, y2) in combinations(x_valid_neighbors, 2):

                # if y1 and y2 are already connected, skip them
                if _any_direction(G, y1, y2):
                    continue

                # find all outputs from y1
                from_y1 = G.neighbors(y1, igraph.OUT)

                # find all inputs to y2
                to_y2 = G.neighbors(y2, igraph.IN)

                # shuffle them
                gen.shuffle(from_y1)
                gen.shuffle(to_y2)

                # iterate over all possible pairs consisting of one output from
                # y1 and one input to y2.
                for z1, z2 in product(from_y1, to_y2):

                    # we're only interested in unconnected pairs
                    if _any_direction(G, z1, z2):
                        continue

                    # must satisfy z1 != x; z2 != x; z1 != z2
                    elif x not in (z1, z2) and z1 != z2:
                        have_rewire_candidates = True
                        break

                if have_rewire_candidates:
                    break

    # perform double edge swap
    G.delete_edges([(y1, z1), (z2, y2)])
    G.add_edges([(y1, y2), (z2, z1)])

    pass


def _break_triangle(G, candidate_x, gen):
    """
    destroy at least one triangle by rewiring two edges
    """

    have_rewire_candidates = False
    n_edges = G.ecount()

    # get candidate edges to rewire
    while not have_rewire_candidates:

        # a random node with a degree of at least 2
        x = gen.choice(candidate_x)

        # find all neighbors of this node with a degree of at least 2 (ignoring
        # direction)
        x_neighbors = G.neighbors(x)
        x_valid_neighbors = _filter_by_degree(
            x_neighbors, G.degree(x_neighbors), 2
        )

        # skip this candidate if there aren't at least two neighbors with
        # degrees >= 2
        if len(x_valid_neighbors) < 2:
            continue

        else:

            # shuffle the valid neighbors of x, iterate over every possible
            # pair
            gen.shuffle(x_valid_neighbors)

            for (y1, y2) in combinations(x_valid_neighbors, 2):

                # if a connection exist from y1 --> y2...
                if G.are_connected(y1, y2):
                    y1_neighbors = G.neighbors(y1)
                    y2_neighbors = G.neighbors(y2)

                    exclude = x_neighbors + y1_neighbors + y2_neighbors

                    while not have_rewire_candidates:

                        # pick a random edge
                        eidx = gen.randint(0, n_edges)
                        e = G.es[eidx]
                        z2, z1 = e.source, e.target

                        # neither z1 nor z2 can be connected to either x, y1,
                        # or y2
                        if z1 not in exclude and z2 not in exclude:

                            have_rewire_candidates = True
                            break

                if have_rewire_candidates:
                    break

    # perform double edge swap
    G.delete_edges([(y1, y2), (z2, z1)])
    G.add_edges([(y1, z1), (z2, y2)])

    pass


def _filter_by_degree(indices, degrees, min_deg=2):
    return [ii for ii, dd in zip(indices, degrees) if dd >= min_deg]


def _any_direction(G, a, b):
    """
    if a --> b, return 1
    if a <-- b, return -1
    else,       return 0
    """
    if G.are_connected(a, b):
        return 1
    elif G.are_connected(b, a):
        return -1
    else:
        return 0