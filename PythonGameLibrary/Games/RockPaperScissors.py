from tkinter import *
import random
# Setting up a class so self. can be used to interact with the labels buttons and entryboxes from outside of the init function
class steenPapierSchaar:
    def __init__(self):
        # First 5 lines set up the gui window the rest fills it up
        gui = Tk()
        self.gui = gui
        self.gui.title("Steen Papier Schaar")
        self.gui.geometry("750x550")
        self.gui.config(bg='#4c5563')

        # Top Tekst
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(self.gui, text= "Hier begint Steen Papier Schaar!", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(self.gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")
        self.duidelijk_label = Label(self.gui, text= "Voer jou keuze in: ", fg= '#c5d2ed', bg= '#4c5563')
        self.duidelijk_label.grid(row= 3, column=1)

        self.user_entry = Entry(self.gui, fg= '#c5d2ed', bg= '#4c5563')
        self.user_entry.grid(row=3, column = 2)

        self.keuze_button = Button(self.gui, text="Submit keuze", fg= '#c5d2ed', bg= '#4c5563',command= self.echte_spel)
        self.keuze_button.grid(row=3, column= 3)

        self.veranderend_label = Label(self.gui, text= "", fg= '#c5d2ed', bg= '#4c5563')
        self.veranderend_label.grid(row=4, column= 2)
        self.resultaat_label = Label(self.gui, text= "", fg= '#c5d2ed', bg= '#4c5563')
        self.resultaat_label.grid(row=5, column= 2)
        # Mainloop start de window zonder deze line runt het wel maar wordt er niks laten zien
        self.gui.mainloop()

    def echte_spel(self):
        # Keuze van de computer is van 1 tot en met 3 dus er zijn 3 keuzes voor de computer
        computer = random.randint(1,3)
        user = self.user_entry.get()
        # Match case wordt gebruikt om mezelf hier mee te leren werken en een if loop meer typen was geweest
        match computer:
            case 1:
                self.veranderend_label.config(text="Computer gokt Steen")
                match user.upper():
                    case "STEEN":
                        self.resultaat_label.config(text="Gelijkspel")
                    case "PAPIER":
                        self.resultaat_label.config(text="Gebruiker Wint")
                    case "SCHAAR":
                        self.resultaat_label.config(text="Gebruiker Verliest")
                    case _:
                        self.resultaat_label.config(text="Geen goeie input van de gebruiker")
            case 2:
                self.veranderend_label.config(text="Computer gokt Schaar")
                match user.upper():
                    case "STEEN":
                        self.resultaat_label.config(text="Gebruiker Wint")
                    case "PAPIER":
                        self.resultaat_label.config(text="Gebruiker Verliest")
                    case "SCHAAR":
                        self.resultaat_label.config(text="Gelijkspel")
                    case _:
                        self.resultaat_label.config(text="Geen goeie input van de gebruiker")
            case 3:
                self.veranderend_label.config(text="Computer gokt Papier")
                match user.upper():
                    case "STEEN":
                        self.resultaat_label.config(text="Gebruiker Verliest")
                    case "PAPIER":
                        self.resultaat_label.config(text="Gelijkspel")
                    case "SCHAAR":
                        self.resultaat_label.config(text="Gebruiker Wint")
                    case _:
                        self.resultaat_label.config(text="Geen goeie input van de gebruiker")        
        
if __name__ == "__main__":
    potje = steenPapierSchaar()