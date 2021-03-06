from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from polje import *
import racunalnik
import random
import threading

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

        self.odprta_polja = []  # vsa trenutno odprta polja
        self.zaprta_polja = [(i, j) for i in range(self.velikost) for j in range(self.velikost)]  # vsa trenutno zaprta
        # polja
        self.zastave = []  # vsa polja, ki so trenutno oznacena z zastavico

        # --- INTELIGENCA ---
        self.vlakno = None
        self.inteligenca = None
        self.p = None  # poteza
        self.pomoc = True  # ali igralec zeli pomoc racunalnika ali ne
        self.zakasnitev = 30  # zakasnitev risanja potez racunalnika

        # --- GUI ---
        self.master = master  # da ga lahko kasneje unicimo
        self.ozadje = '#BABABA'  # barva ozadja polj
        zastava = Image.open('flag_small.png')
        self.zastava = ImageTk.PhotoImage(zastava)  # nalozimo sliko zastave
        bomba = Image.open('bomb_small.png')
        self.bomba = ImageTk.PhotoImage(bomba)  # nalozimo sliko mine
        self.nastavitve = None  # okno z nastavitvami
        self.maxvelikost = 30  # maksimalna velikost, ki jo bo uporabnik lahko izbral pri nastavitvah
        self.izbrana_velikost = None  # velikost, ki jo je uporabnik izbral
        self.izbrane_mine = None  # stevilo min, ki jih bo uporabnik izbral
        self.izbran_igralec = None  # ali bo uporabnik izbral resevanje s pomocjo racunalnika

        master.title('Minolovec')

        okvir = Frame(master)
        okvir.grid()

        menu = Menu(master)
        master.config(menu=menu)
        podmenu = Menu(menu)
        podmenu.add_command(label='Nova igra    [F1]', command=self.nova_igra)
        podmenu.add_command(label='Nastavitve   [F2]', command=self.okno_z_nastavitvami)
        podmenu.add_separator()
        podmenu.add_command(label='Izhod           [Esc]', command=self.izhod)
        menu.add_cascade(label='File', menu=podmenu)

        Label(okvir, text='Zmage: ').grid(row=0, column=0)
        Label(okvir, textvariable=self.zmage).grid(row=0, column=1, sticky='W')
        Label(okvir, text='Porazi: ').grid(row=1, column=0)
        Label(okvir, textvariable=self.porazi).grid(row=1, column=1, sticky='W')
        Label(okvir, text='Preostale mine: ').grid(row=2, column=0, sticky='S')
        Label(okvir, textvariable=self.preostale_mine).grid(row=2, column=1, sticky='WS')

        self.poteza_racunalnika = Button(okvir, text='Namig', command=self.prepusti_racunalniku)
        self.poteza_racunalnika.grid(row=0, column=2, rowspan=3)

        self.platno = Canvas(okvir, width=self.velikost*self.kvadratek, height=self.velikost*self.kvadratek,
                             background='#FFFFFF', bd=1, highlightthickness=1, highlightbackground='#000000')
        self.platno.grid(row=3, column=0, columnspan=3)
        self.narisi_mrezo()
        self.platno.bind("<Button-1>", self.klik)
        self.platno.bind("<Button-3>", self.klik)
        master.bind("<F1>", self.nova_igra)
        master.bind("<F2>", self.okno_z_nastavitvami)
        master.bind("<Escape>", self.izhod)

        self.okno_z_nastavitvami()

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

    def nova_igra(self, *args):
        """ Resetira vse spremenljivke in pripravi novo igro. """
        if self.vlakno is not None:
            self.vlakno.join()

        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.napolni()
        self.preostale_mine.set(self.mine)
        self.platno.delete(ALL)
        self.platno.config(width=self.velikost*self.kvadratek, height=self.velikost*self.kvadratek)
        self.narisi_mrezo()
        self.gameactive = True

        self.zaprta_polja = [(i, j) for i in range(self.velikost) for j in range(self.velikost)]
        self.odprta_polja = []
        self.zastave = []

        # self.prikazi_celotno_polje(True)  # prikazovanje celotnega polja za debugiranje

        if self.pomoc:
            self.platno.after(self.zakasnitev, self.prepusti_racunalniku)

    # ***********************
    # NASTAVITEV IGRE
    # ***********************

    def ponastavi(self, *args):
        """ Ponastavi parametre igre glede na podatke, vnešene v okno z nastavitvami. Klice se ob kliku na gumb 'V
        redu' ali ob pritisku na <Enter> znotraj okna z nastavitvami. """
        try:
            m = int(self.izbrane_mine.get())
            v = int(self.izbrana_velikost.get())
            if m > v ** 2:
                messagebox.showerror('Nepravilno število min', 'Vnešeno število min je večje od površine polja!')
                self.nastavitve.focus()
                self.izbrana_velikost.focus()
            elif v > self.maxvelikost:
                messagebox.showerror('Prevelika velikost polja', 'Prosim, vnesite velikost med 1 in {0}!'.format(
                    self.maxvelikost))
                self.nastavitve.focus()
                self.izbrana_velikost.focus()
            else:
                self.velikost = v
                self.mine = m
                self.pomoc = True if self.izbran_igralec.get() else False
                if self.pomoc: self.poteza_racunalnika.grid_remove()
                else: self.poteza_racunalnika.grid()
                self.nastavitve.destroy()
                self.gameactive = True
                self.nova_igra()
        except ValueError:
            messagebox.showerror('Nepravilna vrednost', 'Vnesli ste nepravilno vrednost!')
            self.nastavitve.focus()
            self.izbrana_velikost.focus()

    def posodobi_max_stevilo_min(self):
        """ Glede na vneseno velikost polja posodobi zgornjo mejo za stevilo min v oknu za nastavitve. """
        velikost = int(self.izbrana_velikost.get())
        self.izbrane_mine.config(to=velikost**2)

    def okno_z_nastavitvami(self, *args):
        """ Odpre okno z nastavitvami. """
        self.nastavitve = Toplevel()
        self.nastavitve.title('Nastavitve')
        self.nastavitve.transient(self.master)  # poskrbi, da je okno z nastavitvami vedno nad glavnim oknom
        self.nastavitve.focus()

        self.gameactive = False

        trenutna_velikost = StringVar()
        trenutna_velikost.set(self.velikost)
        Label(self.nastavitve, text='Velikost polja: ').grid(row=0, column=0, sticky='W')
        self.izbrana_velikost = Spinbox(self.nastavitve, from_=2, to=self.maxvelikost,
                                        textvariable=trenutna_velikost, command=self.posodobi_max_stevilo_min)
        self.izbrana_velikost.grid(row=0, column=1)
        self.izbrana_velikost.focus()

        trenutne_mine = StringVar()
        trenutne_mine.set(self.mine)
        Label(self.nastavitve, text='Število min: ').grid(row=1, column=0, sticky='W')
        self.izbrane_mine = Spinbox(self.nastavitve, from_=1, to=int(self.izbrana_velikost.get())**2,
                                    textvariable=trenutne_mine)
        self.izbrane_mine.grid(row=1, column=1)

        self.izbran_igralec = IntVar()
        self.izbran_igralec.set(1 if self.pomoc else 0)
        Checkbutton(self.nastavitve, text='Igro naj rešuje računalnik', var=self.izbran_igralec).grid(row=2, column=0,
                                                                                                      columnspan=2)

        Button(self.nastavitve, text='V redu', command=self.ponastavi).grid(row=3, column=1)

        self.nastavitve.bind("<Return>", self.ponastavi)

    def izhod(self, *args):
        """ Poskrbi za unicenje threada in glavnega okna ob izhodu iz igre. """
        if self.vlakno is not None:
            self.vlakno.join()
        self.master.destroy()

    # ***********************
    # MEHANIZEM IGRE
    # ***********************

    def poteza(self, p):
        """ Sprejme potezo p in jo izvede. """
        (x, y, m) = p
        if self.gameactive:
            if m:  # če je m True, je uporabnik kliknil z desno tipko, torej oznacimo polje z zastavo
                ozn = self.polje[x][y].oznaci()
                if ozn:  # polje smo uspesno oznacili
                    self.narisi_mino(x, y)
                    mine = self.preostale_mine.get()
                    if (x, y) in self.zastave:
                        self.zastave.remove((x, y))
                        self.zaprta_polja.append((x, y))
                        self.preostale_mine.set(mine + 1)
                    else:
                        self.zaprta_polja.remove((x, y))
                        self.zastave.append((x, y))
                        self.preostale_mine.set(mine - 1)
                    self.preveri()
            else:  # sicer polje odpremo
                if not self.polje[x][y].flagged:
                    self.odpri_blok((x, y))
                    self.preveri()

            if self.gameactive and self.pomoc:
                self.platno.after(self.zakasnitev, self.prepusti_racunalniku)  # ce igro resuje racunalnik,
                # potem ponovno poklicemo metodo, ki od racunalnika pridobi novo potezo

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
                if self.polje[x][y].prikaz == 'x':
                    self.preveri(mina=True)
                    break
                self.zaprta_polja.remove((x, y))
                self.odprta_polja.append((x, y))
            checked.append((x, y))
            if self.polje[x][y].vrednost == 0:
                for i in range(max(0, x - 1), min(x + 2, self.velikost)):
                    for j in range(max(0, y - 1), min(y + 2, self.velikost)):
                        if not self.polje[i][j].odprto and not (i, j) in checked:
                            odpri.append((i, j))

    def polno(self):
        """ Preveri, ali je igralno polje zapolnjeno. """
        if self.zaprta_polja:
            return False
        return True

    def preveri(self, mina=False):
        """ Preveri, ali je igre konec. Neobvezen parameter mina pove, ali je bila metoda poklicana, ker je igralec
        stopil na mino. """
        polno = self.polno()
        if mina:
            self.gameactive = False
            self.porazi.set(self.porazi.get() + 1)
        elif polno and self.preostale_mine.get() == 0:  # polje je pravilno izpolnjeno
            self.gameactive = False
            self.zmage.set(self.zmage.get() + 1)

    # ***********************
    # INPUT
    # ***********************

    def klik(self, klik):
        """ Metoda, ki je bindana na levi in desni klik miske. Ce igra poteka, naredi potezo glede na to, ali je
        uporabnik kliknil levo ali desno tipko. """
        if self.gameactive and not self.pomoc:  # uporabnik lahko klikne, ce igra poteka in ce je ne resuje racunalnik
            y = klik.x // self.kvadratek
            x = klik.y // self.kvadratek
            if x < self.velikost and y < self.velikost:  # uporabnik je kliknil znotraj polja
                flag = True if klik.num == 3 else False  # ali je uporabnik kliknil z desno ali levo tipko miske
                self.poteza((x, y, flag))

    # ***********************
    # RISANJE
    # ***********************

    def narisi_mrezo(self):
        """ Narise mrezo na Canvasu. """
        for i in range(1, self.velikost):
            self.platno.create_line(i * self.kvadratek, 0, i * self.kvadratek, self.velikost * self.kvadratek)
            self.platno.create_line(0, i * self.kvadratek, self.velikost * self.kvadratek, i * self.kvadratek)

    def narisi_polje(self, x, y):
        """ Narise kvadratek s stevilko. """
        kvad = self.izracunaj_kvadratek(x, y)
        self.platno.create_rectangle(*kvad, fill=self.ozadje)
        stevilka = self.polje[x][y].vrednost
        sredina = self.izracunaj_sredino_kvadratka(x, y)
        if stevilka == 'x':
            self.platno.create_rectangle(*kvad, fill='#FF0000')
            self.platno.create_image(sredina, image=self.bomba)
        elif stevilka != 0:
            barva = BARVE[stevilka]
            self.platno.create_text(sredina, text=stevilka, font=('Arial', 14, 'bold'), fill=barva)

    def narisi_mino(self, x, y):
        """ Ali narise ali zbrise zastavico na polje. """
        flag = self.polje[x][y].flagged  # polje smo ze oznacili/odznacili, treba ga je samo se narisat
        sredina = self.izracunaj_sredino_kvadratka(x, y)
        if flag:
            kvad = self.izracunaj_kvadratek(x, y)
            self.platno.create_rectangle(*kvad, fill='#FF9696', width=1, outline='#000000')
            self.platno.create_image(sredina, image=self.zastava)
        else:
            tag = self.najdi_id(x, y)
            for t in tag:
                self.platno.delete(t)
            self.platno.delete(self.platno.find_closest(*sredina))

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

    def naredi_matriko(self):
        """ Naredi matriko, ki prikazuje trenutno stanje na polju. """
        matrika = [['' for _ in range(self.velikost)] for _ in range(self.velikost)]
        for r in self.polje:
            for k in r:
                matrika[k.x][k.y] = k.prikaz
        return matrika

    # ***********************
    # INTELIGENCA
    # ***********************

    def prepusti_racunalniku(self):
        """ Pozene vzporedni thread, kjer racunalnik racuna potezo. """
        if self.gameactive:
            self.p = None
            if self.inteligenca is None:
                self.inteligenca = racunalnik.Racunalnik()
            self.vlakno = threading.Thread(target=self.razmisljaj)
            self.vlakno.start()
            self.platno.after(self.zakasnitev, self.konec_razmisljanja)

    def razmisljaj(self):
        """ Racunalnik izracuna naslednjo potezo, ki se spravi v atribut p. """
        m = self.naredi_matriko()
        p = self.inteligenca.vrni_potezo(m, int(self.preostale_mine.get()))
        self.p = p
        self.vlakno = None

    def konec_razmisljanja(self):
        """ Preveri, ali je racunalnik ze izracunal potezo. """
        if self.p is None:  # racunalnik se ni izracunal poteze
            self.platno.after(self.zakasnitev, self.konec_razmisljanja)
        else:  # racunalnik je ze izracunal potezo
            self.poteza(self.p)  # naredimo potezo
            self.p = None

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
igrica = Minesweeper(root, 10, 20)
root.mainloop()