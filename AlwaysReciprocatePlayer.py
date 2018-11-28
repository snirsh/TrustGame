from itertools import count;

global_index = 1
global_bank_fee = 1
global_bank_win = 2
global_bank_lose = 3


class AlwaysReciprocatePlayer:
    _ids = count(0)

    def __init__(self, trustor_or_trustee, trust_coefficient, beta):
        global global_bank_fee
        global_bank_fee = beta
        self.id = next(self._ids)
        self.trustor = trustor_or_trustee
        self.currency = 0

    def changeTrustStatus(self):
        self.trustor = not self.trustor

    def reciprocate(self, other):
        return True

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

    def __repr__(self):
        return "Always Reciprocates Player ID: " + str(
            self.id) + "\n" + "Currency: " + str(
            self.currency) + "\nIs truster? " + self.trustor

    def __str__(self):
        return "Always Reciprocates Player ID: " + str(
            self.id) + "\n" + "Currency: " + str(
            self.currency) + "\nIs truster? " + self.trustor