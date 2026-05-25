import random
import os
from tkinter import *

def clear_terminal():
    os.system('cls')
clear_terminal()
# Beelden die later geprint worden in een canvas
galgje_beelden = ['''\n\n\n\n
     ===''','''

      |
      |
      |
     ==='''
    ,'''
   +---+
       |
       |
       |
      ===''', '''
   +---+
   O   |
       |
       |
      ===''', '''
   +---+
   O   |
   |   |
       |
      ===''', '''
   +---+
   O   |
  /|   |
       |
      ===''', '''
   +---+
   O   |
  /|\  |
       |
      ===''', '''
   +---+
   O   |
  /|\  |
  /    |
      ===''', '''
   +---+
   O   |
  /|\  |
  / \  |
      ===''']
class galgjeSpel:
    def __init__(self):
        # Window control
        galgje_gui = Tk()
        self.galgje_gui = galgje_gui
        self.galgje_gui.title("Galgje")
        self.galgje_gui.geometry("700x500")
        self.galgje_gui.title("Galgje")
        self.galgje_gui.config(bg='#4c5563')

        # Top Tekst
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(galgje_gui, text= "Hier begint Galgje!", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(galgje_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,columnspan= 300, sticky= "nsew")
        # Label Zorgt voor duidelijkheid geen variabel want veranderd niet
        Label(galgje_gui, text= "Uw gebruikersnaam: ", fg= '#c5d2ed', bg= '#4c5563').grid(row=2, column= 0, sticky= "nsew")
        # Username entry box: Heeft een variabel omdat hij nog veranderd
        self.username = Entry(galgje_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.username.grid(row=2, column= 1, sticky= "nsew")
        # Username submit Button: Nodig voor het starten van het spel 
        self.submit_username = Button(galgje_gui, text="Submit username", fg= '#c5d2ed', bg= '#4c5563',command= self.start_game)
        self.submit_username.grid(row=2, column= 5, sticky= "nsew")
        # Label: Leeg kan gevuld worden met nuttige error informatie
        self.error_label= Label(galgje_gui, text="",fg= '#c5d2ed', bg= '#4c5563')
        self.error_label.grid(row=3, column=3 , sticky= "nsew")
        # Het enige canvas: Deze is vereist voor het maken van het plaatje van galgje
        self.canvas = Canvas(galgje_gui, width=200, height=200, bg= '#4c5563')
        self.canvas.grid(row=4,column= 3,padx=30, pady= 10, sticky= "nsew")
        # Label: Laat zien waar de letter ingevoerd moet worden
        Label(galgje_gui, text="Raad een letter:", fg= '#c5d2ed', bg= '#4c5563').grid(row= 5, column=0, sticky= "nsew")
        # Letter Entry box: Nodig om de geraden letter uit te lezen. Variabele omdat deze leeg gemaakt moet worden elke keer
        self.karakter_box = Entry(galgje_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.karakter_box.config(state="disabled", disabledbackground="#373d47")
        self.karakter_box.grid(row=5, column= 1, sticky= "nsew")
        # Confirm Button: Nodig om de letter door te geven veranderd nog wel eens dus variabel nodig
        self.confirm_gok= Button(galgje_gui, text="Confirm letter",fg= '#c5d2ed', bg= '#4c5563', command=self.user_gokt, state= DISABLED)
        self.confirm_gok.grid(row = 5, column= 5, sticky= "nsew")
        # Label: Empty is nodig om hier een error te geven voor geraden letters        
        self.communicatie_label = Label(galgje_gui, text="",fg= '#c5d2ed', bg= '#4c5563')
        self.communicatie_label.grid(row= 6, column=3, sticky= "nsew")
        # Label: Empty is nodig om hier een update geven voor geraden letters        
        self.bottom_error_label = Label(galgje_gui, text="",fg= '#c5d2ed', bg= '#4c5563')
        self.bottom_error_label.grid(row= 7, column=3, sticky= "nsew", padx= 10)

        # Bottom Tekst
        self.button_opnieuw = Button(galgje_gui, text="Nieuw spel", fg= '#c5d2ed', bg= '#4c5563', command= self.nieuw_spel)
        self.button_opnieuw.config(state= DISABLED)
        self.button_opnieuw.grid(row= 20,column= 1, sticky= "nsew")
        # Stop button: Geen variabel nodig want deze heeft maar 1 executie en dat is het programma afsluiten
        Button(galgje_gui, text="Stop de applicatie", fg= '#c5d2ed', bg= '#4c5563', command= self.galgje_gui.destroy).grid(row= 20,column= 3, sticky= "ns")
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(galgje_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=19,columnspan= 300, sticky= "nsew")

        galgje_gui.mainloop()

    def start_game(self):
        self.geraden = False
        # Verander status voor user zodat niet edge cases ontstaan
        self.karakter_box.config(state= NORMAL)
        self.username.config(state="disabled", disabledbackground="#373d47")
        self.username_input = self.username.get()
        if not self.username_input:
            self.error_label.config(text="Voer alstublieft een gebruikersnaam in.")
            return
        # Try except of het bestand bestaat
        try:
            with open('Games/wordlist.txt', 'r') as file:
                woorden = file.read().split("\n")
                # Er staan 413938 woorden in deze lijst dus moet er een woord gekozen worden tussen die range
                woordnummer = random.randint(0,len(woorden))
                self.woord_lijst = list(woorden[woordnummer].lower())
        except:
            self.error_label.config(text="Kan het woordenbestand niet vinden.")
            return
        # verander de status van gokken want user is niet altijd handig
        self.confirm_gok.config(state= NORMAL)
        self.submit_username.config(state=DISABLED)
        self.button_opnieuw.config(state= NORMAL)

        self.ongeraden_woord = ['_'] * len(self.woord_lijst)
        self.geraden_letters = []
        self.foute_letters = []
        self.geraden = False
        
        self.update_canvas()
        self.update_message()
        
    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_text(100, 100, text=galgje_beelden[len(self.foute_letters)],font=("Courier", 20))

    def update_message(self):
        ongeraden_woord = ''.join(self.ongeraden_woord)
        geraden_letters = ', '.join(self.geraden_letters)
        self.bottom_error_label.config(text=f"Woord: {ongeraden_woord}\nGeraden letters: {geraden_letters}\nPogingen over: {8-len(self.foute_letters)}")


    def user_gokt(self):
        karakter = self.karakter_box.get().lower()
        self.karakter_box.delete(0, END)
        if len(karakter) != 1:
            self.communicatie_label.config(text="Voer alstublieft één enkele letter in.")
            return
        
        counter = -1
        juist = False
        # Check of de letter al geraden is en zorg dat als het geraden is er een bericht uit wordt geprint en niks meer
        if karakter not in self.geraden_letters:
            self.geraden_letters.append(karakter)
            gokwoord = ''.join(self.ongeraden_woord)
            # Zorg dat niet maar de eerste editie van de letter genoteerd wordt
            for i in self.woord_lijst:
                counter += 1
                if karakter == i:
                    # Als er een goed karakter gegokt is moet er maar 1 bericht geprint worden en wordt de huidige status van het woord laten zien
                    juist = True
                    self.ongeraden_woord[counter] = karakter
                    gokwoord = ''.join(self.ongeraden_woord)

            if juist == True:
                self.communicatie_label.config(text='Gefeliciteerd, het is een goed geraden letter ')
            else:
                # Maak de foute_letters lijst eentje langer zodat de while loop niet oneindig is
                self.foute_letters.append(karakter)
                self.communicatie_label.config(text='Helaas, de letter zit niet in het woord')
        else:
            self.communicatie_label.config(text='Deze letter is al geraden')
            return

        self.update_canvas()
        self.update_message()
        woord= "".join(self.woord_lijst)
        if gokwoord == woord:
            self.communicatie_label.config(text=f"Gefeliciteerd {self.username_input}, je hebt gewonnen!")
            self.end_game()

        if len(self.foute_letters) > 7:
            self.communicatie_label.config(text=f"Jammer, het woord was '{woord}'.")
            self.end_game()

    def end_game(self):
        woord= "".join(self.woord_lijst)
        self.confirm_gok.config(state=DISABLED)
        self.karakter_box.config(state=DISABLED)
        with open("Games/GalgjeSpelers.txt", 'a') as file:
            file.write(f"{self.username_input}: {woord}\n")

    def nieuw_spel(self):
        # Hoppaa alles terug naar hoe het stond
        self.button_opnieuw.config(state= DISABLED)
        self.karakter_box.config(state=DISABLED)
        self.confirm_gok.config(state=DISABLED)
        self.submit_username.config(state=NORMAL)
        self.username.config(state=NORMAL)
        self.canvas.delete('all')
        self.username.delete(0, END)
        self.error_label.config(text="")
        self.bottom_error_label.config(text="")
        self.communicatie_label.config(text="")

if __name__ == "__main__":
    potje = galgjeSpel()