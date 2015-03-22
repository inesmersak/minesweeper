import random


class Racunalnik:
    def __init__(self, igra):
        self.odpri = []
        self.oznaci = []
        self.igra = igra
        self.stanje_polja = None
        self.odprta_polja = None
        self.zaprta_polja = None
        self.zastave = None

    def naredi_potezo(self):
        if self.odpri:
            poteza = self.odpri.pop()
        else:
            self.izracunaj_potezo()
            if self.odpri:
                poteza = self.odpri.pop()
            else:
                poteza = self.nakljucna_poteza()
        self.igra.poteza(*poteza)
        self.posodobi_stanje_polja(poteza)

    def izracunaj_potezo(self):
        d = self.igra.velikost
        for x in range(d):
            for y in range(d):
                p = self.stanje_polja[x][y]
                if p != '' and p != 'f':
                    zastave = self.igra.vrni_sosednje_zastave(x, y)
                    if p == zastave:
                        poteze = self.igra.vrni_sosednja_polja(x, y)
                        for (z, w) in poteze:
                            self.odpri.append((z, w, False))
                    else:
                        zaprti_sosedi = self.zaprti_sosedje(x, y)
                        if len(zaprti_sosedi) == p:
                            for (z, w) in zaprti_sosedi:
                                self.odpri.append((z, w, True))

    def nakljucna_poteza(self):
        (x, y) = random.choice(self.zaprta_polja)
        return (x, y, False)

    def simuliraj(self):
        pass

    def zaprti_sosedje(self, x, y):
        sosedi = self.igra.vrni_sosednja_polja(x, y)
        zaprti = []
        for s in sosedi:
            if s in self.zaprta_polja:
                zaprti.append(s)
        return zaprti

    def zgradi_stanje_polja(self):
        if self.stanje_polja is None:
            v = self.igra.velikost
            self.odprta_polja = []
            self.zaprta_polja = [(i, j) for i in range(v) for j in range(v)]
            self.stanje_polja = [['' for _ in range(v)] for _ in range(v)]
            for r in self.igra.polje:
                for c in r:
                    koord = (c.x, c.y)
                    if c.odprto:
                        self.stanje_polja[c.x][c.y] = c.vrednost
                        self.zaprta_polja.remove(koord)
                        self.odprta_polja.append(koord)
                    elif c.flagged:
                        self.stanje_polja[c.x][c.y] = 'f'
                        self.zaprta_polja.remove(koord)
                        self.zastave.append(koord)

    def posodobi_stanje_polja(self, poteza):
        """ Sprejme potezo, ki jo racunalnik naredi, in posodobi polje. Poteza je nabor, sestavljen iz dveh koordinat in
         booleana, ki nam pove, ali smo polje oznacili z zastavico."""
        if self.stanje_polja is not None:
            (x, y, m) = poteza
            self.stanje_polja[x][y] = 'f' if m else self.igra.polje[x][y].vrednost