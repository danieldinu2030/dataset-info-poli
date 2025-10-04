# Dataset Probleme Admitere Informatică Politehnica

Problemele din setul de date sunt scrise integral în **LaTeX**, conținând enunțuri, câte 6 variante de răspuns, soluția și rezolvarea, dezvoltată în funcție de caz.
Pentru compilarea părților din set, este necesară includerea următoarelor pachete:

```c
\usepackage{graphicx}            % pentru \includegraphics
\usepackage{amsmath}             % pentru \text, align
\usepackage{array}               % pentru array
\usepackage[normalem]{ulem}      % pentru \sout
```

## Surse

- Culegerea oficială a UPB cu probleme pentru admiterea la informatică, ediția 2020:
    - 46 de variante a câte 15 probleme
    - **Total**: 690 probleme

- Chestionarele de concurs date la admiteri, simulări și/sau preadmiteri:
    > De adăugat pe viitor, odată ce există rezolvări publice complete

## Conținut

- Pentru culegerea de probleme:
    - Fișiere LaTeX provenite din culegerea de probleme scanată, editate și formatate pe linii
    - Fișiere `.csv` intermediare pentru enunțuri, răspunsuri și rezolvări
    - Fișiere `.csv` finale care reunesc toate informațiile problemelor
    - Script-uri Python și Shell utilizate pentru prelucrarea fișierelor

> A se edita după caz, este un template preluat de la dataset-ul pentru fizică (https://github.com/danieldinu2030/dataset-fizica-poli)

- Pentru subiectele de admitere:
    - Fișiere LaTeX provenite din PDF-urile scanate, editate și formatate pe linii
    - Fișiere `.csv` finale care reunesc toate informațiile problemelor
    - Script-uri Python utilizate pentru prelucrarea fișierelor
