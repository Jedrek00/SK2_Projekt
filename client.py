import tkinter as tk
import socket
import argparse

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
    for i in "Dodaj temat", "Wyślij wiadomość", "Zasubskrybuj temat", "Anuluj subskrybcję", "Wyjście":
        b = tk.Button(master=root, text=i)
        b.pack(side="top", fill="both")
        yield b

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
        print(error)
        error_view = tk.Tk()
        error_view.title("Komunikat")
        error_label = tk.Label(master = error_view, text=error)
        error_label.pack()
        exit_button = tk.Button(master = error_view, text="OK", command=error_view.destroy)
        exit_button.pack()
        view.destroy()

#Funkcja odpowiadająca za wprowadzanie tematu
def insert_topic():
    inserting_window = add_window()
    label = add_label(inserting_window, "Wprowadź nazwę tematu: ")
    entry = add_entry(inserting_window)
    apply_button = add_button(inserting_window, "Zatwierdź")
    cancel_button = add_button(inserting_window, "Anuluj")
    apply_button.configure(command=lambda:add_topic("a", sockfd, entry, inserting_window))
    cancel_button.configure(command=inserting_window.destroy)

#Łączenie się z serwerem
sockfd = connect(args.server_address, int(args.port))

#Stworzenie okna aplikacji
root = add_window('600x400', "Publish/subscribe Client")

frame = tk.Frame(master=root)
frame.pack(fill=None)

b1, b2, b3, b4, b5 = buttons()

label = tk.Label(master = root)
label.pack()

#Przypisanie akcji do przycisków
b1.configure(command=insert_topic)
b5.configure(command=lambda:close_app(sockfd))

#Stworzenie okna
root.mainloop()
    