from eth_account import Account

class Refferals:
    def __init__(self):
        self.minimumStakes = 100
        self.stakers = {}
        self.users = {}
    def stake(self, User, amount):
        if User.balance >= self.minimumStakes and User.balance >= amount:
            self.stakers[User.address] = amount
            User.balance -= amount
            return True
    class User:
        def __init__(self):
            self.private_key = Account.create().privateKey
            self.public_key = Account.privateKeyToAccount(self.private_key).publicKey
            self.address = Account.privateKeyToAccount(self.private_key).address
            self.balance = 0
            self.uplinerIds = 0
            self.downlines = {}
            self.minimumStakes = 100
            self.stakers = {}
        def add_upliner(self, upliner_id):
            if upliner_id not in self.downlines:
                if self.uplinerIds == 0:
                    self.uplinerId = upliner_id
        def isUserHasUpliner(self, user_id):
            if self.uplinerId is not 0:
                return True
        def add_downliner(self, upliner_id, downliner_id):