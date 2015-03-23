import random


class Racunalnik:
    def __init__(self, igra):
        self.odpri = []
        self.oznaci = []
        self.igra = igra

    def vrni_potezo(self):
        if self.odpri:
            poteza = self.odpri.pop()
        else:
            self.izracunaj_potezo()
            if self.odpri:
                poteza = self.odpri.pop()
            else:
                poteza = self.nakljucna_poteza()
        return poteza

    def izracunaj_potezo(self):
        for (x, y) in self.igra.odprta_polja:
            v = self.igra.polje[x][y].prikaz
            zastave = self.igra.vrni_sosednje_zastave(x, y)
            sosedi = self.zaprti_sosedje(x, y)
            if v == zastave:
                for (z, w) in sosedi:
                    self.odpri.append((z, w, False))
            elif len(sosedi) + zastave == v:
                for (z, w) in sosedi:
                    self.odpri.append((z, w, True))

    def nakljucna_poteza(self):
        (x, y) = random.choice(self.igra.zaprta_polja)
        return tuple([x, y, False])

    def simuliraj(self):
        pass

    def zaprti_sosedje(self, x, y):
        sosedi = self.igra.vrni_sosednja_polja(x, y)
        zaprti = []
        for s in sosedi:
            if s in self.igra.zaprta_polja:
                zaprti.append(s)
        return zaprti