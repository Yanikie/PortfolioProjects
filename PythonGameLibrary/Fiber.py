# ------------------------------------------------------------------------ Terminal GUI --------------------------------------------------------------------------
import os
from tkinter import *
from Games.Galgje import galgjeSpel
from Games.RaadHetNummer import raadHetNummer
from Games.RockPaperScissors import steenPapierSchaar
from Games.Blackjack import eenentwintigen
from Applications.WieBetaaltWat import splitser

def clear_terminal():
    os.system('cls')
clear_terminal()
# These functions will be starting the games that the buttons correspond to
def button1():
    potje = galgjeSpel()
def button2():
    potje = splitser()
def button3():
    potje = raadHetNummer()
def button4():
    potje = steenPapierSchaar()
def button5():
    potje = eenentwintigen()

# With Tk() a window is launched containing all following labels and buttons
root = Tk()
root.title("Fiber XL")
root.geometry("600x300")
# This sets the background to a blue greyish background
root.config(bg='#4c5563')

# Most speaks for itself only thing to note is that variables are needed if config needs to be changed later
label_welcome = Label(root, text='Welcome to Fiber XL!', fg= '#c5d2ed', bg= '#4c5563')
label_options = Label(root, text="Please click the button of the game you want to play:",fg= '#c5d2ed', bg= "#4c5563")

button_galgje = Button(root, text='Galgje', fg= '#c5d2ed', bg= '#4c5563', command = button1)
button_wbw = Button(root, text='Wie Betaalt Wat', fg= '#c5d2ed', bg= '#4c5563', command= button2)
button_RHN = Button(root, text="Raad Het Nummer", fg= '#c5d2ed', bg= '#4c5563', command= button3)
button_SPS = Button(root, text="Steen Papier Schaar", fg= '#c5d2ed', bg= '#4c5563', command= button4)
button_blackjack = Button(root, text="Blackjack", fg= '#c5d2ed', bg= '#4c5563', command= button5)
button_stop = Button(root, text="Stop de applicatie", fg= '#c5d2ed', bg= '#4c5563',command= root.destroy)

# The grid cannot be put behind the original setup of the button or label as that makes it NoneType
label_welcome.grid(row=0, column=3, pady=10, sticky="nsew")
label_options.grid(row=1, column=3, pady=10, sticky="nsew")
button_RHN.grid(row=2, column=1, pady=10, padx = 10, ipadx= 20, sticky="ns")
button_wbw.grid(row=2, column=5, pady=10, padx = 10, ipadx= 20, sticky="ns")
button_galgje.grid(row=2, column=3, pady=10, padx = 10, ipadx= 20, sticky="ns")
button_SPS.grid(row=3, column=5, pady=10, padx = 10, ipadx= 20, sticky="ns")
button_blackjack.grid(row=3, column=1, pady=10, padx = 10, ipadx= 20, sticky="ns")
button_stop.grid(row=4, column=3, pady=10, ipadx= 20, sticky="ns")
# sets the way the columns interact with a window change
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(5, weight=1)
# If this file is ran only the following things are ran
if __name__ == "__main__":
    root.mainloop()