from tkinter import *
import random


class Polje():
    def __init__(self, x, y, vrednost=0):
        self.x = x
        self.y = y
        self.vrednost = vrednost
        self.odprto = False
        self.prikaz = None
        self.flagged = False

    def __str__(self):
        return str(self.prikaz)

    def odpri(self):
        if not self.flagged and not self.odprto:
            self.prikaz = self.vrednost
            self.odprto = True
            return True
        return False

    def oznaci(self):
        if not self.odprto:
            self.prikaz = 'f' if '_' == self.prikaz else '_'
            self.flagged = True if not self.flagged else False
            return True
        return False

    def prikaz(self):
        pass


class Minesweeper():
    def __init__(self, master, velikost, mine):
        self.velikost = velikost
        self.kvadratek = 30
        self.mine = mine
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.preostale_mine = self.mine
        self.zmage = IntVar(0)
        self.porazi = IntVar(0)

        # --- GUI ---
        master.title('Minolovec')

        okvir = Frame(master)
        okvir.grid()

        menu = Menu(master)
        master.config(menu=menu)
        podmenu = Menu(menu)
        podmenu.add_command(label='Nova igra', command=self.nova_igra)
        podmenu.add_command(label='Izhod', command=self.quit)
        menu.add_cascade(label='File', menu=podmenu)

        Label(okvir, text='Zmage: ').grid(row=0, column=0)
        Label(okvir, textvariable=self.zmage).grid(row=0, column=1, sticky='W')
        Label(okvir, text='Porazi: ').grid(row=1, column=0)
        Label(okvir, textvariable=self.porazi).grid(row=1, column=1, sticky='W')

        self.platno = Canvas(okvir, width=self.velikost*self.kvadratek, height=self.velikost*self.kvadratek,
                             background='#FFFFFF')
        self.platno.grid(row=2, column=0, columnspan=2)
        for i in range(1, self.velikost):
            self.platno.create_line(i*self.kvadratek, 0, i*self.kvadratek, self.velikost*self.kvadratek)
            self.platno.create_line(0, i*self.kvadratek, self.velikost*self.kvadratek, i*self.kvadratek)
        self.platno.bind("<Button-1>", self.levi_klik)
        self.platno.bind("<Button-3>", self.desni_klik)

        self.napolni()
        print(self.polje)

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

    # def prikazi_celotno_polje(self, odkrito=False):
    #     """ Prikaze celotno polje min in praznih kvadratkov. """
    #     niz = ''
    #     for x in self.polje:
    #         niz += '|'
    #         for y in x:
    #             n = y.vrednost if odkrito else str(y)
    #             niz += ' {0} |'.format(n)
    #         niz += '\n'
    #     print(niz)

    def levi_klik(self, klik):
        y = klik.x // self.kvadratek
        x = klik.y // self.kvadratek
        odpr = self.polje[x][y].odpri()
        if odpr:
            self.platno.create_text(y * self.kvadratek + (self.kvadratek // 2), x * self.kvadratek +
                                    (self.kvadratek // 2), text=self.polje[x][y].vrednost)

    def desni_klik(self, klik):
        y = klik.x // self.kvadratek
        x = klik.y // self.kvadratek
        ozn = self.polje[x][y].oznaci()
        if ozn:
            self.platno.create_text(y * self.kvadratek + (self.kvadratek // 2), x * self.kvadratek +
                                    (self.kvadratek // 2), text='f')
            print(self.platno.find_closest(klik.x, klik.y))

    def odpri_blok(self, koord):
        """ Sprejme tuple koord s koordinatami, kamor je uporabnik levo-kliknil (kjer je prazno polje), in odpre vsa
        sosednja polja, ce je stevilo min v okolici polja 0. Postopek ponavlja za vsako polje, ki se odpre,
        dokler ne naleti na polje, ki ima v okolici kaksno mino. """
        odpri = [koord]
        while odpri:
            x, y = odpri.pop()
            self.polje[x][y].odpri()
            if self.polje[x][y].vrednost == 0:
                for i in range(max(0, x-1), min(x+2, self.velikost)):
                    for j in range(max(0, y-1), min(y+2, self.velikost)):
                        if not self.polje[i][j].odprto:
                            odpri.append((i, j))

    def posodobi(self, x, y, m):
        """ Sprejme koordinate, kamor je kliknil uporabnik, in ali je oznacil mino ali ne ter posodobi igro,
        tako da odpre polja oziroma oznaci mino. """
        if m:
            ozn = self.polje[x][y].oznaci()
            if ozn:
                self.preostale_mine -= 1
        else:
            if self.polje[x][y].vrednost == 'x':
                return False
            else:
                self.polje[x][y].odpri()
                if self.polje[x][y].vrednost == 0:
                    self.odpri_blok((x, y))
        return True

    def konec(self):
        for x in self.polje:
            for y in x:
                if not (y.odprto or y.flagged):
                    return False
        return True

    def nova_igra(self):
        pass

    def quit(self):
        pass

    # def igra(self):
    #     while True:
    #         self.prikazi_celotno_polje()
    #         print("Preostale mine:", self.preostale_mine)
    #         v = int(input("Vrstica: ")) - 1
    #         s = int(input("Stolpec: ")) - 1
    #         m = input("(m)ina / (p)razno: ")
    #         m = (m == 'm')
    #         poteka = self.posodobi(v, s, m)
    #         if not poteka:
    #             self.prikazi_celotno_polje(odkrito=True)
    #             print('Zal ste naleteli na mino!')
    #             self.porazi += 1
    #             break
    #         konec = self.konec()
    #         if konec:
    #             self.prikazi_celotno_polje(odkrito=True)
    #             if self.preostale_mine == 0:
    #                 self.zmage += 1
    #                 print('Zmagali ste!')
    #             else:
    #                 self.porazi += 1
    #                 print('Izgubili ste!')
    #             break


# igrica = Minesweeper(5, 3)
# igrica.napolni()
# igrica.prikazi_celotno_polje(odkrito=True)
# igrica.igra()
root = Tk()
igrica = Minesweeper(root, 10, 3)
root.mainloop()