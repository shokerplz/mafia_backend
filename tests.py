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
    print('http://localhost:5000/action?action=vote&user_id='+user_id+'&target_id='+target_id)
    try:
        r = requests.post('http://localhost:5000/action?action=vote&user_id='+user_id+'&target_id='+target_id)
        voted_json = r.json()
    except:
        print(r.text)
        voted_json = r.text
    return(voted_json)

def kill(user_id, target_id):
    print('http://localhost:5000/action?action=kill&user_id='+user_id+'&target_id='+target_id)
    try:
        r = requests.post('http://localhost:5000/action?action=kill&user_id='+user_id+'&target_id='+target_id)
        voted_to_kill_json = r.json()
    except:
        print(r.text)
        voted_to_kill_json = r.text
    return(voted_to_kill_json)

#try:
user_id = create_user()
room_id = create_room(user_id, '9')
users_in_room = []
for i in range(9):
    new_user_id = create_user()
    users_in_room.append(new_user_id)
    join_room(room_id, new_user_id)['users']
for user in users_in_room:
    set_ready(user)
time.sleep(10)
room_status = json.loads(get_status(users_in_room[1]))
print('ROOM STATUS ON FIRST READY: ')
print(room_status)
print('\n')
for player in room_status['users']:
    if (player['role'] == 'mafia'):
        print(player['id'])
        set_ready(player['id'])
time.sleep(15)
while not room_status['state'].startswith('ended'):
    room_status = json.loads(get_status(users_in_room[1]))
    print('ROOM STATUS ON MAFIA READY: ')
    print(room_status)
    print('\n')
    to_vote = random.choice(users_in_room)
    for user in users_in_room:
        vote(random.choice(users_in_room), to_vote)
    time.sleep(10)
    room_status = json.loads(get_status(users_in_room[1]))
    print('ROOM STATUS AFTER VOTE: ')
    print(room_status)
    print('\n')
    time.sleep(10)
    to_kill = random.choice(users_in_room)
    for player in room_status['users']:
        if (player['role'] == 'mafia'):
            kill(player['id'], to_kill)
    time.sleep(10)
    room_status = json.loads(get_status(users_in_room[0]))
    print('ROOM STATUS AFTER KILL: ')
    print(room_status)
    print('\n')
        

#except Exception as e:
#    print(e)