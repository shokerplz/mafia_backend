import requests, time, json, random
def create_user():
    r = requests.post('http://localhost:5000/get-user-id')
    user_id = str(r.json()['USER_ID'])
    return(user_id)

def create_room(user_id, users='3'):
    r = requests.post('http://localhost:5000/create?users='+users+'&user_id='+user_id)
    room_id = str(r.json()['id'])
    return(room_id)

def join_room(room_id, user_id):
    r = requests.post('http://localhost:5000/join?id='+room_id+'&user_id='+user_id)
    joined_json = r.json()
    return(joined_json)

def set_ready(id):
    r = requests.post('http://localhost:5000/ready?id='+id)
    joined_json = r.text
    return(joined_json)

def get_status(id):
    r = requests.get('http://localhost:5000/status?id='+id)
    joined_json = r.text
    return(joined_json)

def vote(user_id, target_id):
    #print('http://localhost:5000/action?action=vote&user_id='+user_id+'&target_id='+target_id)
    try:
        r = requests.post('http://localhost:5000/action?action=vote&user_id='+user_id+'&target_id='+target_id)
        voted_json = r.json()
    except:
        #print(r.text)
        voted_json = r.text
    return(voted_json)

def kill(user_id, target_id):
    #print('http://localhost:5000/action?action=kill&user_id='+user_id+'&target_id='+target_id)
    try:
        r = requests.post('http://localhost:5000/action?action=kill&user_id='+user_id+'&target_id='+target_id)
        voted_to_kill_json = r.json()
    except:
        #print(r.text)
        voted_to_kill_json = r.text
    return(voted_to_kill_json)

def print_status(room_status):
    print('Alive users: '+' '.join(room_status['alive']))
    print('Alive mafia: '+' '.join(room_status['mafia']))
    print('Alive peaceful: '+' '.join(room_status['peaceful']))
    print('Jailed users: '+' '.join(room_status['jailed']))
    print('Killed users: '+' '.join(room_status['killed']))

#try:
USERS_IN_ROOM=9
user_id = create_user()
room_id = create_room(user_id, str(USERS_IN_ROOM))
users_in_room = []
for i in range(USERS_IN_ROOM):
    new_user_id = create_user()
    users_in_room.append(new_user_id)
    join_room(room_id, new_user_id)['users']
for user in users_in_room:
    set_ready(user)
time.sleep(10)
room_status = json.loads(get_status(users_in_room[1]))
print('ROOM STATUS ON FIRST READY: ')
print_status(room_status)
print('\n')
for player in room_status['users']:
    if (player['role'] == 'mafia'):
        #print(player['id'])
        set_ready(player['id'])
time.sleep(15)
room_status = json.loads(get_status(users_in_room[1]))
print('ROOM STATUS ON MAFIA READY: ')
print_status(room_status)
print('\n')
while not room_status['state'].startswith('ended'):
    time.sleep(5)
    room_status = json.loads(get_status(users_in_room[0]))
    for user in users_in_room:
        to_vote = random.choice(users_in_room)
        if to_vote in room_status['alive']: break
        else: continue
    print('All users will vote to: '+to_vote)
    room_status = json.loads(get_status(users_in_room[0]))
    for user in users_in_room:
        if (user in room_status['alive']):
            vote(user, to_vote)
    time.sleep(5)
    room_status = json.loads(get_status(users_in_room[1]))
    print('ROOM STATUS AFTER VOTE: ')
    print_status(room_status)
    print('\n')
    time.sleep(5)
    room_status = json.loads(get_status(users_in_room[0]))
    for user in users_in_room:
        to_kill = random.choice(users_in_room)
        if to_kill in room_status['alive']: break
        else: continue
    print('All mafia will kill: '+to_kill)
    room_status = json.loads(get_status(users_in_room[0]))
    for player in room_status['users']:
        if (player['role'] == 'mafia' and player['id'] in room_status['alive']):
            kill(player['id'], to_kill)
    time.sleep(5)
    room_status = json.loads(get_status(users_in_room[0]))
    print('ROOM STATUS AFTER KILL: ')
    print_status(room_status)
    print('\n')
if ('peaceful' in room_status['state']):
    print('Peaceful won')
else: print('Mafia won')
        

#except Exception as e:
#    print(e)