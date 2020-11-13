from importing_modules import *
app = Flask(__name__)

global players, rooms

players = []
rooms   = {}

@app.route('/')
def root():
    return("Project root")

@app.route('/get-user-id', methods=['POST'])
def get_user_id():
    while True:
        player_id = random.randint(0, 100)
        if player_id not in players:
            players.append(player_id)
        else: break
    return(jsonify(
        USER_ID=player_id
))

@app.route('/create', methods=['POST'])
def create_root():
    data = request.args
    if (not data or not data['user_id']): abort(400, 'User id not found')
    else: user_id = data['user_id']
    while True:
        room_id = random.randint(0, 100)
        if room_id not in rooms.keys():
            rooms[room_id] = {
                
            }
        else: break
        print(rooms)
    return(jsonify(
        ROOM_ID=room_id
    ))
app.run()