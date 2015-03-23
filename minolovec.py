from tkinter import *
from polje import *
import racunalnik
import random

# array barv za stevilke na polju
BARVE = {1: '#8B00FF',
         2: '#4B0082',
         3: '#0000FF',
         4: '#20A106',
         5: '#F2CB1D',
         6: '#FF7F00',
         7: '#FF0000',
         8: '#000000',
         9: '#000000'}


class Minesweeper():
    def __init__(self, master, velikost, mine):
        self.velikost = velikost  # velikost kvadratnega igralnega polja
        self.kvadratek = 30  # velikost enega kvadratka na igralnem polju
        self.mine = mine  # stevilo min
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.preostale_mine = IntVar(value=self.mine)
        self.zmage = IntVar(0)
        self.porazi = IntVar(0)
        self.gameactive = True  # ali igra poteka
        self.inteligenca = None

        # --- GUI ---
        self.ozadje = '#BABABA'  # barva ozadja polj
        self.zastava = PhotoImage(file='flag_small.png')  # nalozimo sliko zastave
        self.bomba = PhotoImage(file='bomb_small.png')  # nalozimo sliko mine

        master.title('Minolovec')

        okvir = Frame(master)
        okvir.grid()

        menu = Menu(master)
        master.config(menu=menu)
        podmenu = Menu(menu)
        podmenu.add_command(label='Nova igra', command=self.nova_igra)
        podmenu.add_command(label='Izhod', command=master.destroy)
        menu.add_cascade(label='File', menu=podmenu)

        Label(okvir, text='Zmage: ').grid(row=0, column=0)
        Label(okvir, textvariable=self.zmage).grid(row=0, column=1, sticky='W')
        Label(okvir, text='Porazi: ').grid(row=1, column=0)
        Label(okvir, textvariable=self.porazi).grid(row=1, column=1, sticky='W')
        Label(okvir, text='Preostale mine: ').grid(row=2, column=0, sticky='S')
        Label(okvir, textvariable=self.preostale_mine).grid(row=2, column=1, sticky='WS')

        self.platno = Canvas(okvir, width=self.velikost*self.kvadratek, height=self.velikost*self.kvadratek,
                             background='#FFFFFF')
        self.platno.grid(row=3, column=0, columnspan=2)
        self.narisi_mrezo()
        self.platno.bind("<Button-1>", self.klik)
        self.platno.bind("<Button-3>", self.klik)

        self.napolni()

        self.prepusti_racunalniku()

    # ***********************
    # PRIPRAVA IGRE
    # ***********************

    def spremeni_stevilko_polj(self, x, y):
        """ Spremeni stevilko polj okoli mine, ta je podana s koordinatami x in y. """
        for z in range(max(0, x-1), min(x+2, self.velikost)):
            for w in range(max(0, y-1), min(y+2, self.velikost)):
                if self.polje[z][w].vrednost != 'x':
                    self.polje[z][w].vrednost += 1

    def napolni(self):
        """ Nakljucno napolni igralno polje s 'self.mine' stevilom min. Mine so oznacene z x, prazni kvadratki z 0. """
        i = self.mine
        prazno = [(x, y) for x in range(self.velikost) for y in range(self.velikost)]
        while i > 0:
            (x, y) = random.choice(prazno)
            prazno.remove((x, y))
            self.polje[x][y].vrednost = 'x'
            self.spremeni_stevilko_polj(x, y)
            i -= 1

    def nova_igra(self):
        """ Resetira vse spremenljivke in pripravi novo igro. """
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.napolni()
        self.preostale_mine.set(self.mine)
        self.platno.delete(ALL)
        self.narisi_mrezo()
        self.gameactive = True

    # ***********************
    # MEHANIZEM IGRE
    # ***********************

    def poteza(self, x, y, m):
        if self.gameactive:
            if m:  # če je m True, je uporabnik kliknil z desno tipko, torej oznacimo polje z zastavo
                ozn = self.polje[x][y].oznaci()
                if ozn:
                    self.narisi_mino(x, y)
                    self.preveri()
            else:  # sicer polje odpremo
                if not self.polje[x][y].flagged:
                    print(self.vrni_sosednje_zastave(x, y))
                    print(self.vrni_sosednja_polja(x, y))
                    self.odpri_blok((x, y))
                    self.preveri()

    def odpri_blok(self, koord):
        """ Sprejme tuple koord s koordinatami, kamor je uporabnik levo-kliknil (kjer je prazno polje), in odpre vsa
        sosednja polja, ce je stevilo min v okolici polja 0. Postopek ponavlja za vsako polje, ki se odpre,
        dokler ne naleti na polje, ki ima v okolici kaksno mino. """
        checked = [koord]
        odpri = [koord]
        while odpri:
            x, y = odpri.pop()
            odpr = self.polje[x][y].odpri()
            if odpr:
                self.narisi_polje(x, y)
            checked.append((x, y))
            if self.polje[x][y].vrednost == 0:
                for i in range(max(0, x - 1), min(x + 2, self.velikost)):
                    for j in range(max(0, y - 1), min(y + 2, self.velikost)):
                        if not self.polje[i][j].odprto and not (i, j) in checked:
                            odpri.append((i, j))

    def konec(self):
        """ Preveri, ali je igralno polje pravilno zapolnjeno z zastavami. """
        for x in self.polje:
            for y in x:
                if not (y.odprto or y.flagged):
                    return False
        return True

    def preveri(self, mina=False):
        """ Preveri, ali je igre konec. """
        konec = self.konec()
        if mina:
            self.gameactive = False
            self.porazi.set(self.porazi.get() + 1)
        elif konec and self.preostale_mine.get() == 0:
            self.gameactive = False
            self.zmage.set(self.zmage.get() + 1)

    # ***********************
    # INPUT
    # ***********************

    def klik(self, klik):
        """ Metoda, ki je bindana na levi in desni klik miske. Ce igra poteka, naredi potezo glede na to, ali je
        uporabnik kliknil levo ali desno tipko. """
        if self.gameactive:
            # print(vars(klik))
            y = klik.x // self.kvadratek
            x = klik.y // self.kvadratek
            if x < self.velikost and y < self.velikost:
                flag = True if klik.num == 3 else False  # ali je uporabnik kliknil z desno ali levo tipko miske
                self.poteza(x, y, flag)

    # ***********************
    # RISANJE
    # ***********************

    def narisi_mrezo(self):
        """ Narise mrezo na Canvasu. """
        for i in range(1, self.velikost):
            self.platno.create_line(i * self.kvadratek, 0, i * self.kvadratek, self.velikost * self.kvadratek)
            self.platno.create_line(0, i * self.kvadratek, self.velikost * self.kvadratek, i * self.kvadratek)

    def narisi_polje(self, x, y):
        """ Narise polje s stevilko. """
        kvad = self.izracunaj_kvadratek(x, y)
        self.platno.create_rectangle(*kvad, fill=self.ozadje)
        stevilka = self.polje[x][y].vrednost
        sredina = self.izracunaj_sredino_kvadratka(x, y)
        if stevilka == 'x':
            self.platno.create_rectangle(*kvad, fill='#FF0000')
            self.platno.create_image(sredina, image=self.bomba)
            self.preveri(mina=True)
        elif stevilka != 0:
            barva = BARVE[stevilka]
            self.platno.create_text(sredina, text=stevilka, font=('Arial', 14, 'bold'), fill=barva)

    def narisi_mino(self, x, y):
        """ Ali narise ali zbrise zastavico na polje. """
        flag = self.polje[x][y].flagged  # polje smo ze oznacili/odznacili, treba ga je samo se narisat
        mine = self.preostale_mine.get()
        sredina = self.izracunaj_sredino_kvadratka(x, y)
        if flag:
            kvad = self.izracunaj_kvadratek(x, y)
            self.platno.create_rectangle(*kvad, fill='#FF9696', width=1, outline='#000000')
            # self.platno.create_text(sredina, text='f', fill='#FFFFFF')
            self.platno.create_image(sredina, image=self.zastava)
            self.preostale_mine.set(mine - 1)
        else:
            tag = self.najdi_id(x, y)
            for t in tag:
                # print(t)
                self.platno.delete(t)
            self.platno.delete(self.platno.find_closest(*sredina))
            self.preostale_mine.set(mine + 1)

    # ------ POMOZNE FUNKCIJE ZA RISANJE ------
    def izracunaj_kvadratek(self, x, y):
        """ Izracuna tocki v levem zgornjem kotu in desnem spodnjem kotu kvadratka, ki se nahaja v vrstici x in
        stolpcu y. """
        return [y * self.kvadratek, x * self.kvadratek, (y + 1) * self.kvadratek,
                (x + 1) * self.kvadratek]

    def izracunaj_sredino_kvadratka(self, x, y):
        """ Izracuna koordinate tocke na sredini kvadratka. """
        return y * self.kvadratek + (self.kvadratek // 2), x * self.kvadratek + (self.kvadratek // 2)

    def najdi_id(self, x, y):
        """ Najde id vseh elementov na Canvasu znotraj kvadratka na koordinati x, y. """
        kvad = self.izracunaj_kvadratek(x, y)
        return self.platno.find_enclosed(*kvad)

    # ***********************
    # SPREMLJANJE IGRE
    # ***********************

    def vrni_sosednje_zastave(self, x, y):
        """ Vrne stevilo trenutnih zastav v okolici polja, podana z x in y. """
        zastave = 0
        for z in range(max(0, x - 1), min(x + 2, self.velikost)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost)):
                if z != x or w != y:
                    if self.polje[z][w].flagged:
                        zastave += 1
        return zastave

    def vrni_sosednja_polja(self, x, y):
        """ Vrne koordinate sosednjih polj polja, podanega z x in y. """
        sosedi = []
        for z in range(max(0, x - 1), min(x + 2, self.velikost)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost)):
                if z != x or w != y:
                    sosedi.append((z, w))
        return sosedi

    def vrni_stanje(self):
        """ Vrne stanje celotnega igralnega polja - kateri kvadratki so odkriti in kateri oznaceni. """
        return None

    # ***********************
    # INTELIGENCA
    # ***********************

    def prepusti_racunalniku(self):
        self.inteligenca = racunalnik.Racunalnik(self)
        self.inteligenca.zgradi_stanje_polja()
        print(self.inteligenca.stanje_polja)
        self.inteligenca.naredi_potezo()
        print(self.inteligenca.stanje_polja)
        self.inteligenca.naredi_potezo()
        print(self.inteligenca.stanje_polja)
        self.inteligenca.naredi_potezo()
        print(self.inteligenca.stanje_polja)
        self.inteligenca.naredi_potezo()
        print(self.inteligenca.stanje_polja)
        # while self.gameactive:
        #     self.inteligenca.naredi_potezo()
        #     print(self.inteligenca.stanje_polja)

    # ***********************
    # POMOZNE FUNKCIJE
    # ***********************

    def prikazi_celotno_polje(self, odkrito=False):
        """ Prikaze celotno polje min in praznih kvadratkov. """
        niz = ''
        for x in self.polje:
            niz += '|'
            for y in x:
                n = y.vrednost if odkrito else str(y)
                niz += ' {0} |'.format(n)
            niz += '\n'
        print(niz)


root = Tk()
igrica = Minesweeper(root, 10, 10)
igrica.prikazi_celotno_polje(True)
root.mainloop()