import random


class Polje():
    def __init__(self, x, y, vrednost=0):
        self.x = x
        self.y = y
        self.vrednost = vrednost
        self.odprto = False
        self.prikaz = '_'
        self.flagged = False

    def __str__(self):
        return str(self.prikaz)

    def odpri(self):
        self.prikaz = self.vrednost
        self.odprto = True

    def oznaci(self):
        if not self.odprto:
            self.prikaz = 'f'
            self.flagged = True

    def odznaci(self):
        if not self.odprto:
            self.prikaz = '_'
            self.flagged = False


class Minesweeper():
    def __init__(self, velikost, mine):
        self.velikost = velikost
        self.mine = mine
        self.polje = [[Polje(j, i) for i in range(self.velikost)] for j in range(self.velikost)]
        self.preostale_mine = self.mine
        self.zmage = 0
        self.porazi = 0

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
            self.polje[x][y].oznaci()
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

    def igra(self):
        while True:
            self.prikazi_celotno_polje()
            print("Preostale mine:", self.preostale_mine)
            v = int(input("Vrstica: ")) - 1
            s = int(input("Stolpec: ")) - 1
            m = input("(m)ina / (p)razno: ")
            m = (m == 'm')
            poteka = self.posodobi(v, s, m)
            if not poteka:
                self.prikazi_celotno_polje(odkrito=True)
                print('Zal ste naleteli na mino!')
                self.porazi += 1
                break
            konec = self.konec()
            if konec:
                self.prikazi_celotno_polje(odkrito=True)
                self.zmage += 1
                print('Zmagali ste!')
                break


igrica = Minesweeper(5, 3)
igrica.napolni()
#igrica.prikazi_celotno_polje(odkrito=True)
igrica.igra()
