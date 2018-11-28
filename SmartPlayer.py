from itertools import count

global_index = 1
global_bank_fee = 1
global_bank_win = 2
global_bank_lose = 3


class smartPlayer:
    _ids = count(0)

    def __init__(self, trustor_or_trustee, trust_coefficient, beta):
        global global_bank_fee
        global_bank_fee = beta
        self.id = next(self._ids)
        self.trustor = trustor_or_trustee
        self.trustingCoefficient = trust_coefficient
        self.memory = {}
        self.currency = 0

    def changeTrustStatus(self):
        self.trustor = not self.trustor

    def reciprocate(self, other):
        alreadyIn = False
        for key in self.memory.keys():
            if key == other.id:
                alreadyIn = True
        if not alreadyIn:
            self.memory[other.id] = self.trustingCoefficient
        ans = self.memory[other.id] >= 0.66 * (1 + global_bank_fee)
        if not ans and self.trustor:
            self.currency -= global_bank_fee
        return ans

    def updateCurrency(self, win_lose):
        if self.trustor:
            if win_lose:
                self.currency += global_bank_win
            else:
                self.currency -= global_bank_fee
        else:
            if win_lose:
                self.currency += global_bank_win
            else:
                self.currency += global_bank_lose

    def updateTrustStatus(self, other, result):
        if result:
            self.memory[other.id] *= self.trustingCoefficient
        else:
            self.memory[other.id] *= (1 - self.trustingCoefficient)

    def memoryPrint(self):
        repstr = []
        i = 0
        for pid, mem in self.memory.items():
            repstr[i] = "Player ID: " + pid + ", Trusting Status: " + mem
        return repstr

    def __repr__(self):
        return "Player ID: " + str(self.id) + "\n" + "Currency: " + str(
            self.currency) + "\n" + "Self trusting coefficient: " + self.trustingCoefficient + "\n" + "Is truster? " + self.trustor

    def __str__(self):
        trustorStr = "No"
        if self.trustor:
            trustorStr = "Yes"
        return "Player ID: " + str(self.id) + ", Currency: {0}".format(self.currency) + ", Self trusting coefficient: {0}".format(self.trustingCoefficient) + ", Is truster? " + trustorStr + "\n"
