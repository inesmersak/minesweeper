def simuliraj(self, level=0):
    self.izracunaj_potezo()
    if self.odpri:
        p1 = self.odpri.pop()
        self.simuliraj_potezo(p1)
        print(level * "  ", "Simuliram potezo ", p1)
        if not self.preveri_veljavnost_polja():
            print(level * "  ", "Neveljavno polje!")
            self.preklici_potezo(p1)
            return NEVELJAVNO
        p2 = self.simuliraj(level + 1)
        print(level * "  ", "Našel rešitev ", p2)
        self.preklici_potezo(p1)
        return p2
    else:
        rob = self.doloci_rob()
        if not rob:
            print(level * "  ", "Ni več roba!")
            return NEVEM
        (x, y) = random.choice(rob)
        p1 = (x, y, True)
        self.simuliraj_potezo(p1)
        if not self.preveri_veljavnost_polja():
            print(level * "  ", "Neveljavno polje takoj po predpostavki ", p1)
            self.preklici_potezo(p1)
            return (x, y, False)
        print(level * "  ", "Predpostavljam zastavo ", p1)
        p2 = self.simuliraj(level + 1)
        print(level * "  ", "Našel rešitev2 ", p2)
        self.preklici_potezo(p1)
        if p2 == NEVELJAVNO:
            return (x, y, False)
        elif p2 == NEVEM:
            return p2
        if level == 0:
            print(level * "  ", "Level je 0!")
            return p2
        else:
            print(level * "  ", "Obračam predpostavko...")
            self.simuliraj_potezo(p2)
            if not self.preveri_veljavnost_polja():
                print(level * "  ", "Obrnjena predpostavka povzroči neveljavno polje")
                self.preklici_potezo(p2)
                return NEVELJAVNO
            p3 = self.simuliraj(level + 1)
            print(level * "  ", "Našel rešitev3 ", p3)
            self.preklici_potezo(p2)
            return p3
