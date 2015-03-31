class Polje():
    def __init__(self, x, y, vrednost=0):
        self.x = x
        self.y = y
        self.vrednost = vrednost
        self.odprto = False  # ali je polje odprto
        self.prikaz = ''
        self.flagged = False  # ali je polje oznaceno z zastavico

    def __str__(self):
        return str(self.prikaz)

    def odpri(self):
        if not self.flagged and not self.odprto:  # polje lahko odpremo le, ce je zaprto
            self.prikaz = self.vrednost
            self.odprto = True
            return True
        return False

    def oznaci(self):
        if not self.odprto:  # polje lahko oznacimo z zastavico / odznacimo, ce ni odprto
            self.prikaz = 'f' if '' == self.prikaz else ''
            self.flagged = True if not self.flagged else False
            return True
        return False