import random
import os
from tkinter import *
def clear_terminal():
    os.system('cls')
clear_terminal()

# ------------------------------------------------------------------------Raad Het Nummer--------------------------------------------------------------------------

class raadHetNummer:
    def __init__(self):
        # Window control zorgt voor een duidelijke overview
        rhn_gui = Tk()
        self.rhn_gui = rhn_gui
        self.rhn_gui.title("Raad Het Nummer")
        self.rhn_gui.geometry("900x550")
        self.rhn_gui.config(bg='#4c5563')

        # Top Tekst
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(rhn_gui, text= "Hier begint Raad Het Nummer!", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(rhn_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")
        # Label voor verduidelijking
        Label(rhn_gui, text= "Vul hier het einde van de range in:",fg= '#c5d2ed', bg= '#4c5563').grid(row=2, column= 1)
        self.range_entry = Entry(rhn_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.range_entry.config(disabledbackground= "#373d47")
        self.range_entry.grid(row=2,column= 2,sticky= "nsew")
        # Range submit Button: Nodig voor het starten van het spel 
        self.range_submit = Button(rhn_gui, text="Submit range", fg= '#c5d2ed', bg= '#4c5563',command= self.kies_nummer)
        self.range_submit.grid(row=2, column= 5, sticky= "nsew")        
        
        Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Welk nummer gok je:").grid(row=4, column= 1)
        self.gok_entry = Entry(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', state= DISABLED, disabledbackground="#373d47")
        self.gok_entry.grid(row=4, column= 2, sticky= "ns")

        self.gok_button = Button(rhn_gui, state= DISABLED, fg= '#c5d2ed', bg= '#4c5563', text= "Submit gok", command= self.gok)
        self.gok_button.grid(row= 4, column= 5,sticky= "nsew")

        self.error_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.error_label.grid(row= 5, column= 1)
        # Door meerdere labels te gebruiken kan elke optie blijven staan
        self.keuze1_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.keuze1_label.grid(row= 5, column= 3)
        self.keuze2_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.keuze2_label.grid(row= 6, column= 3)
        self.keuze3_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.keuze3_label.grid(row= 7, column= 3)
        self.keuze4_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.keuze4_label.grid(row= 8, column= 3)
        self.keuze5_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.keuze5_label.grid(row= 9, column= 3)
        self.result_label = Label(rhn_gui, fg= '#c5d2ed', bg= '#4c5563', text="")
        self.result_label.grid(row= 10, column= 3)

        # Een canvas wordt gebruikt om het figuur te maken dit is hier het makkleijkst
        self.canvas = Canvas(rhn_gui,width=400, height=200, bg= '#4c5563',bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(row=11,column= 3,padx=30, pady= 10, sticky= "nsew")
        # Zet dit in een init om ervoor te zorgen dat deze variabele op meerdere plekker gebruikt kan worden
        self.keuzes = 0
        self.nummerlijnlist = []


        # Bottom Tekst
        self.button_opnieuw = Button(rhn_gui, text="Nieuw spel", fg= '#c5d2ed', bg= '#4c5563', command= self.nieuw_spel)
        self.button_opnieuw.config(state= DISABLED)
        self.button_opnieuw.grid(row= 20,column= 1, sticky= "nsew")
        # Stop button: Geen variabel nodig want deze heeft maar 1 executie en dat is het programma afsluiten
        Button(rhn_gui, text="Stop de applicatie", fg= '#c5d2ed', bg= '#4c5563', command= self.rhn_gui.destroy).grid(row= 20,column= 3, sticky= "ns")
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(rhn_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=19,columnspan= 300, sticky= "nsew")

        rhn_gui.mainloop()


    def nummerlijn(self):
        '''
        Het doel moet aangegeven worden met een X
        De keuze moet aangegeven worden met een |
        Alle andere getallen geven een -
        Als het getal geraden is wordt alleen de | aangegeven niet het X    
        '''
        # Eerst een string aanmaken om die vervolgens te vullen met alle scores
        canvas_print = ''

        # Loop door de gegokte nummers heen en print een lijn met getallen die gegokt moet worden
        for i in self.nummerlijnlist:
            if i < self.doel:
                canvas_print += ((i-1) * '-' + '|' + (self.doel-i-1) * '-' + 'X' + (self.range_end - self.doel) * '-') + "\n" 
            elif i > self.doel:
                canvas_print += ((self.doel-1) * '-' + 'X' + (i-self.doel-1) * '-' + '|' + (self.range_end - i) * '-') + "\n"
            elif i == self.doel:
                canvas_print += ((i-1) * '-' + '|'  + (self.range_end - i) * '-') + "\n"
        self.canvas.create_text(200, 100, text=canvas_print)
        
    # Met een functie kan de try except vaker gebruikt worden wat voor duidelijkheid zorgt
    def input_check(self,user):
        try:
            int(user)
        except:
            print('Alleen een integer mag ingevuld worden')
            replay = input('Wil je het nog eens proberen? (Ja voor nog een keer proberen) ')
            if replay.upper() == 'JA':
                self.kies_nummer()
            else:
                return


    def kies_nummer(self):
        # Knoppen uitzetten en andere aanzetten. Om edge cases te voorkomen
        self.range_entry.config(state= DISABLED)
        self.range_submit.config(state= DISABLED)
        self.gok_entry.config(state= NORMAL)
        self.gok_button.config(state=NORMAL)
        self.button_opnieuw.config(state= NORMAL)

        # Range bepalen
        self.range_start = 1
        range_input = self.range_entry.get()
        self.input_check(range_input) 
        self.range_end = int(range_input)
        self.doel = random.randint(self.range_start,self.range_end)


    def gok(self):
        # Elke iteration nieuwe gok
        user_input = self.gok_entry.get()
        # Try except statemtent om te checken of het een int statement is 
        try:
            user = int(user_input)
        except:
            # Verlaag de keuzes om te voorkomen dat de user zich dom voelt
            self.error_label.config(text= "Voer een Integer in alsjeblieft")
            return
        self.keuzes += 1
        # Match case om te oefenen en om uit te zoeken op welk moment de user is in het spel
        match self.keuzes:
            case 1:
                moment = self.keuze1_label
            case 2: 
                moment = self.keuze2_label
            case 3:
                moment = self.keuze3_label
            case 4:
                moment = self.keuze4_label
            case 5:
                self.gok_entry.config(state= NORMAL)
                self.gok_button.config(state=NORMAL)   
                moment = self.keuze5_label

        geraden = False
        # Als het goed geraden is moet dat aangegeven worden
        if user == self.doel:    
            moment.config(text=f"Goed gedaan, je hebt het nummer geraden! Het was: {self.doel}. \nJe hebt er {self.keuzes} keer over gedaan\n")
            self.nummerlijnlist.append(user)
            geraden = True
            # Zorg dat de code niet doorloopt als het getal al geraden is
        # Aangeven wanneer het lager is dan het gewenste getal
        elif user < self.doel:
            moment.config(text="Helaas fout, je antwoord moet hoger liggen")
            self.nummerlijnlist.append(user) 
        # Aangeven wanneer het hoger is dan het gewenste getal
        elif user > self.doel:
            moment.config(text= 'Helaas fout, je antwoord moet lager liggen') 
            self.nummerlijnlist.append(user) 

        if geraden == True:
            # Roep de functie aan die voor een score zorgt
            self.nummerlijn()
            self.gok_entry.delete(0,END)
            self.gok_entry.config(state= DISABLED)
            self.gok_button.config(state= DISABLED)

        if self.keuzes >= 5:
            # Aangeven dat de keuzes op zijn
            if geraden == False:     
                self.result_label.config(text= 'Je hebt er te vaak over gedaan, helaas!')
            # Code om een track record te laten zien
            self.nummerlijn() 
            

    def nieuw_spel(self):
        # Woohoooo nu mag alles leeg en terug naar hoe het eerst was
        self.gok_entry.delete(0,END)
        self.range_entry.config(state= NORMAL)
        self.range_submit.config(state= NORMAL)
        self.gok_entry.config(state= DISABLED)
        self.gok_button.config(state=DISABLED)
        self.keuze1_label.config(text= "")
        self.keuze2_label.config(text= "")
        self.keuze3_label.config(text= "")
        self.keuze4_label.config(text= "")
        self.keuze5_label.config(text= "")
        self.result_label.config(text= "")
        self.canvas.delete("all")
        self.keuzes = 0
        self.nummerlijnlist = []

        
if __name__ == "__main__":
    potje = raadHetNummer()

    