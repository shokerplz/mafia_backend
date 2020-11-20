from importing_modules import *
app = Flask(__name__)

global players, rooms

players = []
players_info = []
rooms   = []
room_json = json.load(open("template_room.json"))
user_json = json.load(open("template_user.json"))
player_info_json = json.load(open("template_player_info.json"))

def get_user_by_id(user_id):
    if isinstance(user_id, str):
        user_id = int(user_id)
    return next((p for p in players_info if p["id"] == user_id), None)

def get_room_by_id(room_id):
    if isinstance(room_id, str):
        room_id = int(room_id)
    return next((p for p in rooms if p["id"] == room_id), None)

@app.route('/')
def root():
    return("Project root")

@app.route('/get-user-id', methods=['POST'])
def get_user_id():
    while True:
        user_id = random.randint(0, 100)
        if user_id not in players:
            players.append(user_id)
            players_info.append(dict(player_info_json))
            players_info[len(players_info) - 1]['id'] = user_id
        else: break
    return(jsonify(
        USER_ID=user_id
))

@app.route('/create', methods=['POST'])
def create_root():
    data = request.args
    if (not data or not data['user_id']): 
        abort(400, 'User id not found')
    else: 
        user_id = data['user_id']
    if (not data or not data['users']): 
        abort(400, 'Max users not set')
    else: 
        max_users = data['users']
    if int(user_id) not in players:
        abort(400, "Player not found")
    player = get_user_by_id(user_id)
    if (player['in_room'] == 'true'): 
        abort(400, 'You are already in room')
    while True:
        room_id = random.randint(0, 100)
        if get_room_by_id(room_id) == None:
            rooms.append(dict(room_json))
            index = len(rooms) - 1
            rooms[index]['id'] = room_id
            rooms[index]['max_users'] = max_users
            rooms[index]['state'] = 'joining'
            print(rooms)
            break # Create function to enter new room
    return(jsonify(
        rooms[index]
    ))
@app.route('/join', methods=['POST'])
def join_room():
    data = request.args
    if (not data or not data['id']): 
        abort(400, 'Room id not found')
    else: room_id = data['id']
    if (not data or not data['user_id']): 
        abort(400, 'User id not found')
    else: user_id = data['user_id']
    if int(user_id) not in players:
        abort(400, "Player not found")
    player = get_user_by_id(user_id)
    if (player['in_room'] == 'true'): 
        abort(400, 'You are already in room')
    room = get_room_by_id(room_id)
    if (int(room['max_users'])) <= len(room['users']): 
        abort(400, 'Room is full')
    player_enter_dict = dict(user_json)
    player_enter_dict['id'] = user_id
    users = room['users'].copy()
    users.append(player_enter_dict)
    room['users'] = users
    player = get_user_by_id(user_id)
    if player != None:
        player['alive'] = 'true'
        player['votes_against'] = '0'
        player['in_room'] = 'true'
    print(rooms)
    return(jsonify(
        room
    ))

app.run()