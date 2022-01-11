import tkinter as tk
import socket
#import threading
import argparse
from tkinter.constants import LEFT, RAISED

#Wczytywanie adresu serwera i nr portu jako argumentów przy uruchamianiu 
parser = argparse.ArgumentParser()
parser.add_argument("server_address")
parser.add_argument("port")
args = parser.parse_args()  

#Stworzenie okna aplikacji
root = tk.Tk()
root.geometry('600x400')
root.title("Publish/subscribe Client")

frame = tk.Frame(master=root)
frame.pack(fill=None)

def buttons():
    for i in "Dodaj temat", "Wyślij wiadomość", "Zasubskrybuj temat", "Anuluj subskrybcję", "Wyjście":
        b = tk.Button(master=frame, text=i)
        b.pack(side="top", fill="both")
        yield b

b1, b2, b3, b4, b5 = buttons()

label = tk.Label(master = root)
label.pack()


#Funkcja łącząca z serwerem
def connect(server_addr, port):
    try:
        connection_socket_description = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Błąd przy próbie utworzenia gniazda")
        label.configure(text="Błąd przy próbie utworzenia gniazda")

    try: 
        connection_socket_description.connect((server_addr, port))
    except:
        print("Błąd przy próbie połączenia z serwerem")
        label.configure(text="Błąd przy próbie połączenia z serwerem")
    
    return connection_socket_description

#Funkcja kończąca działanie klienta
def close_app(sockfd):
    sockfd.send('e'.encode())
    sockfd.close()
    root.destroy()

#Funkcja dodająca nowy temat
def add_topic(akcja, sockfd, entry, view):
    error=""
    buff = akcja
    topic = str(entry.get())
    if len(topic) < 10:
        buff+='0'
    buff+=str(len(topic))
    buff+=topic
    sockfd.send(buff.encode())
    error = str(sockfd.recv(1024).decode())
    if error[0] == "r":
        error_view = tk.Tk()
        error_view.title("Błąd")
        error_label = tk.Label(master = error_view, text=error[1:])
        error_label.pack()
        exit_button = tk.Button(master = error_view, text="OK", command=error_view.destroy)
        exit_button.pack()
    else: 
        view.destroy()

#Funkcja odpowiadająca za wprowadzanie nowych danych
def insert_new_topic():
    inserting_view = tk.Tk()
    inserting_view.title("Wprowadzanie tematu")
    inserting_view.geometry('300x200')
    lab = tk.Label(master = inserting_view, text="Wprowadź nazwę tematu: ")
    lab.pack()
    entry = tk.Entry(master = inserting_view)
    entry.pack()
    butt1 = tk.Button(master = inserting_view, text="Zatwierdź")
    butt2 = tk.Button(master = inserting_view, text="Anuluj")
    butt1.pack()
    butt2.pack()
    butt1.configure(command=lambda:add_topic("a", sockfd, entry, inserting_view))
    butt2.configure(command=inserting_view.destroy)

#Łączenie się z serwerem
sockfd = connect(args.server_address, int(args.port))

#Przypisanie akcji do przycisków
b1.configure(command=insert_new_topic)
b5.configure(command=lambda:close_app(sockfd))

#Stworzenie okna
root.mainloop()
    