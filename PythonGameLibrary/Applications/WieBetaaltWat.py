import os
from tkinter import *

def clear_terminal():
    os.system('cls')
clear_terminal()

# ------------------------------------------------------------------------ Wie Betaalt Wat --------------------------------------------------------------------------
class splitser:
    def __init__(self):
        self.ja = False
        self.nee = False
        self.namen_nummers = 0
        self.naam_lijst = []
        self.inner_list = []
        self.eind_lijst = []


        wbw_gui = Tk()
        self.wbw_gui = wbw_gui
        self.wbw_gui.config(bg='#4c5563')
        self.wbw_gui.title("Wie Betaalt Wat")
        self.wbw_gui.geometry("750x550")
        # Top Tekst
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(wbw_gui, text= "Wie Betaalt Wat", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(wbw_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")
        
        # Label voor verduidelijking
        Label(wbw_gui, text= "Zit je al in een groep?",fg= '#c5d2ed', bg= '#4c5563').grid(row=2, column= 1)
        v = IntVar()
        self.ja_radio = Radiobutton(wbw_gui, text='Ja', variable=v, value=1,fg= 'Black', bg= '#4c5563',activebackground ='#4c5563', activeforeground= "Black" , command= self.user_wel_groep)
        self.ja_radio.grid(row=2,column= 2 )
        self.nee_radio = Radiobutton(wbw_gui, text='Nee', variable=v, value=2,fg= "Black", bg= '#4c5563', activebackground ='#4c5563', activeforeground= "Black", command= self.user_geen_groep)
        self.nee_radio.grid(row=2, column= 3)

        # Stop button: Geen variabel nodig want deze heeft maar 1 executie en dat is het programma afsluiten
        Button(wbw_gui, text="Stop de applicatie", fg= '#c5d2ed', bg= '#4c5563', command= self.wbw_gui.destroy).grid(row= 20,column= 3, sticky= "ns")
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(wbw_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=19,columnspan= 300, sticky= "nsew")

        wbw_gui.mainloop()


    def splitser_individual(self,number_people,purchases_list):
        # __INIT__
        output_list = []
        bedrag_list = []
        person_list = []

        # Input handling
        try:
            int_people = int(number_people)
        except:
            print('Voer een nummer personen in')
            # Een empty list wordt gegeven om de handling makkelijker te maken
            return output_list
        try:
            aankopen = list(purchases_list)
            if len(aankopen) < 2:
                # Check of er aan de voorwaarden is voldaan
                print('Vergeet niet de persoon_id in de list te vermelden')
                return output_list
        except:
            print('Voer een juiste template van aankopen aan')
            return output_list
        # Initieer een boolean waarde om hier later een check op uit te boeren
        error = False
        # Run een for loop zodat er een check over alle waardes komt
        for i in purchases_list:
            try:
                # Float waarde zodat er een decimale waarde toegevoegd kan worden
                item = float(i)
                purchases_list[purchases_list.index(i)] = item
            except:
                error = True
                print(f'Het item {i} is niet een correcte waarde. Hij staat op positie {purchases_list.index(i)}')
                continue
        # Check of er een error gevonden is
        if error == True:
            return output_list
        # Einde input handling

        # Scheid de bedragen van de mensen
        for i in purchases_list:
            if purchases_list.index(i) % 2 == 1:
                # Check voor user error
                if i > int_people:
                    print(f'De gegeven waarde {i} is te hoog voor het aangegeven nummer mensen')
                    return output_list
                # Voeg alle personen aan een list toe 
                person_list.append(int(i))
            else:
                # Alle getallen op de even indexen zijn bedragen
                bedrag_list.append(i)

        # Vul de lijst met getallen zodat er makkelijk een som gemaakt kan worden
        for i in range(int_people):
            output_list.append(0.0)

        # Haal de som op die vervolgens geoutput gaat worden
        teller = 0
        
        # Heel eerlijk gezegd heb ik het idee dat ik dit veel moeilijker gemaakt dan nodig
        # Zoek voor elk persoon het bijgelegen bedrag en zorg dat de individuele getallen 
        for i in person_list:
            bijbehorend = bedrag_list[teller] 
            output_list[i - 1] += bijbehorend
            teller += 1
        return output_list

    def individual_balance(self,user_number, aankopen):
        '''
        Berekent het individuele balans: besteede bedrag - het gemiddelde bedrag per persoon
        parameters: user_number == int staat voor hoeveelheid mensen in groep
        aankopen == List met aankopen en wie het betaalt heeft
        '''
        # Maak eerst een list met alle bedragen per persoon
        ind_total_list = self.splitser_individual(user_number, aankopen)
        # Als het een empty list is stop dan de functie
        if len(ind_total_list) == 0:
            return
        # Bereken het gemiddelde door de som van alle individuele bedragen te vinden en die te delen door de hoeveelheid mensen
        avg = sum(ind_total_list) / len(ind_total_list)
        # Initieer en vul de output_list
        output_list = []
        for i in range(len(ind_total_list)):
            output_list.append(ind_total_list[i]-avg)
        return output_list


    def user_geen_groep(self,):
        self.ja_radio.config(state = DISABLED)
        self.nee_radio.config(state = DISABLED)
        self.nee = True
        self.wbw_gui.destroy()

        wbw_geen_gui = Tk()
        self.wbw_geen_gui = wbw_geen_gui
        self.wbw_geen_gui.config(bg='#4c5563')
        self.wbw_geen_gui.title("Wie Betaalt Wat")
        self.wbw_geen_gui.geometry("750x550")
        # Top Tekst
        # Geen variabel nodig omdat ze niet veranderd gaan worden
        Label(wbw_geen_gui, text= "Wie Betaalt Wat", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(wbw_geen_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")
        
        
        Label(wbw_geen_gui, text= "Wat wordt de naam van je groep:",fg= '#c5d2ed', bg= '#4c5563').grid(row=2, column= 1)
        self.groepnaam_entry = Entry(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.groepnaam_entry.config(disabledbackground= "#373d47")
        self.groepnaam_entry.grid(row=2,column= 2,sticky= "nsew")

        self.groepnaam_geen_button = Button(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Submit naam", command= self.groepnaam_maken)
        self.groepnaam_geen_button.grid(row= 2, column= 5,sticky= "nswe")

        Label(wbw_geen_gui, text= "Wat wordt het wachtwoord van je groep:",fg= '#c5d2ed', bg= '#4c5563').grid(row=3, column= 1)
        self.wachtwoord_entry = Entry(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.wachtwoord_entry.config(disabledbackground= "#373d47", state= DISABLED)
        self.wachtwoord_entry.grid(row=3,column= 2,sticky= "nsew")
        
        self.wachtwoord_geen_button = Button(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Submit wachtwoord",state= DISABLED, command= self.wachtwoord_maken)
        self.wachtwoord_geen_button.grid(row= 3, column= 5, sticky= "nswe")

        self.error_label = Label(wbw_geen_gui, text= "",fg= '#c5d2ed', bg= '#4c5563')
        self.error_label.grid(row=20, column= 3)

        self.veranderend_label = Label(wbw_geen_gui, text= "Met hoeveel mensen zit je in een groep:",fg= '#c5d2ed', bg= '#4c5563')
        self.veranderend_label.grid(row=4, column= 1)
        self.tellen_entry = Entry(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.tellen_entry.config(disabledbackground= "#373d47", state= DISABLED)
        self.tellen_entry.grid(row=4,column= 2,sticky= "nsew")
        
        self.tellen_geen_button = Button(wbw_geen_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Submit hoeveelheid",state= DISABLED, command= self.groep_maken)
        self.tellen_geen_button.grid(row= 4, column= 5, sticky= "nswe")

        self.eind_label = Label(wbw_geen_gui, text= "",fg= '#c5d2ed', bg= '#4c5563')
        self.eind_label.grid(row=10, column= 3, sticky= "nsew")

        wbw_geen_gui.mainloop()

    def groepnaam_maken(self):
        # Zorg voor een identificeerbaar id waar we de user info mee kunnen opslaan
        choice = self.groepnaam_entry.get()
        # Verander het naar een list om naar info te checken
        choice_list = list(choice)
        # Deze check heb ik nodig omdat ik een hard code check heb zitten naar ':'
        if ':' in choice_list or len(choice_list) == 0:
            self.error_label.config(text=f"Het karakter ':' mag niet in de naam zitten" )
            # Eindig de functie en stuur de user naar de CUI
            return 
        # Lees de file op al bestaande groepen
        with open('Applications/WBW.txt', 'r') as file:
            regels = file.read()
            if regels != '':
                regels_list = regels.split('\n')
        # Haal elke witregel uit de lijst. Deze ontstaat vaak bij de eerste versie van de file.
        while '' in regels_list:
            regels_list.remove('') 

        # Initieer alle lijsten die gevuld worden met de namen en info die in het bestand staan
        groepnamen = []
        wachtwoorden = []
        kasstaat = []
        namen_lijst = []

        # Vul alle lijsten met de corresponderende info
        for i in regels_list:
            groepnamen.append(i.split(': ')[0])
            wachtwoorden.append(i.split(': ')[1])
            kasstaat.append(i.split(': ')[2])
            namen_lijst.append(i.split(': ')[3])
        
        # Dit zal helaas moeten om duplicate info niet bij de verkeerde persoon uit te laten komen
        if choice in groepnamen:
            self.error_label.config(text='Sorry deze groepsnaam is al in gebruik')
            return 
        
        self.groepnaam = choice
        self.wachtwoord_entry.config(state= NORMAL)
        self.wachtwoord_geen_button.config(state= NORMAL)
        self.groepnaam_entry.config(state= DISABLED)
        self.groepnaam_geen_button.config(state=DISABLED)


    def wachtwoord_maken(self):

        # Een wachtwoord encrypt de groep tot een zeker niveau
        ww = self.wachtwoord_entry.get()
        ww_list = list(ww)
        # Hier moet ik helaas weer een check doen naar ':' omdat ik dit gehardcode heb vanuit txt
        if ':' in ww_list:
            self.error_label.config(text="Sorry er mag geen ':' in je wachtwoord zitten!")
            return 
        
        self.wachtwoord = ww
        self.tellen_entry.config(state= NORMAL)
        self.tellen_geen_button.config(state= NORMAL)
        self.wachtwoord_entry.config(state= DISABLED)
        self.wachtwoord_geen_button.config(state=DISABLED)



    def groep_maken(self):
        # Nieuwe groep wordt gemaakt
        number_people = self.tellen_entry.get()

        # Kijk of de waardes kloppen die zijn ingevoerd
        try:
            hoeveelheid_mensen = int(number_people)
            self.eind_lijst.append(hoeveelheid_mensen)
        except:
            self.error_label.config(text= 'Vul een passend getal in!')
            self.user_geen_groep()
            return 
        
        self.hoeveelheid_mensen = hoeveelheid_mensen
        # Zorg dat er voor elk persoon een naam is in de txt file
        self.tellen_entry.delete(0, END)
        self.tellen_geen_button.config(text= "submit naam", command= self.naam_toevoegen)
        self.veranderend_label.config(text= f'Wat is de naam van persoon nummer {len(self.naam_lijst)+1}? ')        



    def naam_toevoegen(self):
        if len(self.naam_lijst) < self.hoeveelheid_mensen-1:
            naam = self.tellen_entry.get()
            self.naam_lijst.append(naam)
            self.tellen_entry.delete(0,END)
            self.veranderend_label.config(text= f'Wat is de naam van persoon nummer {len(self.naam_lijst)+1}? ')
            return
        elif len(self.naam_lijst) == self.hoeveelheid_mensen-1:
            naam = self.tellen_entry.get()
            self.naam_lijst.append(naam)
            self.error_label.config(text= "Alle namen zijn ingevoerd")
            self.veranderend_label.config(text= "Hoeveel was de uitgave? \n(Vul q of quit in om te stoppen!)")
            self.tellen_entry.delete(0, END)
            self.tellen_geen_button.config(text= "submit bedrag", command= self.bedragen_toevoegen)

    def bedragen_toevoegen(self):
        # Met een while loop kunnen we er altijd nieuwe bedragen toegevoegen tot de user aangeeft er klaar mee te zijn
        self.veranderend_label.config(text= 'Hoeveel was de uitgave? \n(Vul q of quit in om te stoppen!) ')
        bedrag_en_naam = self.tellen_entry.get()

        if self.nee:
            # Bij invoor van een variatie op quit of q wordt de while loop onderbroken en stopt de user met bedragen invullen
            if bedrag_en_naam.upper() == 'QUIT' or bedrag_en_naam.upper() == 'Q' and len(self.inner_list) %2 == 0:
                self.veranderend_label.config(text= "Alle info is ingevoerd")
                self.tellen_entry.delete(0,END)
                self.tellen_entry.config(state= DISABLED)
                self.tellen_geen_button.config(state= DISABLED)
                self.tekst_werken()
                return
            
            try:
                self.inner_list.append(float(bedrag_en_naam))
            except:
                self.error_label.config(text= "Sorry dit was geen bedrag")
                return
            self.tellen_entry.delete(0, END)
            self.veranderend_label.config(text= 'Wie heeft het betaald?')
            self.tellen_geen_button.config(text= "submit persoon", command= self.personen_toevoegen)
        elif self.ja:
            self.eind_label.config(text= "")
            self.error_label.config(text= "")
            
            # Bij invoor van een variatie op quit of q wordt de while loop onderbroken en stopt de user met bedragen invullen
            if bedrag_en_naam.upper() == 'QUIT' or bedrag_en_naam.upper() == 'Q' and len(self.inner_list) %2 == 0:
                self.veranderend_label.config(text= "Alle info is ingevoerd")
                self.tellen_entry.delete(0,END)
                self.tellen_entry.config(state= DISABLED)
                self.tellen_wel_button.config(state= DISABLED)
                self.tekst_werken()
                return
            try:
                self.result[1].append(float(bedrag_en_naam))            
            except:
                self.error_label.config(text= "Sorry dit was geen bedrag")
                return
            self.tellen_entry.delete(0, END)
            self.veranderend_label.config(text= 'Wie heeft het betaald?')
            self.tellen_wel_button.config(text= "submit persoon", command= self.personen_toevoegen)



    def personen_toevoegen(self):
        if self.nee:
            # De user moet invullen wie er betaald heeft. Als deze naam niet voorkomt in de eerder gegeven stof wordt deze ingave niet genoteerd
            persoon = self.tellen_entry.get()
            if persoon in self.naam_lijst:   
                self.inner_list.append(self.naam_lijst.index(persoon) + 1)
            else:
                self.error_label.config(text="Die naam herkennen we niet!")
            
            self.tellen_entry.delete(0, END)
            self.veranderend_label.config(text= "Hoeveel was de uitgave? \n(Vul q of quit in om te stoppen!)")
            self.tellen_geen_button.config(text= "submit bedrag", command= self.bedragen_toevoegen)
        elif self.ja:
            # De user moet invullen wie er betaald heeft. Als deze naam niet voorkomt in de eerder gegeven stof wordt deze ingave niet genoteerd
            persoon = self.tellen_entry.get()
            if persoon in self.naam_lijst:   
                self.result[1].append(self.naam_lijst.index(persoon) + 1)
            else:
                self.error_label.config(text="Die naam herkennen we niet!")
            
            self.tellen_entry.delete(0, END)
            self.veranderend_label.config(text= "Hoeveel was de uitgave? \n(Vul q of quit in om te stoppen!)")
            self.tellen_wel_button.config(text= "submit bedrag", command= self.bedragen_toevoegen)



    def tekst_werken(self):


        if self.ja:
            # Laat de eerder gedefinieerde functie de bedragen vinden
            balans_lijst = self.individual_balance(self.result[0],self.result[1])
            # Elke iteration van kosten lijst is een getal die checkt hoeveel er betaalt moet worden
            eindprint = ''
            for i in range(len(balans_lijst)):
                if balans_lijst[i] >= 0:
                    eindprint += f'{self.naam_lijst[i]} moet {balans_lijst[i]} uitbetaald krijgen\n'
                else:
                    eindprint += f'{self.naam_lijst[i]} moet {-1 * balans_lijst[i]} betalen\n'
            self.eind_label.config(text=eindprint)
            self.error_label.config(text= "")
            # We kunne hier niet de info appenden omdat het al bekende info is dus moet er overheen geschreven worden
                # Voor extra efficientie is dit beter gedaan met een database
            with open("Applications/WBW.txt", 'w') as file:
                for i in range(len(self.groepnamen)):
                    file.write(f"\n{self.groepnamen[i]}: {self.wachtwoorden[i]}: {self.kasstaat[i]}: {self.namen_lijst[i]}")
        elif self.nee:
            # Zorg voor een duidelijke lijst die toegevoegt wordt aan het tekstbestand
            self.eind_lijst.append(self.inner_list)
            # Laat de eerder gedefinieerde functie de bedragen vinden
            kosten_lijst = self.individual_balance(self.eind_lijst[0],self.eind_lijst[1])
            # Elke iteration van kosten lijst is een getal die checkt hoeveel er betaalt moet worden
            eindprint = ''
            for i in range(len(kosten_lijst)):
                if kosten_lijst[i] >= 0:
                    eindprint += f'{self.naam_lijst[i]} moet {kosten_lijst[i]} uitbetaald krijgen\n'
                else:
                    eindprint += f'{self.naam_lijst[i]} moet {-1 * kosten_lijst[i]} betalen\n'
            self.eind_label.config(text=eindprint)
            self.error_label.config(text= "")
            # Omdat dit niet een bestaande groep is kan dit toegevoegd worden met de append functie
            with open('Applications/WBW.txt', 'a') as file:
                file.write(f'\n{self.groepnaam}: {self.wachtwoord}: {self.eind_lijst}: {self.naam_lijst}')
        else:
            print("Het kan niet")


    def user_wel_groep(self):
        self.ja_radio.config(state = DISABLED)
        self.nee_radio.config(state = DISABLED)
        self.ja = True
        self.wbw_gui.destroy()

        wbw_wel_gui = Tk()
        self.wbw_wel_gui = wbw_wel_gui
        self.wbw_wel_gui.config(bg='#4c5563')
        self.wbw_wel_gui.title("Wie Betaalt Wat")
        self.wbw_wel_gui.geometry("750x550")
        # Top Tekst
        # wel variabel nodig omdat ze niet veranderd gaan worden
        Label(wbw_wel_gui, text= "Wie Betaalt Wat", fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column= 3,pady= 15, sticky= "nsew")
        Label(wbw_wel_gui, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")
        
        
        Label(wbw_wel_gui, text= "Wat is de naam van je groep:",fg= '#c5d2ed', bg= '#4c5563').grid(row=2, column= 1)
        self.groepnaam_entry = Entry(wbw_wel_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.groepnaam_entry.config(disabledbackground= "#373d47")
        self.groepnaam_entry.grid(row=2,column= 2,sticky= "nsew")

        Label(wbw_wel_gui, text= "Wat is het wachtwoord van je groep:",fg= '#c5d2ed', bg= '#4c5563').grid(row=3, column= 1)
        self.wachtwoord_entry = Entry(wbw_wel_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.wachtwoord_entry.config(disabledbackground= "#373d47", state= NORMAL)
        self.wachtwoord_entry.grid(row=3,column= 2,sticky= "nsew")
        
        self.wachtwoord_wel_button = Button(wbw_wel_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Submit wachtwoord",state= NORMAL, command= self.account_check)
        self.wachtwoord_wel_button.grid(row= 3, column= 5, sticky= "nswe")


        self.error_label = Label(wbw_wel_gui, text= "",fg= '#c5d2ed', bg= '#4c5563')
        self.error_label.grid(row=9, column= 3)

        self.veranderend_label = Label(wbw_wel_gui, text= "Hoeveel was de uitgave?\n(Vul q of quit in om te stoppen!):",fg= '#c5d2ed', bg= '#4c5563')
        self.veranderend_label.grid(row=4, column= 1)
        self.tellen_entry = Entry(wbw_wel_gui, fg= '#c5d2ed', bg= '#4c5563')
        self.tellen_entry.config(disabledbackground= "#373d47", state= DISABLED)
        self.tellen_entry.grid(row=4,column= 2,sticky= "nsew")
        
        self.tellen_wel_button = Button(wbw_wel_gui, fg= '#c5d2ed', bg= '#4c5563', text= "Submit hoeveelheid",state= DISABLED, command= self.bedragen_toevoegen)
        self.tellen_wel_button.grid(row= 4, column= 5, sticky= "nswe")

        self.eind_label = Label(wbw_wel_gui, text= "",fg= '#c5d2ed', bg= '#4c5563')
        self.eind_label.grid(row=10, column= 3, sticky= "nsew")

        wbw_wel_gui.mainloop()


    def account_check(self):
        # self.ja_radio.config(state = DISABLED)
        # self.nee_radio.config(state = DISABLED)
        # Begin met twee inputs die de identificatie regelen van de groep
        group_number = self.groepnaam_entry.get()
        ww = self.wachtwoord_entry.get()
        # Open de file en lees deze uit en maak schoon
        with open('Applications/WBW.txt', 'r') as file:
            regels = file.read()
            regel = regels.split('\n')
        while '' in regel:
            regel.remove('')
        # Initieer de lijsten die gevuld gaan worden met de info uit de 
        self.groepnamen = []
        self.wachtwoorden = []
        self.kasstaat = []
        self.namen_lijst = []
        # Vul de lijst met alle info uit de file
        for i in regel:
            self.groepnamen.append(i.split(': ')[0])
            self.wachtwoorden.append(i.split(': ')[1])
            self.kasstaat.append(i.split(': ')[2])
            self.namen_lijst.append(i.split(': ')[3])
        # Check of de groep naam al bekend is of niet
        try:
            belangrijk_nummer = self.groepnamen.index(group_number)
        except: 
            self.error_label.config(text= "Deze naam is onbekend in ons systeem")
            return
            
        # Haal alle info uit de strings. Dit moet gebeuren omdat ik een txt file gebruik 
        naam_unfiltered_lijst = self.namen_lijst[belangrijk_nummer].replace('[','').replace(' ','').replace(']','').replace("'","")
        self.naam_lijst = naam_unfiltered_lijst.split(',')
        temp = self.kasstaat[belangrijk_nummer].replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
        temp_parts = temp.split(',')
        outer_value = int(temp_parts[0])
        inner_list = [int(x) if x.isdigit() else x for x in temp_parts[1:]]
        self.result = [outer_value, inner_list]
        self.kasstaat[belangrijk_nummer] = self.result
        # Yipeee het is schoon
        # De user komt de file niet in zonder het wachtwoord goed te hebben
        if ww != self.wachtwoorden[belangrijk_nummer]:
            self.error_label.config(text= 'Dit wachtwoord is helaas niet juist! Probeer het opnieuw')
            return 
        # De naam is correct en het wachtwoord ook dus kunnen we naar 
        self.error_label.config(text= f'We hebben hem gevonden dit is de huidige staat:\n')
        balans_lijst = self.individual_balance(self.result[0],self.result[1])
        # Zeker weten dat iterator start op 0 en dat hij elke persoon laat weten hoeveel hij/zij krijgt of moet betalen
        i = 0
        variabele_tekst = ""
        while i in range(len(balans_lijst)):
            if balans_lijst[i] > 0:
                variabele_tekst += f"{self.naam_lijst[i]} krijgt {balans_lijst[i]}\n"
            elif balans_lijst[i] < 0:
                variabele_tekst += f"{self.naam_lijst[i]} moet {-1 * balans_lijst[i]} betalen\n"
            elif balans_lijst[i] == 0:
                variabele_tekst += f"{self.naam_lijst[i]} hoeft niks te betalen\n"
            i += 1
        self.eind_label.config(text= variabele_tekst)
        self.groepnaam_entry.config(state= DISABLED)
        self.wachtwoord_entry.config(state= DISABLED)
        self.wachtwoord_wel_button.config(state= DISABLED)
        self.tellen_entry.config(state= NORMAL)
        self.tellen_wel_button.config(state= NORMAL)

if __name__ == "__main__":
    potje = splitser()