import requests, time, json, random

def create_user():                           #endpoint POST "Get ID"
    r = requests.post('http://localhost:5000/get-user-id')
    user_id = str(r.json()['USER_ID'])
    return(user_id)

def create_room(user_id, users='3'):         #endpoing POST "Create"
    r = requests.post('http://localhost:5000/create?users='+users+'&user_id='+user_id)
    room_id = str(r.json()['id'])
    return(room_id)

def join_room(room_id, user_id):             #endpoint POST "Join"
    r = requests.post('http://localhost:5000/join?id='+room_id+'&user_id='+user_id)
    joined_json = r.json()
    return(joined_json)

def set_ready(id):                           #endpoint POST "Ready"
    r = requests.post('http://localhost:5000/ready?id='+id)
    joined_json = r.text
    return(joined_json)

def get_status(id):                          #endpoint GET "Status"
    r = requests.get('http://localhost:5000/status?id='+id)
    joined_json = r.text
    return(joined_json)


                                             #endpoint POST "Action"
def vote(user_id, target_id):
    try:
        r = requests.post('http://localhost:5000/action?action=vote&user_id='+user_id+'&target_id='+target_id)
        voted_json = r.json()
    except:
        voted_json = r.text
    return(voted_json)

def kill(user_id, target_id):
    try:
        r = requests.post('http://localhost:5000/action?action=kill&user_id='+user_id+'&target_id='+target_id)
        voted_to_kill_json = r.json()
    except:
        voted_to_kill_json = r.text
    return(voted_to_kill_json)

def print_status(room_status):
    print('Alive users: '+' '.join(room_status['alive']))
    print('Alive mafia: '+' '.join(room_status['mafia']))
    print('Alive peaceful: '+' '.join(room_status['peaceful']))
    print('Jailed users: '+' '.join(room_status['jailed']))
    print('Killed users: '+' '.join(room_status['killed']))



def aliver(aliveusers, someone):             # alive or not
    for user in aliveusers:
        if (user == someone):
            return True
    return False

def canv(users,aliveusers,to):               # can vote
    for user in users:
        if ((user['role'] == 'peaceful' and user['id'] == to) or (not(aliver(aliveusers,to)))):
            return False
    return True


def cank(peacefulusers,users,aliveusers,to): # can kill
    for user in users:
        if ((user['role'] == 'mafia' and user['id'] == to) and (aliver(aliveusers,to))):
            return True
    return False


def scanmafia(users,roomstatus):             # some mafia alive
    for user in users:
        if((user['role'] == 'mafia') and (user['id'] in roomstatus['alive'])):
            return True
    return False





#priority - peaceful

USERS_IN_ROOM = 7                           # players (if players > 9 - upper sleeptime)
NUMBER_OF_ROUNDS = 10                        # rounds
user_id = create_user()                     # id room
room_id = create_room(user_id, str(USERS_IN_ROOM)) 
users_in_room = []

for i in range(USERS_IN_ROOM):
    new_user_id = create_user()             # id user 'i'
    users_in_room.append(new_user_id)
    join_room(room_id, new_user_id)['users']

for user in users_in_room:
    set_ready(user)
time.sleep(5)
room_status = json.loads(get_status(users_in_room[1]))
print('ROOM STATUS ON FIRST READY: ')
print_status(room_status)
print('\nMafia users:')

for player in room_status['users']:
    if (player['role'] == 'mafia'):
        print(player['id'])
        set_ready(player['id'])
time.sleep(5)
room_status = json.loads(get_status(users_in_room[1]))
print('\nROOM STATUS ON MAFIA READY: ')
print_status(room_status)
print('\n')

for rnd in range (NUMBER_OF_ROUNDS):
    time.sleep(5)
    room_status = json.loads(get_status(users_in_room[0]))
    
    if not(scanmafia(room_status['users'],room_status)):  # scan for mafia
        break
    
    print('------------------\n Round ' + str((rnd+1)) + '\n------------------')
    
    for user in users_in_room:
        to_vote = random.choice(users_in_room)
        while not(canv(room_status['users'],room_status['alive'],to_vote)):
            to_vote = random.choice(users_in_room)
    print('All peaceful users will vote to: '+to_vote+'\n')
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
    
    if not(scanmafia(room_status['users'],room_status)):  # scan for mafia
        break
    
    for user in users_in_room:
        to_kill = random.choice(users_in_room)
        while not(cank(room_status['peaceful'],room_status['users'],room_status['alive'],to_kill)):
            to_kill = random.choice(users_in_room)
    print('All mafia will kill: '+to_kill+'\n')
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
    print('Peaceful won. End of the game.')
else: print('Mafia won. End of the game.')
