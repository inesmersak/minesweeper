import random


class Racunalnik:
    def __init__(self):
        self.odpri = set()
        self.oznaci = []

        self.matrika = []
        self.velikost_matrike = 0
        self.odprta_polja = []
        self.zaprta_polja = []
        self.zastave = []

    def pridobi_podatke(self):
        self.velikost_matrike = len(self.matrika)
        self.odprta_polja = []
        self.zaprta_polja = []
        self.zastave = []
        for x in range(self.velikost_matrike):
            for y in range(self.velikost_matrike):
                v = self.matrika[x][y]
                if isinstance(v, int):
                    self.odprta_polja.append((x, y))
                elif v == 'f':
                    self.zastave.append((x, y))
                else:
                    self.zaprta_polja.append((x, y))

    def vrni_potezo(self, matrika):
        self.matrika = matrika
        self.pridobi_podatke()
        # print(self.odpri)

        if self.odpri:
            poteza = self.odpri.pop()
        else:
            self.izracunaj_potezo()
            if self.odpri:
                poteza = self.odpri.pop()
            else:
                # self.simuliraj()
                poteza = self.nakljucna_poteza()
        return poteza

    def izracunaj_potezo(self):
        for (x, y) in self.odprta_polja:
            v = self.matrika[x][y]
            zastave = self.vrni_sosednje_zastave(x, y)
            sosedi = self.zaprti_sosedje(x, y)
            if v == zastave:
                for (z, w) in sosedi:
                    self.odpri.add((z, w, False))
            elif len(sosedi) + zastave == v:
                for (z, w) in sosedi:
                    self.odpri.add((z, w, True))

    def nakljucna_poteza(self):
        (x, y) = random.choice(self.zaprta_polja)
        return tuple([x, y, False])

    def simuliraj(self):
        rob = self.doloci_rob()
        print(rob)

    def vrni_sosednje_zastave(self, x, y):
        """ Vrne stevilo trenutnih zastav v okolici polja, podana z x in y. """
        zastave = 0
        for z in range(max(0, x - 1), min(x + 2, self.velikost_matrike)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost_matrike)):
                if z != x or w != y:
                    if (z, w) in self.zastave:
                        zastave += 1
        return zastave

    def vrni_sosednja_polja(self, x, y):
        """ Vrne koordinate sosednjih polj polja, podanega z x in y. """
        sosedi = []
        for z in range(max(0, x - 1), min(x + 2, self.velikost_matrike)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost_matrike)):
                if z != x or w != y:
                    sosedi.append((z, w))
        return sosedi

    def zaprti_sosedje(self, x, y):
        sosedi = self.vrni_sosednja_polja(x, y)
        zaprti = []
        for s in sosedi:
            if s in self.zaprta_polja:
                zaprti.append(s)
        return zaprti

    def doloci_rob(self):
        """ Doloci, kje je rob odprtih polj. Zaprto polje je na robu, ce se na vsaj eni izmed stranic tega polja
        nahajajo tri zaprta polja. """
        rob = []
        spodaj = True  # rob je spodaj
        zgoraj = True  # rob je zgoraj
        levo = True  # rob je na levi
        desno = True  # rob je na desni
        for (x, y) in self.zaprta_polja:
            for w in range(max(0, y - 1), min(y + 2, self.velikost_matrike)):
                if zgoraj and x - 1 >= 0:
                    if (x - 1, w) not in self.odprta_polja:
                        zgoraj = False
                if spodaj and x + 1 < self.velikost_matrike:
                    if (x + 1, w) not in self.odprta_polja:
                        spodaj = False
            if zgoraj and x == 0: zgoraj = False  # ce je polje na zgornjem robu polja, zgornjega roba nima
            if spodaj and x == self.velikost_matrike - 1: spodaj = False  # ce je polje na spodnjem robu polja,
            # spodnjega roba nima

            for z in range(max(0, x - 1), min(x + 2, self.velikost_matrike)):
                if levo and y - 1 >= 0:
                    if (z, y - 1) not in self.odprta_polja:
                        levo = False
                if desno and y + 1 < self.velikost_matrike:
                    if (z, y + 1) not in self.odprta_polja:
                        desno = False
            if levo and y == 0: levo = False  # ce je polje na levem robu polja, levega roba nima
            if desno and y == self.velikost_matrike - 1: desno = False  # ce je polje na desnem robu polja,
            # desnega roba nima

            if spodaj or zgoraj or levo or desno:
                rob.append((x, y))

            levo = True
            desno = True
            spodaj = True
            zgoraj = True
        return rob

    def preveri_veljavnost_polja(self):
        # tukaj se nekaj o preostalih minah
        for x in range(self.velikost_matrike):
            for y in range(self.velikost_matrike):
                v = self.matrika[x][y]
                if isinstance(v, int):
                    zaprti_sosedi = self.zaprti_sosedje(x, y)
                    if len(zaprti_sosedi) < v:
                        return False
        return True