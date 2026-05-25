from tkinter import *
import random

class eenentwintigen:
    def __init__(self):
        # Een stock kaarten maken. Kleur van kaart maakt niet uit omdat de waarde in blackjack er niet mee veranderd
        self.stock = [1,2,3,4,5,6,7,8,9,10,11,12,13] * 4
        # Dit is gebruikt om twee functies naar dezelfde functie te sturen (hit functie)
        self.user = True
        # Tk window is de volgende 51 lines
        root = Tk()
        root.title("Fiber XL")

        root.geometry("400x400")
        root.config(bg='#4c5563')

        Label(root, text='Welcome to the casino\nLets play some blackjack', fg= '#c5d2ed', bg= '#4c5563').grid(row=0, column=3, pady=10, sticky="nsew")
        Label(root, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=1,column= 1,columnspan= 300, sticky= "nsew")

        button_play = Button(root, text='Begin het spel', fg= '#c5d2ed', bg= '#4c5563', command = self.game)
        button_play.grid(row=2, column=3, pady=10, padx = 10, ipadx= 20, sticky="ns")
        self.button_play = button_play
        
        Label(root,text="Player hand:", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=3,column= 3, sticky= "nsew")
        player_hand_label = Label(root,text="", fg= '#c5d2ed', bg= '#4c5563' )
        player_hand_label.grid(row=3,column= 4, sticky= "nsew")
        self.player_hand_label = player_hand_label

        Label(root,text="Dealer hand:", fg= '#c5d2ed', bg= '#4c5563').grid(row=5,column= 3, sticky= "nsew")
        dealer_hand_label = Label(root,text="", fg= '#c5d2ed', bg= '#4c5563')
        dealer_hand_label.grid(row=5,column= 4, sticky= "nsew")
        self.dealer_hand_label = dealer_hand_label

        label_player_resultaat = Label(root,text="", fg= '#c5d2ed', bg= '#4c5563' )
        label_player_resultaat.grid(row=4,column= 3, sticky= "nsew")
        self.label_player_resultaat = label_player_resultaat

        label_dealer_resultaat = Label(root,text="", fg= '#c5d2ed', bg= '#4c5563' )
        label_dealer_resultaat.grid(row=6,column= 3, sticky= "nsew")
        self.label_dealer_resultaat = label_dealer_resultaat

        button_stand = Button(root, text='Stand', fg= '#c5d2ed', bg= '#4c5563', command= self.stand, state= DISABLED)
        button_stand.grid(row=4, column=4, pady=10, padx = 10, ipadx= 20, sticky="ns")
        self.button_stand = button_stand

        button_hit = Button(root, text="Hit", fg= '#c5d2ed', bg= '#4c5563', command= self.hit, state= DISABLED)
        button_hit.grid(row=4, column=2, pady=10, padx = 10, ipadx= 20, sticky="ns")
        self.button_hit = button_hit

        label_algemeen_resultaat = Label(root, text="", fg= '#c5d2ed', bg= '#4c5563')
        label_algemeen_resultaat.grid(row=7, column=3, pady=10, padx = 10, ipadx= 20, sticky="ns")
        self.label_algemeen_resultaat = label_algemeen_resultaat

        button_opnieuw = Button(root, text="Opnieuw", fg= '#c5d2ed', bg= '#4c5563', command= self.opnieuw, state= DISABLED)
        button_opnieuw.grid(row=8, column=3, pady=10, padx = 10, ipadx= 20, sticky="ns")
        self.button_opnieuw = button_opnieuw

        Label(root, text= 150 * "-", fg= '#c5d2ed', bg= '#4c5563' ).grid(row=9,columnspan= 300, sticky= "nsew")
        button_stop = Button(root, text="Stop de applicatie", fg= '#c5d2ed', bg= '#4c5563',command= root.destroy)
        button_stop.grid(row=10, column=3, pady=10, ipadx= 20, sticky="ns")

        root.mainloop()


    def deal(self):
        hand = []
        for i in range(2):
            random.shuffle(self.stock)
            card = self.stock.pop()
            # Verander de kaart naar een symbool als dat moet
            match card:
                case 1:card = "A"
                case 11: card ="J"
                case 12: card ="Q"
                case 13: card = "K"
            hand.append(card)
        return hand
    
    def totaal(self,hand):
        totaal = 0
        for i in hand:
            # gebruikt om te leren werken met matching case
            match i:
                # Or statement is aangeduid met |
                case "J" | "Q" | "K": totaal += 10
                case "A": 
                    if totaal == 11: totaal = 12
                    else: totaal += 11
                case _: totaal += i
        return totaal

    def game(self):
        self.button_play.config(state= DISABLED)
        self.button_hit.config(state= NORMAL)
        self.button_stand.config(state= NORMAL)
        
        # Geef de speler twee kaarten en laat deze zien ook het totaal voor de duidelijkheid
        player_hand = self.deal()
        self.player_hand_label.config(text= f"{str(player_hand[0])}, {str(player_hand[1])}")
        player_totaal = self.totaal(player_hand)
        self.label_player_resultaat.config(text= f"totaal: {player_totaal}")
        # Geef ook de dealer 2 kaarten en laat deze zien ook het totaal voor de duidelijkheid
        dealer_hand = self.deal()
        self.dealer_hand_label.config(text= f"{str(dealer_hand[0])}, {str(dealer_hand[1])}")
        dealer_totaal = self.totaal(dealer_hand)
        self.label_dealer_resultaat.config(text= f"totaal: {dealer_totaal}")
        # Maak ze nu voor de hele class duidelijk
        self.dealer_hand = dealer_hand
        self.player_hand = player_hand
        # check of 1 van de spelers blackjack heeft en geef een passend bericht
        player_blackjack = False
        if self.totaal(player_hand) == 21: 
            self.label_player_resultaat.config(text= "Player has blackjack")
            player_blackjack = True
        if self.totaal(dealer_hand)== 21:
            self.label_dealer_resultaat.config(text= "Dealer has blackjack!")
            if player_blackjack: self.label_algemeen_resultaat.config(text= "Result = Push")
            else: self.label_algemeen_resultaat(text = "Player loses! Dealer has blackjack")
            self.button_opnieuw.config(state=NORMAL)



    def stand(self):
        # Vanaf een stand is alleen de dealer nog aan de beurt dus zorg dat de dealer nu speelt
        self.user = False
        self.button_hit.config(state= DISABLED)
        self.button_stand.config(state=DISABLED)
        dealer_totaal = self.totaal(self.dealer_hand)
        while dealer_totaal < 17:
            card = self.stock.pop()
            match card:
                case 1: card = "A"
                case 11: card ="J"
                case 12: card ="Q"
                case 13: card = "K"
            self.dealer_hand.append(card)
            dealer_totaal = self.totaal(self.dealer_hand)
        dealer_totaal = self.totaal(self.dealer_hand)
        self.dealer_hand_label.config(text= self.dealer_hand)
        # De laatste zet van de user zal altijd een stand zijn en dus kan nu ook het resultaat berekend worden
        if dealer_totaal <= 21: 
            self.label_dealer_resultaat.config(text= f"Totaal: {dealer_totaal}")
            if self.totaal(self.player_hand) < dealer_totaal:
                self.label_algemeen_resultaat.config(text= "Dealer has more! Player loses")
            elif self.totaal(self.player_hand) > dealer_totaal:
                self.label_algemeen_resultaat.config(text= "Player has more! Dealer loses")
            else:
                self.label_algemeen_resultaat.config(text= "Equal footing! no one loses!")
        else:
            self.label_dealer_resultaat.config(text= f"Totaal: {dealer_totaal}, Dealer BUSTS")
            self.label_algemeen_resultaat.config(text= f"Player Wins!!!")
        self.button_opnieuw.config(state=NORMAL)
        
    
    def hit(self):
        # Kies een kaart uit het geshufflede deck en haal hem dan ook uit de lijst
        card = self.stock.pop()
        match card:
            case 1: card = "A"
            case 11: card ="J"
            case 12: card ="Q"
            case 13: card = "K"
        # Beide de dealer en de speler moeten kaarten kunnen pakken
        if self.user:
            self.player_hand.append(card)
            self.player_hand_label.config(text= self.player_hand)
            player_totaal = self.totaal(self.player_hand)
            
            if player_totaal <= 21: self.label_player_resultaat.config(text= f"Totaal: {player_totaal}")
            else:
                self.label_player_resultaat.config(text= f"Totaal: {player_totaal}, Players BUSTS")
                self.button_hit.config(state= DISABLED)
                self.button_stand.config(state=DISABLED)
                self.button_opnieuw.config(state=NORMAL)
                self.label_algemeen_resultaat.config(text= f"The Dealer Wins!")
        else:
            self.dealer_hand.append(card)
            self.dealer_hand_label.config(text= self.dealer_hand)
            dealer_totaal = self.totaal(self.dealer_hand)
            
            if dealer_totaal <= 21: self.label_player_resultaat.config(text= f"Totaal: {dealer_totaal}")
            else:
                self.label_dealer_resultaat.config(text= f"Totaal: {dealer_totaal}, Dealer BUSTS")
                self.button_opnieuw.config(state=NORMAL)
                self.button_hit.config(state= DISABLED)
                self.button_stand.config(state=DISABLED)

    def opnieuw(self):
        # Alle waarden weer naar hun originele status
        self.stock = self.stock = [1,2,3,4,5,6,7,8,9,10,11,12,13] * 4
        self.user = True
        self.button_play.config(state= NORMAL)
        self.label_dealer_resultaat.config(text= "")
        self.label_player_resultaat.config(text= "")
        self.label_algemeen_resultaat.config(text= "")
        self.dealer_hand_label.config(text= "")
        self.player_hand_label.config(text= "")
        

if __name__ == "__main__":
    potje = eenentwintigen()