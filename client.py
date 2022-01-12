import tkinter as tk
import socket
import argparse

BUFFSIZE = 302
TOPICLENGTH = 99
TOPICSNUMBER = 2
MSG_LENGTH = 200

#Wczytywanie adresu serwera i nr portu jako argumentów przy uruchamianiu 
parser = argparse.ArgumentParser()
parser.add_argument("server_address")
parser.add_argument("port")
args = parser.parse_args()  

def add_window(size = '300x200', title = "Client App"):
    window = tk.Tk()
    window.geometry(size)
    window.title(title)
    return window

def add_label(anchor, txt = ""):
    label = tk.Label(master = anchor, text = txt)
    label.pack()
    return label

def add_entry(anchor):
    entry = tk.Entry(master = anchor)
    entry.pack()
    return entry

def add_button(anchor, txt = ""):
    button = tk.Button(master = anchor, text = txt)
    button.pack(fill="both")
    return button

def buttons():
    for i in "Dodaj temat", "Wyślij wiadomość", "Zasubskrybuj temat", "Anuluj subskrybcję", "Wyświetl tematy", "Odbierz wiadomości", "Wyjście":
        b = tk.Button(master=root, text=i)
        b.pack(side="top", fill="both")
        yield b

#Funkcja łącząca z serwerem
def connect(root, server_addr, port):
    feedback_window = add_window()
    button = add_button(feedback_window, "OK")
    button.configure(command = feedback_window.destroy)

    try:
        connection_socket_description = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        add_label(feedback_window, "Nie udało się stworzyć socketu")
        button.configure(command = lambda:[feedback_window.destroy(), root.destroy()])

    connection_socket_description.connect((server_addr, port))
    feedback = str(connection_socket_description.recv(BUFFSIZE).decode())
    
    if feedback[0] == "r":
        add_label(feedback_window, feedback[1:])
        button.configure(command = lambda:[feedback_window.destroy(), root.destroy()])
    else:
        add_label(feedback_window, feedback)

    return connection_socket_description

#Funkcja kończąca działanie klienta
def close_app(sockfd):
    sockfd.send('e'.encode())
    sockfd.close()
    root.destroy()

def display_msg(sockfd):
    msg = 'w'
    sockfd.send(msg.encode())
    message_num = str(sockfd.recv(TOPICSNUMBER).decode())
    messages_window = add_window('600x200', "Wiadomości")
    add_label(messages_window, "Wiadomości: \n")
    for i in range(int(message_num[0])):
        message = str(sockfd.recv(BUFFSIZE).decode())
        topic_length = int(message[1:3])
        _ = add_label(messages_window, message[3:3+topic_length] + ":\t" + message[3+topic_length:])
    exit_button = add_button(messages_window, "OK")
    exit_button.configure(command=messages_window.destroy)

def display_topics(sockfd):
    msg = "t"
    sockfd.send(msg.encode())
    topics_num = str(sockfd.recv(TOPICSNUMBER).decode())
    topics_window = add_window('500x200')
    _ = add_label(topics_window, "Aktualna lista tematów: \n")
    for i in range(int(topics_num[0])):
        _ = add_label(topics_window, str(sockfd.recv(TOPICLENGTH).decode()))
    exit_button = add_button(topics_window, "OK")
    exit_button.configure(command=topics_window.destroy)

