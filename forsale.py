import random
class ForSale:
    games = {}
    @classmethod
    def get_by_id(cls,id):
        return cls.games.get(id)

    def init_id(self):
        upper = 100000000
        idx = random.randint(1,upper)
        while (ForSale.games.has_key(idx)):
            idx = random.randint(0,upper)
        ForSale.games[str(idx)] = self
        return idx

    def __init__(self,creator_id,args):
        try:
            self.player_count = int(args["player_count"])
            if self.player_count < 3:
                return None
            self.house_count = int(args["house_count"])
            self.rounds = int(args["rounds"])
            self.initial_money = int(args["initial_money"])
            if self.player_count * self.rounds > self.house_count:
                self.rounds = self.house_count / self.player_count
        except:
            self.inited = False
            return None
        self.id = self.init_id()
        print "init self.id",self.id
        self.players = [creator_id]
        self.status = "WAIT"
        self.houses = range(1,self.house_count+1)
        half = (self.house_count+1)/2
        values = range(half)
        values[1] = half
        self.values = values*2
        random.shuffle(self.houses)
        random.shuffle(self.values)
        self.cur_round = 0
        self.cur_player = 0
        self.all_sales = []
        self.cur_sales = []
        self.player_status = [{"money":self.initial_money,
                "quitted":False,
                "houses":[],
                "house_money":[],
                "price":0} for i in range(self.player_count)]
        self.inited = True

    def show_status(self):
        print self.status,self.cur_round,self.cur_player
        if self.status == "BUY":
            print self.cur_houses
            print "player ",self.cur_player," price:",self.cur_price
        elif self.status == "SALE":
            print self.cur_values,self.cur_sales
        elif self.status == "FINISHED":
            print self.result
        for s in self.player_status:
            print s

    def new_player(self,player_id):
        if self.status != "WAIT":
            return False
        if player_id in self.players:
            return False
        self.players.append(player_id)
        if len(self.players) == self.player_count:
            self.status = "BUY"
            self.next_round()
        return True

    def submit_house(self,player_id,house):
        idx = -1
        try:
            idx = self.players.index(player_id)
        except:
            return False
        if self.cur_sales.has_key(idx):
            return False
        if not house in self.player_status[idx]["houses"]:
            return False
        self.player_status[idx]["houses"].remove(house)
        self.cur_sales[idx] = house
        if len(self.cur_sales) == self.player_count:
            self.sale_houses()
        return True

    def sale_houses(self):
        sales = []
        for h,v in zip(sorted(self.cur_sales.items(),key = lambda x:x[1],reverse = True),self.cur_values):
            idx,house = h
            sales.append((self.players[idx],house,v))
            self.player_status[idx]["house_money"].append(v)
        self.next_round()
        self.all_sales.append(sales)

    def finish_game(self):
        self.result = []
        for p,status in zip(self.players,self.player_status):
            self.result.append((p,status["money"] + sum(status["house_money"])))
        self.result.sort(key = lambda x:x[1],reverse = True)

    def submit_price(self,player_id,price):
        if self.players[self.cur_player] != player_id:
            return False
        status = self.player_status[self.cur_player]
        if status["money"] < price or price <= self.cur_price:
            return False
        self.cur_price = price
        status["price"] = price
        self.next_player()
        return True

    def give_up(self,player_id):
        if self.players[self.cur_player] != player_id:
            return False
        status = self.player_status[self.cur_player]
        if status["quitted"]:
            return False
        status["houses"].append(self.cur_houses[-1])
        self.cur_houses = self.cur_houses[:-1]
        status["money"] = status["money"] - status["price"] + status["price"]/2
        status["quitted"] = True
        self.next_player()
        return True

    def final_house(self):
        status = self.player_status[self.cur_player]
        status["houses"].append(self.cur_houses[0])
        status["money"] = status["money"] - status["price"]

    def next_player(self):
        if self.status != "BUY":
            return
        self.cur_player = (self.cur_player+1) % self.player_count
        while (self.player_status[self.cur_player]["quitted"]):
            self.cur_player = (self.cur_player+1) % self.player_count
        if len(self.cur_houses) == 1:
            self.final_house()
            self.next_round()

    def next_round(self):
        if self.cur_round == self.rounds:
            if self.status == "BUY":
                self.status = "SALE"
                self.cur_round = 0
            else:
                self.finish_game()
                self.status = "FINISHED"
                return
        self.cur_player = self.cur_round % self.player_count
        offset = self.cur_round * self.player_count
        self.cur_round += 1
        if self.status == "BUY":
            self.cur_houses = sorted(self.houses[offset:offset+self.player_count],reverse = True)
        elif self.status == "SALE":
            self.cur_values = sorted(self.values[offset:offset+self.player_count],reverse = True)
        self.cur_price = 0
        for s in self.player_status:
            s["quitted"] = False
            s["price"] = 0
        self.cur_sales = {}
        if self.status == "SALE" and self.cur_round == self.rounds:
            for i in range(self.player_count):
                self.submit_house(self.players[i],self.player_status[i]["houses"][0])


default_configs = {3:[30,7,18],
        4:[30,6,18],
        5:[30,6,14],
        6:[30,5,14],
        }

def gen_default_config(key):
    conf = default_configs.get(key)
    if not conf:
        return None
    return {"player_count":key,"house_count":conf[0],
            "rounds":conf[1],"initial_money":conf[2],}
