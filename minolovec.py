import random


class Minesweeper():
    def __init__(self, velikost, mine):
        self.velikost = velikost
        self.mine = mine
        self.polje = [[0 for x in range(self.velikost)] for y in range(self.velikost)]

    def spremeni_stevilko_polj(self, x, y):
        """ Spremeni stevilko polj okoli mine, ta je podana s koordinatami x in y. """
        for z in range(x-1, max(x+2, self.velikost)):
            for w in range(y-1, max(y+2, self.velikost)):

        if x-1 >= 0:
            self.polje[x-1][y] += 1
            if y-1 >= 0: self.polje[x-1][y-1] += 1
            if y+1 < self.velikost: self.polje[x-1][y+1] += 1
        if x+1 < self.velikost:
            self.polje[x+1][y] += 1
            if y+1 < self.velikost: self.polje[x+1][y+1] += 1
            if y-1 >= 0: self.polje[x+1][y-1] += 1
        if y-1 >= 0: self.polje[x][y-1] += 1
        if y+1 < self.velikost: self.polje[x][y+1] += 1

    def napolni(self):
        """ Nakljucno napolni igralno polje s 'self.mine' stevilom min. Mine so oznacene z x, prazni kvadratki z 0. """
        i = self.mine
        while i > 0:
            x = random.randint(0, self.velikost-1)
            y = random.randint(0, self.velikost-1)
            while self.polje[x][y] == 'x':
                x = random.randint(0, self.velikost-1)
                y = random.randint(0, self.velikost-1)
            self.polje[x][y] = 'x'
            i -= 1

    def prikazi_celotno_polje(self):
        """ Prikaze celotno polje min in praznih kvadratkov. """
        niz = ''
        for x in self.polje:
            niz += '|'
            for i in range(self.velikost):
                niz += ' {0} |'.format(x[i])
            niz += '\n'
        print(niz)

    def vrni_kvadratek(self, vrstica, stolpec):
        """ Vrne vrednost kvadratka, ki se nahaja v dani vrstici in stolpcu. """
        kvadratek = self.polje[vrstica][stolpec]
        return kvadratek


igrica = Minesweeper(10, 10)
igrica.napolni()
igrica.prikazi_celotno_polje()

