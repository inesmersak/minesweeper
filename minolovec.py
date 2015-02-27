import random


class Minesweeper():
    def __init__(self, velikost, mine):
        self.velikost = velikost
        self.mine = mine
        self.polje = [[0 for x in range(self.velikost)] for y in range(self.velikost)]
        self.odkrito = [['-' for x in range(self.velikost)] for y in range(self.velikost)]
        self.preostale_mine = self.mine

    def spremeni_stevilko_polj(self, x, y):
        """ Spremeni stevilko polj okoli mine, ta je podana s koordinatami x in y. """
        for z in range(max(0, x-1), min(x+2, self.velikost)):
            for w in range(max(0, y-1), min(y+2, self.velikost)):
                if self.polje[z][w] != 'x':
                    self.polje[z][w] += 1

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
            self.spremeni_stevilko_polj(x, y)
            i -= 1

    def prikazi_celotno_polje(self, odkrito=False):
        """ Prikaze celotno polje min in praznih kvadratkov. """
        niz = ''
        if odkrito: data = self.polje
        else: data = self.odkrito
        for x in data:
            niz += '|'
            for i in range(self.velikost):
                niz += ' {0} |'.format(x[i])
            niz += '\n'
        print(niz)

    def posodobi(self, x, y, m):
        if m:
            self.odkrito[x][y] = 'f'
            self.preostale_mine -= 1
        else:
            if self.polje[x][y] == 'x':
                return False
            else:
                self.odkrito[x][y] = self.polje[x][y]
        return True

    def igra(self):
        while True:
            self.prikazi_celotno_polje()
            print("Preostale mine:",self.mine)
            v = int(input("Vrstica: ")) - 1
            s = int(input("Stolpec: ")) - 1
            m = input("(m)ina / (p)razno: ")
            if m == 'm': m = 1
            else: m = 0
            poteka = self.posodobi(v, s, m)
            if not poteka:
                self.prikazi_celotno_polje(odkrito=True)
                print('Zal ste naleteli na mino!')
                break


igrica = Minesweeper(5, 5)
igrica.napolni()
igrica.prikazi_celotno_polje(odkrito=True)
igrica.igra()

