# def posodobi(self, x, y, m):
# """ Sprejme koordinate, kamor je kliknil uporabnik, in ali je oznacil mino ali ne ter posodobi igro,
#     tako da odpre polja oziroma oznaci mino. """
#     if m:
#         ozn = self.polje[x][y].oznaci()
#         if ozn:
#             self.preostale_mine -= 1
#     else:
#         if self.polje[x][y].vrednost == 'x':
#             return False
#         else:
#             self.polje[x][y].odpri()
#             if self.polje[x][y].vrednost == 0:
#                 self.odpri_blok((x, y))
#     return True

# def igra(self):
# while True:
#         self.prikazi_celotno_polje()
#         print("Preostale mine:", self.preostale_mine)
#         v = int(input("Vrstica: ")) - 1
#         s = int(input("Stolpec: ")) - 1
#         m = input("(m)ina / (p)razno: ")
#         m = (m == 'm')
#         poteka = self.posodobi(v, s, m)
#         if not poteka:
#             self.prikazi_celotno_polje(odkrito=True)
#             print('Zal ste naleteli na mino!')
#             self.porazi += 1
#             break
#         konec = self.konec()
#         if konec:
#             self.prikazi_celotno_polje(odkrito=True)
#             if self.preostale_mine == 0:
#                 self.zmage += 1
#                 print('Zmagali ste!')
#             else:
#                 self.porazi += 1
#                 print('Izgubili ste!')
#             break