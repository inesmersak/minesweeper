# MINOLOVEC #

Minolovec je računalniška igra, pri kateri mora igralec odkriti vse mine na mreži manjših praznih polj. Ob levem kliku na polje se prikaže številka, ki označuje število min v sosednjih poljih. Igralec mora iz tega podatka logično sklepati, na katerem izmed sosednjih polj je mina, v nekaterih primerih pa mora tudi ugibati. Cilj igre je odkriti vsa polja, pod katerimi se ne skriva mina, ne bi kliknil na katero od min. Polja, za katera je igralec prepričan, da vsebujejo mino, je možno označiti z zastavico.

### Namen repozitorija ###

Repozitorij vsebuje projekt pri Programiranju 2, š. leto 2014/2015. Cilj je sprogramirati igro minolovec in umetno inteligenco, ki jo igra. Uporabljen bo Python 3.4 in module Tkinter.

### Vsebina repozitorija ###

Repozitorij vsebuje:

* `minolovec.py`: vsebuje glavni razred z mehanizmom igre in grafiko, požene igro;

* `polje.py`: vsebuje razred `Polje`, ki predstavlja en kvadratek na celotni igralni površini, in vsebuje podatke o njemu;

* `racunalnik.py`: vsebuje umetno inteligenco.

Poleg tega repozitorij vsebuje tudi datoteko `tekstovniUI.py`, kjer so shranjeni ostanki tekstovnega uporabniškega vmesnika, ki se pri igri ne uporablja več. 