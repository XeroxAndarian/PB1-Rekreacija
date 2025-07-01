# PB1-Rekreacija
Seminarska naloga pri predmetu Podatkovne Baze 1



### Opis strukture baze
Podatki bodo razdeljeni v pet (5) tabel:
1. Tabela **Igralec** bo vsebovala osebne podatke o posameznem udeležencu rekreacije za katerega se beleži statistika. Atributi bodo *id*, *ime* in *priimek*.
2. Tabela **Tekma** bo vsebovala arhiv tekem. Atributi bodo *id* (id tekme),  *datum*, *goli_a* (goli ekipe A) in *goli_b* (goli ekipe B). Tabeli 1 in 2 bosta povezani preko povezovalne tabele 3.
3. Tabela **Prisotnost** bo povezovalna tabela in bo beležila, kdaj je igralec bil na tekmi in kakšno statistiko si je priigral. Atributi bodo *id*, *igralec_id*, *tekma_id*, *ekipa*, *goli*, *asistence*, *avto_goli*.
4. Tabela **Sezona** bo hranila podatke o začetkih in koncih sezon. Vsako šolsko leto je namreč razdeljeno na dve sezoni (okvirno september - januar in februar - junij). Atributi te tabele bodo *id* (id sezone), *sezona*, *začetek*, *konec*. Tabeli 3 in 4 sta povezani preko datuma. In sicer povezavi tipa *1:n*. Vsaka tekma pripada natanko eni sezoni, ena sezona pa ima vsaj 1 tekmo.
5. Tabela **Vzdevek** bo vsebovala vzdevke igralcev. Atributi bodo *id*, *igralec_id* in *vzdevek*. En igralec ima lahko več vzdevkov.


![image](https://github.com/user-attachments/assets/d6c4addf-0f63-4d3d-85fa-cbcb5b30d510)
