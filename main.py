from importing_modules import *
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

def get_user_in_room(user_id, room_id):
    if isinstance(user_id, str):
        user_id = int(user_id)
    if isinstance(room_id, str):
        room_id = int(room_id)
    room = get_room_by_id(room_id)
    return next((p for p in room['users'] if int(p["id"]) == user_id), None)

def get_users_ready(room_id):
    if isinstance(room_id, str):
        room_id = int(room_id)
    room = get_room_by_id(room_id)
    return next((p for p in room['users'] if p["ready"] == 'false'), None)



def get_room_by_id(room_id):
    if isinstance(room_id, str):
        room_id = int(room_id)
    return next((p for p in rooms if p["id"] == room_id), None)

@app.route('/')
def root():
    return("Project root")

@app.route('/get-user-id', methods=['POST'])
def get_user_id():
    i = 0
    while True:
        user_id = random.randint(0, 1000)
        i += 1
        if user_id not in players:
            players.append(user_id)
            players_info.append(dict(player_info_json))
            players_info[len(players_info) - 1]['id'] = user_id
            break
        if (i >= 1000): abort(500, 'Game server can not handle your request')
    return(jsonify(
        USER_ID=user_id
))

@app.route('/create', methods=['POST']) # user_id, users
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
            break # Create function to enter new room
    return(jsonify(
        rooms[index]
    ))

@app.route('/join', methods=['POST']) # id (room_id), user_id
def join_room():
    data = request.args
    if (not data or not data['id']): abort(400, 'Room id not found')
    else: room_id = data['id']
    if (not data or not data['user_id']): abort(400, 'User id not found')
    else: user_id = data['user_id']
    if int(user_id) not in players: abort(400, "Player not found")
    player = get_user_by_id(user_id)
    if (player['in_room'] == 'true'): abort(400, 'You are already in room')
    room = get_room_by_id(room_id)
    if (int(room['max_users'])) <= len(room['users']): abort(400, 'Room is full')
    player_enter_dict = dict(user_json)
    player_enter_dict['id'] = user_id
    player_enter_dict['alive'] = 'true'
    player_enter_dict['votes_against'] = 0
    player_enter_dict['role'] = 'peaceful'
    player_enter_dict['ready'] = 'false'
    users = room['users'].copy()
    users.append(player_enter_dict)
    room['users'] = users
    player = get_user_by_id(user_id)
    if player != None:
        player['in_room'] = 'true'
        player['room_id'] = room_id
    if (int(room['max_users'])) <= len(room['users']): 
        room['state'] = 'game'
        game_thread = threading.Thread(target=game, args=(room,))
        game_thread.start()
    return(jsonify(
        room
    ))

@app.route('/ready', methods=['POST']) # id (user_id)
def set_ready():
    data = request.args
    if (not data or not data['id']): abort(400, 'User id not found')
    else: user_id = data['id']
    if int(user_id) not in players: abort(400, "Player not found")
    player = get_user_by_id(user_id)
    if (player['in_room'] == 'false'): abort(400, 'You are not in room')
    player_in_room = get_user_in_room(user_id, player['room_id'])
    if player_in_room == None: abort(400, "No such player in room")
    player_in_room['ready'] = 'true'
    return(json.dumps({'success':True}), 200, {'ContentType':'application/json'} )

@app.route('/action', methods=['POST']) # action, user_id, target_id
def action():
    data = request.args
    if (not data or not data['user_id']): abort(400, 'User id not found')
    else: user_id = data['user_id']
    if int(user_id) not in players: abort(400, "Player not found")
    player = get_user_by_id(user_id)
    if (player['in_room'] == 'false'): abort(400, 'You are not in room')
    player_in_room = get_user_in_room(user_id, player['room_id'])
    if (player_in_room['ready'] == 'true') : abort(400, "You already voted")

    if (not data or not data['target_id']): abort(400, 'Target id not found')
    else: target_id = data['target_id']
    if int(target_id) not in players: abort(400, "Target not found")
    target = get_user_by_id(target_id)
    if (target['in_room'] == 'false'): abort(400, 'Target is not in room')
    target_in_room = get_user_in_room(target_id, target['room_id'])

    if (not data or not data['action']): abort(400, 'Action not found')
    else: action = data['action']

    room = get_room_by_id(player['room_id'])

    if (action != 'vote' and action != 'kill'): abort(400, 'Wrong action')
    if (action == 'vote' and room['state'] == 'vote' and player_in_room['id'] in room['alive']):
        target_in_room['votes_against'] += 1
        room['voted'] += 1
        return(json.dumps({'success':True}), 200, {'ContentType':'application/json'})
    if (action == 'kill'):
        if player_in_room['role'] == 'mafia' and room['daytime'] == 'night' and player_in_room['id'] in room['mafia']:
            target_in_room['votes_against'] += 1
            room['voted_to_kill'] += 1
            return(json.dumps({'success':True}), 200, {'ContentType':'application/json'} )
        else: abort(400, 'You can not do this action right now')
    else: abort(500, 'Action error')

