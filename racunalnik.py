import random
import itertools
from copy import deepcopy
import time
import datetime


class Racunalnik:
    def __init__(self):
        self.odpri = set()  # sem bomo shranjevali poteze, ki jih bomo naredili

        # te spremenljivke bomo nastavili, ko bo igra racunalniku podala matriko s trenutnim stanjem polja
        self.matrika = []
        self.velikost_matrike = 0
        self.preostale_mine = 0
        self.odprta_polja = set()
        self.zaprta_polja = set()
        self.zastave = set()

        self.debugmode = True  # ce smo v debug modeu, program izpisuje koristne informacije o poteku razmisljanja na
        # zaslon

    def pridobi_podatke(self, matrika):
        """ Sprejme matriko, ki vsebuje trenutno stanje polja, jo obdela in shrani informacije o tem, kje so polja z
        zastavico, odprta in zaprta polja. """
        self.matrika = matrika
        self.velikost_matrike = len(self.matrika)
        self.odprta_polja = set()
        self.zaprta_polja = set()
        self.zastave = set()
        for x in range(self.velikost_matrike):
            for y in range(self.velikost_matrike):
                v = self.matrika[x][y]
                if isinstance(v, int):
                    self.odprta_polja.add((x, y))
                elif v == 'f':
                    self.zastave.add((x, y))
                else:
                    self.zaprta_polja.add((x, y))

    def vrni_potezo(self, matrika, mine):
        """ Metoda, ki sprejme matriko s trenutnim stanjem polja in preostalim stevilom min, ter vrne potezo. """
        self.preostale_mine = mine
        self.pridobi_podatke(matrika)

        if self.odpri:  # ce smo ob prejsnjem racunanju poteze nasli vec potez, self.odpri ne bo prazen in lahko
            # naredimo eno izmed teh potez, ki je se nismo
            poteza = self.odpri.pop()
        else:  # sicer ponovno racunamo potezo
            self.izracunaj_potezo_s_preprostim_sklepanjem()
            if self.odpri:  # ce smo po preprostem sklepanju nasli potezo, jo naredimo
                poteza = self.odpri.pop()
            else:  # sicer pozenemo simulacijo
                poteza = self.simuliraj()
        return poteza

    def izracunaj_potezo_s_preprostim_sklepanjem(self):
        """ S pomocjo preproste metode sklepanja preveri, ali obstaja kaksna poteza, ki jo lahko zagotovo naredimo. """
        for (x, y) in self.odprta_polja:  # za vsako polje, ki je prazno in odprto (torej ze poznamo njegovo vrednost)
            v = self.matrika[x][y]
            zastave = self.vrni_sosednje_zastave(x, y)
            sosedi = self.sosedje(x, y, True, False)
            if v == zastave:  # v okolici polja je toliko zastav, kolikor je treba
                for (z, w) in sosedi:
                    self.odpri.add((z, w, False))  # ostala sosednja zaprta polja lahko odpremo
            elif len(sosedi) + zastave == v:  # v okolici polja je se toliko zaprtih polj, kolikor manjka min v okolici
                for (z, w) in sosedi:
                    self.odpri.add((z, w, True))  # vsa zaprta polja oznacimo z zastavico
        if not self.odpri:  # ce se nismo nasli resitve, pogledamo, ali lahko na isti nacin kot zgoraj sklepamo globalno
            if len(self.zaprta_polja) == self.preostale_mine:
                for (z, w) in self.zaprta_polja:
                    self.odpri.add((z, w, True))
            elif self.preostale_mine == 0:
                for (z, w) in self.zaprta_polja:
                    self.odpri.add((z, w, False))

    def nakljucna_poteza(self):
        """ Vrne potezo, ki odpre nakljucno izmed zaprtih polj. """
        (x, y) = random.choice(list(self.zaprta_polja))
        return tuple([x, y, False])

    def izracunaj_verjetnost(self, p):
        """ Izracuna verjetnost, da je poteza pravilna, na osnovi celotnega polja. """
        (x, y, m) = p
        imenovalec = len(self.zaprta_polja)
        if m:  # torej nas zanima, kaksna je verjetnost, da je na temu polju mina
            stevec = self.preostale_mine
        else:  # zanima nas, kaksna je verjetnost, da je polje prazno
            stevec = imenovalec - self.preostale_mine
        return stevec / imenovalec

    def vrni_koordinate_podpolja(self, koord):
        """ Vrne zacetno in koncno tocko 5 x 5 podpolja s srediscem v koordinati (x, y). """
        (x, y) = koord
        v1 = max(0, x - 2)
        v2 = min(x + 2, self.velikost_matrike - 1)
        s1 = max(0, y - 2)
        s2 = min(y + 2, self.velikost_matrike - 1)
        return (v1, s1), (v2, s2)

    def preveri_veljavnost_polja(self, zac, kon):
        """ Preveri, ali je polje od tocke zac do tocke kon veljavno. """
        (i1, j1) = zac  # i1 je vrstica, kjer zacnemo; j1 je stolpec, kjer zacnemo
        (i2, j2) = kon  # i2 je vrstica, kjer koncamo; j2 je stolpec, kjer koncamo
        for x in range(i1, i2+1):
            for y in range(j1, j2+1):
                v = self.matrika[x][y]
                if isinstance(v, int):
                    zaprti_sosedi = self.sosedje(x, y, True, False)
                    zastave = self.vrni_sosednje_zastave(x, y)
                    if len(zaprti_sosedi) + zastave < v:  # ce imamo v okolici manj zastavic in zaprtih polj,
                        # kot je min v okolici tega kvadratka, potem je polje neveljavno
                        return False
                    elif zastave > v:  # ce imamo v okolici kvadratka prevec zastav, je polje prav tako neveljavno
                        return False
        return True

    def preizkusi_kombinacije(self, kvad):
        """ Za dana polja iz seznama 'kvad' generira vse mozne kombinacije min in praznih polj, neveljavne zavrze,
        nato pa iz veljavnih izracuna verjetnost, da bo polje prazno, in izbere potezo na teh poljih z najboljso
        verjetnostjo. """
        st_polj = len(kvad)  # taksna bo dolzina nasih kombinacij
        komb = list(set(itertools.product('ef', repeat=st_polj)))  # s pomocjo itertools generiramo vse kombinacije
        p = None  # na zacetku nimamo poteze
        v = 0  # verjetnost, da je ta poteza pravilna, je nic
        veljavne_komb = []
        # prej = time.clock()
        for kombinacija in komb:  # za vsako kombinacijo preverimo, ali je mozna
            if kombinacija.count('f') <= self.preostale_mine:  # ce je zastavic vec kot preostalih min, kombinacija
                # ni mozna
                sredinski_kvad = kvad[len(kvad)-1]  # kvadratek v sredini je vedno na koncu seznama kvad
                poteze_za_razveljavit = []
                for i in range(len(kombinacija)):  # za vsako mozno kombinacijo simuliramo poteze in s tem napolnimo
                    # polje, preverimo, ali je polje se vedno veljavno, na koncu pa preklicemo vse narejene poteze
                    (x, y) = kvad[i]
                    m = True if kombinacija[i] == 'f' else False
                    self.simuliraj_potezo((x, y, m))
                    poteze_za_razveljavit.append((x, y, m))  # potezo si shranimo, da jo lahko kasneje razveljavimo
                zac, kon = self.vrni_koordinate_podpolja(sredinski_kvad)
                if self.preveri_veljavnost_polja(zac, kon):
                    veljavne_komb.append(kombinacija)  # ce je polje veljavno, je ta kombinacija mozna
                while poteze_za_razveljavit:
                    self.preklici_potezo(poteze_za_razveljavit.pop())
        # potem = time.clock()
        # print("cas za vse kombinacije: ", potem-prej)
        # prej = time.clock()

        # sedaj izracunamo verjetnosti za to, ali so polja odprta, s pomocjo kombinacij, ki so nam ostale
        for i in range(st_polj):
            st_min = 0
            st_odprtih = 0
            for j in range(len(veljavne_komb)):  # za vsako polje posebej gremo cez vse veljavne kombinacije in
                # prestejemo, v koliko kombinacijah je na tem polju mina, in v koliko primerih je polje odprto
                if veljavne_komb[j][i] == 'f':
                    st_min += 1
                elif veljavne_komb[j][i] == 'e':
                    st_odprtih += 1
            verjetnost = st_odprtih / (len(veljavne_komb))  # verjetnost, da je polje odprto
            if verjetnost == 1:  # ce je verjetnost 1, smo nasli polje, ki je zagotovo prazno, zato lahko nehamo gledat
                (z, w) = kvad[i]
                p = (z, w, False)
                v = verjetnost
                break
            elif verjetnost > v:  # ce je verjetnost vecja od do zdaj najboljse verjetnosti, si zapomnemo to novo
                # verjetnost in potezo
                (z, w) = kvad[i]
                p = (z, w, False)
                v = verjetnost
        # potem = time.clock()
        # print("cas za verjetnosti potez: ", potem - prej)
        return p, v  # vrnemo potezo z najboljso verjetnostjo

    def simuliraj(self):
        """ Za vsako polje, ki ima vsaj enega odprtega soseda, vzame vse zaprte sosede in to polje ter na teh poljih
        preizkusi vse mozne kombinacije s pomocjo metode 'preizkusi_kombinacije' - tako dobi najboljso mozno potezo
        na teh poljih. To ponovi za vsako polje z vsaj enim odprtim sosedom in primerja verjetnost dobljenih potez,
        na koncu pa vrne potezo z najvecjo verjetnostjo. """
        if self.debugmode: prej = time.clock()
        p = self.nakljucna_poteza()  # na zacetku vzamemo neko nakljucno potezo, zracunamo njegovo verjetnost,
        # potem iscemo potezo, ki ima boljso verjetnost
        verjetnost = self.izracunaj_verjetnost(p)
        if self.debugmode: print(p, verjetnost)
        for (x, y) in self.zaprta_polja:
            zaprti_sosedi, odprti_sosedi = self.sosedje(x, y, True, True)
            if len(zaprti_sosedi) == 8 or len(odprti_sosedi) < 1:  # pregledujemo le polja z vsaj enim odprtim in
                # vsaj enim zaprtim sosedom
                pass
            else:
                if self.debugmode: print("Pregledujemo polje ", x, y)
                zaprti_sosedi.append((x, y))
                (p1, verp1) = self.preizkusi_kombinacije(zaprti_sosedi)  # dobimo najboljso mozno potezo na teh poljih
                if verp1 == 1:  # poteza p1 je gotova, lahko nehamo razmisljat
                    p = p1
                    verjetnost = verp1
                    break
                elif verp1 > verjetnost:  # verjetnost poteze p1 je boljsa od vseh do zdaj, zapomnemo si novo potezo
                    # in verjetnost
                    p = p1
                    verjetnost = verp1
        if self.debugmode:
            potem = time.clock()
            print(p, verjetnost)
            print("Čas za kalkulacijo: ", potem - prej)
            print("---------------------")
        return p  # vrnemo potezo z najvecjo verjetnostjo

    def vrni_sosednje_zastave(self, x, y):
        """ Vrne stevilo trenutnih zastav v okolici polja, podanega z x in y. """
        zastave = 0
        for z in range(max(0, x - 1), min(x + 2, self.velikost_matrike)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost_matrike)):
                if z != x or w != y:
                    if (z, w) in self.zastave:
                        zastave += 1
        return zastave

    def sosedje(self, x, y, zap=True, odp=True):
        """ Vrne sosede polja s koordinatama x, y: če zap = True, vrne zaprte sosede; če odp = True, vrne odprte
        sosede; če sta zap in odp = True, vrne zaprte in odprte sosede. """
        if zap: zaprti = []
        if odp: odprti = []
        for z in range(max(0, x - 1), min(x + 2, self.velikost_matrike)):
            for w in range(max(0, y - 1), min(y + 2, self.velikost_matrike)):
                if z != x or w != y:
                    polje = (z, w)
                    if polje in self.zaprta_polja and zap:
                        zaprti.append(polje)
                    elif polje in self.odprta_polja and odp:
                        odprti.append(polje)
        if zap and odp: return zaprti, odprti
        elif zap: return zaprti
        elif odp: return odprti

    def simuliraj_potezo(self, p):
        (x, y, m) = p
        v = self.matrika[x][y]
        if v == '':  # polje je zaprto
            self.zaprta_polja.remove((x, y))
            if m:
                self.matrika[x][y] = 'f'
                self.zastave.add((x, y))
                self.preostale_mine -= 1
            else:
                self.matrika[x][y] = 'e'  # 'e' bo oznaceval odprto polje, katerega vrednost ne poznamo
                self.odprta_polja.add((x, y))

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
            self.zaprta_polja.add((x, y))