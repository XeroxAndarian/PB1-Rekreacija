# PB1-Rekreacija
Seminarska naloga pri predmetu Podatkovne Baze 1



### Opis strukture baze
Podatki bodo razdeljeni v štiri (4) tabele:
1. Tabela **Igralec** bo vsebovala osebne podatke o posameznem udeležencu rekreacije za katerega se beleži statistika. Atributi bodo *id*, *ime*, *vzdevek* in *finance*. V spošnem bi tu prišel še *priimek* a v sklopu te seminarske za voljo vsaj delne anonimnosti udeležnecev ta podatek ne bo prisoten.
2. Tabela **Tekma** bo vsebovala arhiv tekem. Atributi bodo *id* (id tekme), *goli_a* (goli ekipe A), *goli_b* (goli ekipe B) ter *datum*. Tabeli 1 in 2 bosta povezani preko povezovalne tabele 3.
3. Tabela **Prisotnost** bo povezovalna tabela in bo beležila, kdaj je igralec bil na tekmi in kakšno statistiko si je priigral. Atributi bodo *id_igralca*, *id_tekme*, *ekipa*, *goli*, *asistence*, *avtogoli*.
4. Tabela **Sezona** bo hranila podatke o začetkih in koncih sezon. Vsako šolsko leto je namreč razdeljeno na dve sezoni (okvirno september - januar in februar - junij). Atributi te tabele *id* (id sezone), *začetek*, *konec*. Tabeli 3 in 4 sta povezani preko datuma. In sicer povezavi tipa *1:n*. Vsaka tekma pripada natanko eni sezoni, ena sezona pa ima vsaj 1 tekmo.


![image](https://github.com/user-attachments/assets/d6c4addf-0f63-4d3d-85fa-cbcb5b30d510)
