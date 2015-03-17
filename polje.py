class Polje():
    def __init__(self, x, y, vrednost=0):
        self.x = x
        self.y = y
        self.vrednost = vrednost
        self.odprto = False
        self.prikaz = None
        self.flagged = False
        # self.id = None

    def __str__(self):
        return str(self.prikaz)

    def odpri(self):
        if not self.flagged and not self.odprto:
            self.prikaz = self.vrednost
            self.odprto = True
            return True
        return False

    def oznaci(self):
        if not self.odprto:
            self.prikaz = 'f' if '_' == self.prikaz else '_'
            self.flagged = True if not self.flagged else False
            return True
        return False

    # def prikaz(self): ## prikaz je metoda in spremenljivka!
    #     pass