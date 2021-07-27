
import socket 
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from threading import Thread
import sys
import random

TOTAL_NO_OF_ROUNDS = 5
game_round = 0

def receive_message():
    while True:
        try:
            my_msg = client_socket.recv(BUFSIZ).decode("utf8")
            if my_msg == "{welcome}":
                btn_ready['state'] = 'normal'
            elif my_msg == "{startgame}":
                lbl_game_round = tk.Label(text="Game round (x)")
                lbl_game_round.pack()
                countdown_thread.start()
                gameFrame.pack()
                chooseButton()
                text['state'] = 'normal'
                text.insert(tk.END, "GAME START")
                text.insert(tk.END, '\n\n')
                text['state'] = 'disabled'
            elif my_msg == "{question}":   
                chooseButton()
            elif my_msg == "Right answer":
                text['state'] = 'normal'
                text.insert(tk.END, "Correct")
                text.insert(tk.END, '\n\n')
                text['state'] = 'disabled'
                questionText['state'] = 'normal'
                questionText.delete('1.0', tk.END)
                questionText['state'] = 'disabled'
            elif my_msg == "Wrong answer":
                text['state'] = 'normal'
                text.insert(tk.END, "Wrong")
                text.insert(tk.END, '\n\n')
                text['state'] = 'disabled'
                questionText['state'] = 'normal'
                questionText.delete('1.0', tk.END)
                questionText['state'] = 'disabled'
            elif my_msg == "{timestop}":
                game_round = 0   
                lbl_game_round.destroy()
                gameFrame.destroy()
                text['state'] = 'normal'
                text.insert(tk.END, "Other player left the game, you won")
                text.insert(tk.END, '\n')
                text['state'] = 'disabled'
            elif my_msg == "{stop}":
                global selectChat
                entryField['state'] = 'normal'
                selectChat = True
            else:
                if selectChat:
                    text['state'] = 'normal'
                    text.insert(tk.END, my_msg)
                    text.insert(tk.END, '\n')
                    text['state'] = 'disabled'
                else :
                    questionText['state'] = 'normal'
                    questionText.insert(tk.END, my_msg)
                    questionText.insert(tk.END, '\n')
                    questionText['state'] = 'disabled'     
        except OSError:
            break

def question(buttonFrame):
    global selectChat 
    selectChat = False
    answerField['state'] = 'normal'
    entryField['state'] = 'disabled'
    btn_answer['state'] = 'normal'
    msg.set("{question}")
    sendMessage()
    buttonFrame.destroy()
        
def ready():
    client_socket.send(bytes("{ready}", "utf8"))
    btn_ready['state'] = 'disabled'

def sendMessage(event = None):
    my_msg = msg.get()
    msg.set("")
    # invia il messaggio sul socket
    client_socket.send(bytes(my_msg, "utf8"))
    if my_msg == "{quit}":
        client_socket.close()
        window_main.close()

def sendAnswer():
    if not answerField.get():
        messagebox.showwarning("Attenzione","Inserire risposta!")
        return
    global selectChat
    selectChat = True
    entryField['state'] = 'normal'
    answerField['state']='disabled'
    btn_answer['state']='disabled'
    questionText['state'] = 'normal'
    my_answer = answer.get()
    client_socket.send(bytes(my_answer, "utf8"))
    answer.set('')
    questionText['state'] = 'disabled'

    
def closeConnection(event = None):
    client_socket.send(bytes("{quit}", "utf8"))
    game_round = 0
    window_main.destroy()
    sys.exit()


def chooseButton():
    button_frame = tk.Frame(master = gameFrame)
    btn_a = tk.Button(master = button_frame, text="A")
    btn_b = tk.Button(master = button_frame, text="B")
    btn_c = tk.Button(master = button_frame, text="C")
    r = random.randint(1, 3)
    if r==1:
        btn_a.config(command = closeConnection)
        btn_b.config(command = lambda: question(button_frame))
        btn_c.config(command = lambda: question(button_frame))
    elif r==2:  
        btn_b.config(command = closeConnection)
        btn_a.config(command = lambda: question(button_frame))
        btn_c.config(command = lambda: question(button_frame))
    else:
        btn_c.config(command = closeConnection)
        btn_a.config(command = lambda: question(button_frame))
        btn_b.config(command = lambda: question(button_frame))
    inner_label.pack()
    btn_a.pack(side = tk.LEFT)
    btn_b.pack(side = tk.LEFT)           
    btn_c.pack(side = tk.LEFT)
    inner_label.pack()
    button_frame.pack()

def count_down():
    global game_round
    if game_round <= TOTAL_NO_OF_ROUNDS:
        game_round = game_round + 1
        
        game_round["text"] = "Game round " + str(game_round)
    else:
        client_socket.send(bytes("{gameover}", "utf8"))
        gameFrame.destroy()

selectChat = True

window_main = tk.Tk()
window_main.title("ChatGame")
text = tk.Text(height = 15, width = 50)
text['state'] = 'disabled'
text.pack()
label = tk.Label(text = "Write here:")
label.pack()
msg = tk.StringVar()
entryField = tk.Entry(width = 25, textvariable = msg)
entryField.pack()
frame = tk.Frame(master = window_main)
btn_send = tk.Button(master = frame, text = "Send", command = sendMessage)
btn_ready = tk.Button(master = frame, text = "Ready", command = ready)
btn_quit = tk.Button(master = frame, text = "Quit", command = closeConnection)
btn_send.pack(side = tk.LEFT)
btn_ready.pack(side = tk.LEFT)
btn_quit.pack(side = tk.LEFT)
btn_ready['state'] = 'disabled'
frame.pack()

gameFrame = tk.Frame(master = window_main)
questionText = tk.Text(height = 5, width = 50, master = gameFrame)
questionText.pack()
questionText['state'] = 'disabled'
answer = tk.StringVar()
answerField = tk.Entry(width = 25, textvariable = answer, master = gameFrame)
answerField.pack()
btn_answer = tk.Button(text = 'Answer', command = sendAnswer, master = gameFrame)
btn_answer['state'] = 'disabled'
btn_answer.pack()
inner_label = tk.Label(master = gameFrame, text = "Choose one the buttons:")
inner_label.pack()

# Inizializzazione countdown
countdown_thread = Thread(target = lambda: count_down)


#Connessione al server   
HOST = '127.0.0.1'
PORT = 8080

BUFSIZ = 1024
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
receive_thread = Thread(target=receive_message)
receive_thread.start()
tk.mainloop()