#Funkcja dodająca nowy temat
def action(akcja, sockfd, entry, view, msg_entry = None):
    feedback = ""
    msg = akcja
    topic = str(entry.get())
    if len(topic) == 0:
        err_window = add_window(title="Błąd")
        add_label(err_window, "Nie podano tematu")
        exit_button = add_button(err_window, "OK")
        exit_button.configure(command=err_window.destroy)
    elif len(topic) > TOPICLENGTH:
        err_window = add_window(title="Błąd")
        add_label(err_window, "Podano za długi temat")
        exit_button = add_button(err_window, "OK")
        exit_button.configure(command=err_window.destroy)
    else:
        if len(topic) < 10:
            msg+='0'
        msg+=str(len(topic))
        msg+=topic

        #Wysyłanie wiadomości
        if akcja == "s":
            message = str(msg_entry.get())
            if len(message) == 0:
                err_window = add_window(title="Błąd")
                add_label(err_window, "Nie podano treści wiadomości")
                exit_button = add_button(err_window, "OK")
                exit_button.configure(command=err_window.destroy)
            elif len(message) > MSG_LENGTH:
                err_window = add_window(title="Błąd")
                add_label(err_window, "Wiadomość przekracza liczbę znaków")
                exit_button = add_button(err_window, "OK")
                exit_button.configure(command=err_window.destroy)
            else:
                msg+=message
                sockfd.send(msg.encode())
                feedback = str(sockfd.recv(BUFFSIZE).decode())
                feedback_window = add_window(title = 'Server Feedback')
                feedback_label = add_label(feedback_window)
                exit_button = add_button(feedback_window, "OK")
                exit_button.configure(command=feedback_window.destroy)
        
        #Subskrybcja, dodawanie tematu, anulowanie subskrybcji
        else:
            print(msg)
            sockfd.send(msg.encode())
            feedback = str(sockfd.recv(BUFFSIZE).decode())
            feedback_window = add_window(title = 'Server Feedback')
            feedback_label = add_label(feedback_window)
            exit_button = add_button(feedback_window, "OK")
            exit_button.configure(command=feedback_window.destroy)

        if feedback[0] == "r":
            feedback_label.configure(text = feedback[1:])
        else:
            feedback_label.configure(text = feedback)
            view.destroy()

#Funkcja odpowiadająca za wprowadzanie tematu
def insert_view():
    inserting_window = add_window()
    add_label(inserting_window, "Wprowadź nazwę tematu: ")
    entry = add_entry(inserting_window)
    apply_button = add_button(inserting_window, "Zatwierdź")
    cancel_button = add_button(inserting_window, "Anuluj")
    cancel_button.configure(command=inserting_window.destroy)
    return inserting_window, entry, apply_button


def insert_topic():
    window, entry, button = insert_view()
    button.configure(command=lambda:action("a", sockfd, entry, window))

def subscribe_topic():
    window, entry, button = insert_view()
    button.configure(command=lambda:action("f", sockfd, entry, window))

def unsubscribe_topic():
    window, entry, button = insert_view()
    button.configure(command=lambda:action("u", sockfd, entry, window))

def send_message_view():
    sending_window = add_window()
    add_label(sending_window, "Wprowadź nazwę tematu: ")
    entry = add_entry(sending_window)
    add_label(sending_window, "Wprowadź wiadomość: ")
    msg_entry = add_entry(sending_window)
    apply_button = add_button(sending_window, "Zatwierdź")
    cancel_button = add_button(sending_window, "Anuluj")
    cancel_button.configure(command=sending_window.destroy)
    return sending_window, entry, msg_entry, apply_button

def send_message():
    window, entry, msg_entry, apply_button = send_message_view()
    apply_button.configure(command=lambda:action("s", sockfd, entry, window, msg_entry))

#Stworzenie okna aplikacji
root = add_window('600x400', "Publish/subscribe Client")

#Łączenie się z serwerem
sockfd = connect(root, args.server_address, int(args.port))

add_label(root, "\nWitamy w aplikacji publish/subscribe!\n\n Wybierz jedną z poniższych opcji: \n")

b1, b2, b3, b4, b5, b6, b7 = buttons()

#Przypisanie akcji do przycisków
b1.configure(command=insert_topic)
b2.configure(command=send_message)
b3.configure(command=subscribe_topic)
b4.configure(command=unsubscribe_topic)
b5.configure(command=lambda:display_topics(sockfd))
b6.configure(command=lambda:display_msg(sockfd))
b7.configure(command=lambda:close_app(sockfd))

#Stworzenie okna
root.mainloop()
    