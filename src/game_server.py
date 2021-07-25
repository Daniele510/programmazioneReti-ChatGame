#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from game_client import question as q
from game_client import close as c
import player as p
import json
import random as r

def accept_clients():
     while True:
        client, client_address = SERVER.accept()
        print("New player connected.")
        print("%s:%s si è collegato." % client_address)
        client.send(bytes("Hi! Write your name and click Enter", "utf8"))
        indirizzi[client] = client_address
        Thread(target=client_manager, args=(client,)).start()

def client_manager(client):
    playerPresent = True
    while playerPresent:
        playerPresent = False
        name = client.recv(BUFSIZ).decode("utf8")
        for cur in players:
            if(cur.name == name):
                client.send(bytes('Used name, please choose another one', 'utf8'))
                playerPresent = True
                break
    global startGame
    if startGame:
        client.send(bytes('Game already started\n', "utf8"))
        return
    
    clients[client] = name
    player = p.Player(name, roles[r.randrange(6)], 0)
    players.append(player)
    
    client.send(bytes('{welcome}', 'utf8'))
    client.send(bytes('Name: %s Role: %s.\n' % (name, player.role), "utf8"))
    client.send(bytes('Click "Ready" to start.\n', "utf8"))
    broadcast(bytes("%s joined the chat" % name, "utf8"))
    
    #controlli sul msg arrivato al server
    question = None    
    while True:
        msg = client.recv(BUFSIZ)
        if question != None:
            if msg == bytes("{gameover}", "utf8"):
                winner = getWinner()
                startGame = False
                client.send(bytes("{stop}", "utf8"))
                client.send(bytes("The end! Winner: %s Points: %d!" % (winner.name, winner.score), "utf8"))
                question = None
                continue
            questions.remove(question)
            if bytes(question.answer, "utf8").lower() == msg.lower():
                client.send(bytes("Right answer", "utf8"))
                player.score += 1
            else:
                client.send(bytes("Wrong answer", "utf8"))
                if player.score > 0:
                    player.score -= 1
            client.send(bytes("Points: " + str(player.score), "utf8"))
            question = None
            continue
        if msg == bytes("{ready}", "utf8"):
            global ready
            ready = ready + 1
            if(len(clients) > 1 and ready == len(clients)):
                #global startGame
                startGame = True
                broadcast(bytes("{startgame}", "utf8"))
        elif msg == bytes("{quit}", "utf8"):
            players.remove(player)
            clients.pop(client)
            broadcast(bytes("%s left the chat." % name, "utf8"))
            if len(players) == 1 and startGame == True:
                winner = getWinner()
                c = list(clients.keys())[0]
                c.send(bytes('{timestop}', "utf8"))
            break
        elif msg == bytes("{question}", "utf8") :
            question = questions[r.randrange(len(questions))]
            client.send(bytes("{question}", "utf8"))
            client.send(bytes(question.question, "utf8"))
        elif msg == bytes("{gameover}", "utf8"):
            startGame = False
            winner = getWinner()
            client.send(bytes("The end! Winner: %s Points: %d!" % (winner.name, winner.score), "utf8"))
        else:
            broadcast(msg, name + ": ")

def broadcast(msg, prefix=""): 
    for u in clients:
        u.send(bytes(prefix, "utf8") + msg)
        

def getWinner():
    winner = players[0]
    for cur in players:
        if cur.score > winner.score:
            winner = cur
    return winner


#variabili globali 
clients = {}

indirizzi = {}

startGame = False

ready = 0

players = []

roles = ["cuoco","artista","geografo",
         "scienziato","storico"]

#variabili globali legate alla domanda
questions = []
f = open ('../resources/questions.json', 'rb')
data = json.load(f)

for value in data:
    questions.append(q.Question(value['domanda'], value['risposta']));

HOST = ''
PORT = 8080
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("In attesa di connessioni...")
    ACCEPT_THREAD = Thread(target = accept_clients())
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()