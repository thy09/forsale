from flask import Flask,render_template,request,redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import random
from forsale import ForSale,default_configs

app = Flask(__name__)
app.config["SECRET_KEY"] = 'neverguess'
sockio = SocketIO(app)

id2user = {}
user2id = {}

def create_app():
    return app

@app.route("/create")
def create():
    print id2user,user2id
    print request.cookies.get("user-id")
    uname = id2user.get(request.cookies.get("user-id"))
    if not uname:
        uname = ""
    return render_template("create.html",
            uname = uname,
            configs = default_configs,
            )

@app.route("/create_game",methods = ["POST"])
def create_game():
    userid = request.cookies.get("user-id")
    uname = None
    if userid:
        if id2user.has_key(userid):
            uname = id2user[userid]
    if not uname:
        return jsonify({"status":"INVALID_USER"})
    args = request.get_json()
    game = ForSale(uname,args)
    print args
    if not game.inited:
        return jsonify({"status":"INVALID_ARGS"})
    return jsonify({"status":"success","id":game.id})

@app.route("/join_game",methods = ["POST"])
def join_game():
    game = ForSale.get_by_id(request.args.get("id"))
    if game == None:
        return jsonify({"status":"INVALID_GAME"})
    userid = request.cookies.get("user-id")
    uname = None
    if userid:
        if id2user.has_key(userid):
            uname = id2user[userid]
    if not uname:
        return jsonify({"status":"INVALID_USER"})
    if not game.new_player(uname):
        return jsonify({"status":"JOIN_FAIL"})
    return jsonify({"status":"success"})

@app.route("/submit",methods = ["POST"])
def submit():
    game = ForSale.get_by_id(request.args.get("id"))
    if game == None:
        return jsonify({"status":"INVALID_GAME"})
    uname = id2user.get(request.cookies.get("user-id"))
    if not uname:
        return jsonify({"status":"INVALID_USER"})
    data = request.get_json()
    type = data.get("type")
    if type == "price":
        price = data.get("price")
        if not game.submit_price(uname,int(price)):
            return jsonify({"status":"SUBMIT_PRICE_FAIL"})
    elif type == "giveup":
        if not game.give_up(uname):
            return jsonify({"status":"GIVE_UP_FAIL"})
    elif type == "house":
        house = data.get("house")
        if not game.submit_house(uname,int(house)):
            return jsonify({"status":"SUBMIT_HOUSE_FAIL"})
    return jsonify({"status":"success"})

@app.route("/game")
def member():
    userid = request.cookies.get("user-id")
    uname = ""
    if userid:
        if id2user.has_key(userid):
            uname = id2user[userid]
    game = ForSale.get_by_id(request.args.get("id"))
    if game == None:
        return redirect(url_for(".create"))
    status = None
    if uname and uname in game.players:
        status = game.player_status[game.players.index(uname)]
    return render_template("forsale.html",
            game = game,
            status = status,
            uname = uname,
            )

upper = 100000
@app.route("/update_name",methods = ["POST"])
def update_name():
    userid = request.cookies.get("user-id")
    uname = request.args.get("uname")
    print userid,uname
    status = "???"
    if userid:
        if id2user.has_key(userid):
            curname = id2user[userid]
            if curname == uname:
                status = "success"
            else:
                user2id.pop(curname)
                user2id[uname] = userid
                id2user[userid] = uname
                status = "success"
        else:
            if user2id.has_key(uname):
                status = "NAME_EXIST"
            id2user[userid] = uname
            user2id[uname] = userid
            status = "success"
    else:
        if user2id.has_key(uname):
            userid = user2id[uname]
            status = "success"
        else:
            userid = str(random.randint(1,upper))
            while user2id.has_key(userid):
                userid = str(random.randint(1,upper))
            id2user[userid] = uname
            user2id[uname] = userid
            status = "success"
    response = jsonify({"status":status})
    response.set_cookie("user-id",userid)
    return response


@app.route("/allgame")
def allgame():
    return jsonify({"idx":ForSale.games.keys()})

if __name__ == "__main__":
    app_ = create_app()
    app_.debug = True
    #sockio.run(app)
    sockio.run(app,port=23322)
   # app_.run(host='0.0.0.0',port = 23332)