@app.route('/status', methods=['GET'])
def get_status():
    data = request.args
    if (not data or not data['id']): abort(400, 'User id not found')
    else: user_id = data['id']
    if int(user_id) not in players: abort(400, "Player not found")
    player = get_user_by_id(user_id)
    room = get_room_by_id(player['room_id'])
    return(jsonify(
        room
    ))

def game(room): # main game function
    while get_users_ready(room['id']) != None: time.sleep(0.25)
    time.sleep(5)
    b_factor = 3
    b_amount = round(int(room['max_users']) / b_factor)
    b_indexes = np.random.choice(len(room['users']), b_amount, replace=False)
    black_users = []
    for user in b_indexes:
        tmp_users = room['users'].copy()
        black_users.append(tmp_users[user])
        tmp_users[user]['role'] = 'mafia'
        mafia_arr = room['mafia'].copy()
        mafia_arr.append(tmp_users[user]['id'])
        room['users'] = tmp_users
        room['mafia'] = mafia_arr
        del mafia_arr, tmp_users
    red_users = []
    tmp_users = room['users'].copy()
    for user in tmp_users:
        if user['role'] == 'peaceful': red_users.append(user)
    for user in red_users:
        user['role'] = 'peaceful'
        peaceful_arr = room['peaceful'].copy()
        peaceful_arr.append(user['id'])
        room['peaceful'] = peaceful_arr
        del peaceful_arr
    for user in tmp_users: 
        user['ready'] = 'false'
        user['alive'] = 'true'
        alive = room['alive'].copy()
        alive.append(user['id'])
        room['alive'] = alive
        del alive
    room['users'] = tmp_users
    del tmp_users
    room['daytime'] = 'night'
    room['cicle'] = 1
    while next((p for p in room['users'] if p["ready"] == 'true' and p['role'] == 'mafia'), None) == None:
        time.sleep(0.25)
    time.sleep(5)
    while not check_if_game_ended(room):
        tmp_users = room['users'].copy()
        for user in tmp_users: 
            user['ready'] = 'false'
        room['users'] = tmp_users
        del tmp_users
        room['daytime'] = 'day'
        room['cicle'] += 1
        vote(room)
        time.sleep(5)
        room['daytime'] = 'night'
        time.sleep(2)
        kill(room)
    room['state'] = 'ended won: '+check_if_game_ended(room)[1]
    return(True)

def check_if_game_ended(room):
    if len(room['mafia']) <= 0:
        return(True, 'peaceful')
    if len(room['peaceful']) <= 0:
        return(True, 'mafia')
    if len(room['mafia']) == 1 and len(room['peaceful']) == 1:
        return(True, 'mafia')
    return(False)

def kill(room):
    while room['voted_to_kill'] < len(room['mafia']):
        time.sleep(0.25)
    if (len(room['mafia']) == 0): return(None)
    votes_max = 0
    votes_max_user = ''
    for user in room['users']:
        if user['votes_against'] >= votes_max:
            votes_max = user['votes_against']
            votes_max_user = user
        user['votes_against'] = 0
    
    killed_arr = room['killed'].copy()
    killed_arr.append(votes_max_user['id'])
    room['killed'] = killed_arr

    tmp_arr_1 = room['alive'].copy()
    tmp_arr_1.remove(votes_max_user['id'])
    room['alive'] = tmp_arr_1
    del tmp_arr_1

    tmp_arr = room[votes_max_user['role']].copy()
    tmp_arr.remove(votes_max_user['id'])
    room[votes_max_user['role']] = tmp_arr
    del killed_arr, tmp_arr

    room['voted_to_kill'] = 0

def vote(room):
    room['state'] = 'vote'
    while room['voted'] < (len(room['peaceful']) + len(room['mafia'])):
        time.sleep(0.25)
    votes_max = 0
    votes_max_user = ''
    for user in room['users']:
        if user['votes_against'] >= votes_max:
            votes_max = user['votes_against']
            votes_max_user = user
        user['votes_against'] = 0
    jailed_arr = room['jailed'].copy()
    jailed_arr.append(votes_max_user['id'])
    room['jailed'] = jailed_arr
    tmp_arr = room[votes_max_user['role']].copy()
    tmp_arr.remove(votes_max_user['id'])
    room[votes_max_user['role']] = tmp_arr
    del tmp_arr, jailed_arr

    tmp_arr_1 = room['alive'].copy()
    tmp_arr_1.remove(votes_max_user['id'])
    room['alive'] = tmp_arr_1
    del tmp_arr_1

    room['voted'] = 0
    tmp_users = room['users'].copy()
    for user in tmp_users:
        user['ready'] = 'false'
    room['users'] = tmp_users
    del tmp_users
    return(True)
if __name__ == '__main__':
 app.run(host='0.0.0.0', debug=True, port=80)
