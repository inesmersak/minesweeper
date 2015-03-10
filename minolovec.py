from tkinter import *
from classes import *
import random

BARVE = {7: '#8B00FF',
         6: '#4B0082',
         5: '#0000FF',
         4: '#20A106',
         3: '#F2CB1D',
         2: '#FF7F00',
         1: '#FF0000',
         8: '#000000',
         9: '#000000'}


class Minesweeper():
    def __init__(self, master, velikost, mine):
        self.velikost = velikost
        self.kvadratek = 30
        self.mine = mine
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.preostale_mine = IntVar(value=self.mine)
        self.zmage = IntVar(0)
        self.porazi = IntVar(0)
        self.gamestate = True
        self.ozadje = '#BABABA'
        self.zastava = PhotoImage(file='flag_icon_s.png')
        self.bomba = PhotoImage(file='bomb_s.png')

        # --- GUI ---
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

    def spremeni_stevilko_polj(self, x, y):
        """ Spremeni stevilko polj okoli mine, ta je podana s koordinatami x in y. """
        for z in range(max(0, x-1), min(x+2, self.velikost)):
            for w in range(max(0, y-1), min(y+2, self.velikost)):
                if self.polje[z][w].vrednost != 'x':
                    self.polje[z][w].vrednost += 1

    def napolni(self):
        """ Nakljucno napolni igralno polje s 'self.mine' stevilom min. Mine so oznacene z x, prazni kvadratki z 0. """
        i = self.mine
        while i > 0:
            x = random.randint(0, self.velikost-1)
            y = random.randint(0, self.velikost-1)
            while self.polje[x][y].vrednost == 'x':
                x = random.randint(0, self.velikost-1)
                y = random.randint(0, self.velikost-1)
            self.polje[x][y].vrednost = 'x'
            self.spremeni_stevilko_polj(x, y)
            i -= 1

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

    def klik(self, klik):
        if self.gamestate:
            # print(vars(klik))
            y = klik.x // self.kvadratek
            x = klik.y // self.kvadratek
            flag = True if klik.num == 3 else False  # ali je uporabnik kliknil z desno ali levo tipko miske
            self.poteza(x, y, flag)

    def poteza(self, x, y, m):
        if m:
            ozn = self.polje[x][y].oznaci()
            if ozn:
                self.narisi_mino(x, y)
                self.preveri()
        else:
            if not self.polje[x][y].flagged:
                # self.narisi_polje(x, y) tega verjetno ne rabim
                self.odpri_blok((x, y))
                self.preveri()

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

    def narisi_mrezo(self):
        """ Narise mrezo na Canvasu. """
        for i in range(1, self.velikost):
            self.platno.create_line(i * self.kvadratek, 0, i * self.kvadratek, self.velikost * self.kvadratek)
            self.platno.create_line(0, i * self.kvadratek, self.velikost * self.kvadratek, i * self.kvadratek)

    def narisi_polje(self, x, y):
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
            self.platno.create_text(sredina, text=stevilka, font=('Arial', 11, 'bold'), fill=barva)

    def narisi_mino(self, x, y):
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
                for i in range(max(0, x-1), min(x+2, self.velikost)):
                    for j in range(max(0, y-1), min(y+2, self.velikost)):
                        if not self.polje[i][j].odprto and not (i, j) in checked:
                            odpri.append((i, j))

    def konec(self):
        for x in self.polje:
            for y in x:
                if not (y.odprto or y.flagged):
                    return False
        return True

    def preveri(self, mina=False):
        konec = self.konec()
        if mina:
            self.gamestate = False
            self.porazi.set(self.porazi.get() + 1)
        elif konec and self.preostale_mine.get() == 0:
            self.gamestate = False
            self.zmage.set(self.zmage.get() + 1)
            # if self.preostale_mine.get() == 0:
            #     self.zmage.set(self.zmage.get() + 1)
            # else:
            #     for vrs in self.polje:
            #         for obj in vrs:
            #             if obj.flagged and obj.vrednost != 'x':
            #                 print(obj.x, obj.y, 'ni good')
            #     self.porazi.set(self.porazi.get() + 1)

    def nova_igra(self):
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.napolni()
        self.preostale_mine.set(self.mine)
        self.platno.delete(ALL)
        self.narisi_mrezo()
        self.gamestate = True

root = Tk()
igrica = Minesweeper(root, 10, 10)
igrica.prikazi_celotno_polje(True)
root.mainloop()

# Jure reports a bug: Zakaj zgubim, ce vse flaggam?
# Jure lost :( Predzadnjo se se da cancellat, potem pa ne vec.

# Jure reports a second bug: veliko jih flaggam, kliknem na 0, se odpre vse povezano, flaggi pa ne.
# (to je prav, seveda). Potem ko unflaggam polje, na katerem je bil flag, se ne pokaze nic, je prazno.
# Nevermind... I am a moron. Jure is stupid, se neokrita polja morajo biti res drugacna :)

# Jure reports a real second bug. It's an exploit :)) Polje ki ima 0 flaggas, potem pa naredis front click,
# pa se vse okoli pokaze (to pomeni da z lahkoto najdes nicle, samo flagas, kliknes, unflagas, ce se kaj odpre,
# si na nicli)