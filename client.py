import tkinter as tk
import socket
#import threading
import argparse

#Klasa Klient
class Client:
    def __init__(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Stworzono socket")
        except socket.error as err:
            print("Nie udało się stworzyć socketu")
        
    #łączenie się z serwerem
    def connect(self):
        try:
            self.s.connect((args.server_address, int(args.port)))
            print("Udało się połączyć z serwerem")
        except:
            print("Nie udało się połączyć z serwerem")

#Wczytywanie adresu serwera i nr portu jako argumentów przy uruchamianiu 
parser = argparse.ArgumentParser()
parser.add_argument("server_address")
parser.add_argument("port")
args = parser.parse_args()  

#Stworzenie okna aplikacji
root = tk.Tk()
root.geometry('300x200')
root.title("Publish/subscribe Client")

frame = tk.Frame(master=root)
frame.pack(fill=None)

#Funkcja odpowiadająca za dodanie przycisków do aplkacji
def buttons():
    for i in "Dodaj temat", "Wyślij wiadomość", "Zasubskrybuj temat", "Anuluj subskrybcję", "Wyjście":
        b = tk.Button(master=frame, text=i)
        b.pack(side="top", fill="both")
        yield b

b1, b2, b3, b4, b5 = buttons()

#Stworzenie instancji klasy Klient i połączenie z serwerem na podstawie podanych argumentów
c1 = Client()
c1.connect()

#Funkcja kończąca działanie klienta
def destroy():
    root.destroy()

#Przypisanie akcji do przycisków
b5.configure(command=destroy)

#Stworzenie okna
root.mainloop()
    