import random
import itertools
from copy import deepcopy


class Racunalnik:
    def __init__(self):
        self.odpri = set()
        self.oznaci = []

        self.matrika = []
        self.velikost_matrike = 0
        self.preostale_mine = 0
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

    def vrni_potezo(self, matrika, mine):
        self.matrika = matrika
        self.preostale_mine = mine
        self.pridobi_podatke()
        # print(self.odpri)

        if self.odpri:
            poteza = self.odpri.pop()
        else:
            self.izracunaj_potezo()
            if self.odpri:
                poteza = self.odpri.pop()
            else:
                poteza = self.simuliraj()
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
        if not self.odpri:
            if len(self.zaprta_polja) == self.preostale_mine:
                for (z, w) in self.zaprta_polja:
                    self.odpri.add((z, w, True))
            elif self.preostale_mine == 0:  # tale opcija je mogoce ze pokrita v zgornji for zanki
                for (z, w) in self.zaprta_polja:
                    self.odpri.add((z, w, False))

    def nakljucna_poteza(self):
        (x, y) = random.choice(self.zaprta_polja)
        return tuple([x, y, False])

    def izracunaj_verjetnost(self, p):
        """ Izracuna verjetnost, da je poteza pravilna, na osnovi celotnega polja. """
        (x, y, m) = p
        imenovalec = len(self.zaprta_polja)
        if m:  # torej nas zanima, kaksna je verjetnost, da je na temu polju mina:
            stevec = self.preostale_mine
        else:  # zanima nas, kaksna je verjetnost, da je polje prazno
            stevec = imenovalec - self.preostale_mine
        return stevec / imenovalec

    def vrni_kombinacije(self, moznosti, dolzina, moznost=None):
        """ V seznam 'moznosti' spravlja vse mozne kombinacije dolzine 'dolzina' in pri tem uporablja rekurzijo. """
        if moznost is None:
            moznost = []
        if dolzina == 0:
            moznosti.append(moznost)
        else:
            self.vrni_kombinacije(moznosti, dolzina - 1, moznost + ['e'])  # e = empty, predstavlja prazno polje
            self.vrni_kombinacije(moznosti, dolzina - 1, moznost + ['f'])

    def vrni_kombinacije2(self, dolzina):
        k = set()
        a = itertools.combinations_with_replacement(['e', 'f'], 5)
        for x in a:
            p = itertools.permutations(x)
            for y in p:
                k.add(y)
        return k

    def vrni_podpolje(self, koord):
        """ Vrne zacetno in koncno tocko 5 x 5 podpolja okoli koordinate (x, y). """
        (x, y) = koord
        v1 = max(0, x - 2)
        v2 = min(x + 2, self.velikost_matrike)
        s1 = max(0, y - 2)
        s2 = min(y + 2, self.velikost_matrike)
        return (v1, s1), (v2, s2)

    def preveri_veljavnost_podpolja(self, matrika, zacetek, konec):
        """ Sprejme matriko, kje zacnemo pregledovati in kje koncamo, ter vrne ali je to podpolje veljavno ali ne. """
        (v1, s1) = zacetek
        (v2, s2) = konec
        for i in range(v1, v2+1):
            for j in range(s1, s2+1):
                vrednost = matrika[i][j]
                if isinstance(vrednost, int):
                    zastave = self.vrni_sosednje_zastave(i, j)
                    # if zastave

    def preizkusi_kombinacije(self, kvad):
        """ Za dana polja iz seznama 'kvad' preizkusi vse mozne kombinacije. """
        komb = []
        st_polj = len(kvad)
        self.vrni_kombinacije(komb, st_polj)
        # print(len(kvad), len(komb))
        p = None
        v = 0
        veljavne_komb = []
        for kombinacija in komb:
            if kombinacija.count('f') <= self.preostale_mine:
                # zacasna_matrika = deepcopy(self.matrika)
                # sredinski_kvad = kvad[len(kvad)-1]  # kvadratek v sredini smo v simuliraj dodali na konec kvad
                # zac, kon = self.vrni_podpolje(sredinski_kvad)
                poteze_za_razveljavit = []
                for i in range(len(kombinacija)):
                    (x, y) = kvad[i]
                    m = True if kombinacija[i] == 'f' else False
                    self.simuliraj_potezo((x, y, m))
                    poteze_za_razveljavit.append((x, y, m))
                if self.preveri_veljavnost_polja():
                    veljavne_komb.append(kombinacija)
                while poteze_za_razveljavit:
                    self.preklici_potezo(poteze_za_razveljavit.pop())
                #     zacasna_matrika[x][y] = kombinacija[i]
                # if self.preveri_veljavnost_podpolja(zacasna_matrika, zac, kon):
                #     veljavne_komb.append(kombinacija)
        for i in range(st_polj):
            st_min = 0
            st_odprtih = 0
            for j in range(len(veljavne_komb)):
                if veljavne_komb[j][i] == 'f':
                    st_min += 1
                elif veljavne_komb[j][i] == 'e':
                    st_odprtih += 1
            verjetnost = st_odprtih / (st_odprtih + st_min)
            if verjetnost > v:
                (z, w) = kvad[i]
                p = (z, w, False)
                v = verjetnost
        return p, v

    def simuliraj(self):
        p = self.nakljucna_poteza()
        verjetnost = self.izracunaj_verjetnost(p)
        print(p, verjetnost)
        for (x, y) in self.zaprta_polja:
            zaprti_sosedi = self.zaprti_sosedje(x, y)
            if len(zaprti_sosedi) == 0 or len(zaprti_sosedi) == 8:
                pass
            else:
                zaprti_sosedi.append((x, y))
                (p1, verp1) = self.preizkusi_kombinacije(zaprti_sosedi)
                if verp1 == 1:
                    p = p1
                    verjetnost = verp1
                    break
                elif verp1 > verjetnost:
                    p = p1
                    verjetnost = verp1
        print(p, verjetnost)
        print("---------------------")
        return p

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
                    zastave = self.vrni_sosednje_zastave(x, y)
                    if len(zaprti_sosedi) + zastave < v:
                        return False
                    elif zastave > v:
                        return False
        return True

    def simuliraj_potezo(self, p):
        (x, y, m) = p
        v = self.matrika[x][y]
        if v == '':  # polje je zaprto
            self.zaprta_polja.remove((x, y))
            if m:
                self.matrika[x][y] = 'f'
                self.zastave.append((x, y))
                self.preostale_mine -= 1
            else:
                self.matrika[x][y] = 'e'  # 'e' bo oznaceval odprto polje, katerega vrednost ne poznamo
                self.odprta_polja.append((x, y))

    def preklici_potezo(self, p):
        (x, y, m) = p
        v = self.matrika[x][y]
        if v != '':  # polje je odprto ali zastavica, torej smo naredili neko potezo na tem polju
            if m:
                self.zastave.remove((x, y))
                self.preostale_mine += 1
            else:
                self.odprta_polja.remove((x, y))
            self.matrika[x][y] = ''
            self.zaprta_polja.append((x, y))