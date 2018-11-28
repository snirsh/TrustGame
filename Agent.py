from Tools.scripts.treesync import raw_input

from SmartPlayer import smartPlayer
from RandomPlayer import RandomPlayer
from AlwaysReciprocatePlayer import AlwaysReciprocatePlayer
from NonReciprocativePlayer import NonReciprocativePlayer
from graph import Graph
import clusterRandNetwork
from time import gmtime, strftime
global_beta = 0


def smartCreator(n, numOfTrusters, Coefficient):
    smarts = []
    for i in range(n):
        if numOfTrusters > 0:
            smart = smartPlayer(True, Coefficient, global_beta)
            numOfTrusters -= 1
        else:
            smart = smartPlayer(False, Coefficient, global_beta)
        smarts.append(smart)
    return smarts


def randCreator(n, Coefficient):
    randoms = []
    for i in range(n):
        rand = RandomPlayer(False, Coefficient)
        randoms.append(rand)
    return randoms


def alwaysRec(n):
    recs = []
    for i in range(n):
        rec = AlwaysReciprocatePlayer()
        recs.append(rec)
    return recs


def nonRec(n):
    nonRecs = []
    for i in range(n):
        nonr = NonReciprocativePlayer()
        nonRecs.append(nonr)
    return nonRecs


def runMatch(p1, p2, warmup=False):
    p1Ans = p1.reciprocate(p2)
    p2Ans = p2.reciprocate(p1)
    p1.updateCurrency(p2Ans)
    p2.updateCurrency(p1Ans)
    if p1Ans and not warmup:
        p1.updateTrustStatus(p2, p2Ans)
        p2.updateTrustStatus(p1, p1Ans)
    return p1Ans, p2Ans


def regNetwork(smarts, rands, recs, nrecs):
    trusters = []
    trustees = []
    for smart in smarts:
        if smart.trustor:
            trusters.append(smart)
        else:
            trustees.append(smart)
    for rand in rands:
        if rand.trustor:
            trusters.append(rand)
        else:
            trustees.append(rand)
    for rec in recs:
        if rec.trustor:
            trusters.append(rec)
        else:
            trustees.append(rec)
    for nrec in nrecs:
        if nrec.trustor:
            trusters.append(nrec)
        else:
            trustees.append(nrec)
    return trusters, trustees


def weightedNetwork(coeff, smarts, rands, recs, nrecs):
    return 1


def printLogFile(smarts, rands, recs, nonRecs):
    f = open("log.txt", "w")
    f.write("################\n")
    f.write("#Smart Players:#\n")
    f.write("################\n")
    for smart in smarts:
        f.write(str(smart))
    f.write("################\n")
    f.write("#     BOTS    :#\n")
    f.write("################\n")
    f.write("total bots: " + str(len(rands) + len(recs) + len(nonRecs)) + "\n")
    f.write("################\n")
    f.write("# Random Bots :#\n")
    f.write(
        "################\n" + "Number of randoms :" + str(len(rands)) + "\n")
    for rand in rands:
        f.write(rand)
    f.write("################\n")
    f.write("# Always reciprocatives:#\n")
    f.write("################\n" + "Number of reciprocative bots:" + str(
        len(recs)) + "\n")
    for rec in recs:
        f.write(rec)
    f.write("################\n")
    f.write("# Non-reciprocatives:#\n")
    f.write("################\n" + "Number of reciprocative bots:" + str(
        len(recs)) + "\n")
    for rec in nonRecs:
        f.write(rec)
    f.close()


if __name__ == '__main__':
    global global_beta
    smarts = []
    randoms = []
    recs = []
    nonRecs = []
    clusterCoefficient = 0
    smartsNumber = int(input("Please insert number of Smart players: "))
    trusters = int(input("Please insert amount of trusters among them: "))
    coeff = float(
        input("Please insert the proportion of genuinely honest trustees: "))
    bots = input("Should there be bots? Y/N: ")
    if bots == "Y" or bots == "y":
        bots = True
        rands = int(input("How many randoms? "))
        recsnum = int(input("How many always reciprocative players? "))
        nrecs = int(input("How many always non-reciprocative players? "))
        randoms = randCreator(rands, coeff)
        recs = alwaysRec(recsnum)
        nonRecs = nonRec(nrecs)
    else:
        bots = False
    global_beta = float(input("Please insert beta "))
    networkType = int(input(
        "insert 1 for simple network, 2 for network with cluster coefficient "))
    if networkType == 2:
        clusterCoefficient = int(input(
            "please insert the clustering coefficient "))
    rounds = int(input("Please insert number of rounds: "))
    smarts = smartCreator(smartsNumber, trusters, coeff)
    trusters = []
    trustees = []
    trusters, trustees = regNetwork(smarts, rands=[], recs=[], nrecs=[])
    warmupRounds = 30
    printLogFile(smarts, randoms, recs, nonRecs)
    timeStamp = strftime("%Y%m%d%H%M", gmtime())
    f = open("log" + timeStamp + ".txt", "w")
    if networkType == 1:
        for i in range(rounds):
            for truster in trusters:
                for trustee in trustees:
                    currp1 = truster.currency
                    currp2 = trustee.currency
                    p1a, p2a = runMatch(truster, trustee, warmupRounds > 0)
                    f.write("Round between: \n")
                    f.write(str(truster))
                    f.write("Decision: {0}".format(p1a) + ", Outcome: {0}".format(
                        truster.currency - currp1))
                    f.write(str(trustee))
                    f.write("Decision: {0}".format(p2a) + ", Outcome: {0}".format(
                        trustee.currency - currp2))
                    warmupRounds -= 1
                    if isinstance(smartPlayer, type(truster)):
                        f.write("estimations of Truster as a Smart Player: \n")
                        f.write("ID: " + truster.id + "\n" + truster.memoryPrint)
                    if isinstance(smartPlayer, type(trustee)):
                        f.write("estimations of Trustee as a Smart Player: \n")
                        f.write("ID: " + trustee.id + "\n" + trustee.memoryPrint)
        f.write("END OF GAME, RESULTS: ")
        for truster in trusters:
            f.write(str(truster))
        for trustee in trustees:
            f.write(str(trustee))

    if networkType == 2:
        g = Graph()
        for truster in trusters:
            g.add_vertex(truster)
            for trustee in trustees:
                g.add_vertex((trustee))
                g.add_edge((truster, trustee))
                g, niter, gcc_best = clusterRandNetwork.bansal_shuffle(g,
                                                                       clusterCoefficient)
        for i in range(rounds):
            for (p1, p2) in g.edges():
                runMatch(p1, p2, warmupRounds > 0)
                warmupRounds -= 1
        f.write("END OF GAME, RESULTS: ")
        for vet in g.vertices():
            f.write(str(vet))
    f.close()
