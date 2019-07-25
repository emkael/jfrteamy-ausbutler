AusButler dla pakietu JFR Teamy
===============================

Narzędzie umożliwiające obliczanie i prezentację znormalizowanego butlera (tzw. "australijskiego butlera") w turniejach prowadzonych przy użyciu pakietu JFR Teamy.

Instalacja
----------

1. Ściągnąć paczkę z programem ze [strony autora](https://github.com/emkael/jfrteamy-ausbutler/releases).
2. Rozpakować paczkę do pożądanego katalogu.
3. [Skonfigurować odpowiednie połączenie z bazą danych](#pliki-konfiguracyjne).
4. Wywołać w katalogu programu plik `butler.exe`.

Wywołanie programu
------------------

Program przyjmuje w linii poleceń, w dowolnej kolejności, szereg argumentów, odpowiadających akcjom wykonywanym przez aplikację:

 * `calculate` przelicza znormalizowanego butlera i wpisuje go do bazy danych
 * `generate` generuje strony HTML z wszystkimi obecnymi w bazie wynikami znormalizowanego butlera
 * `send` wysyła je Gońcem do serwera FTP (pod warunkiem wybrania akcji `generate`)

Wywołanie programu bez żadnego z powyższych argumentów jest równoważne podaniu wszystkich argumentów (`calculate`, `generate` i `send`).

Dodatkowo, program domyślnie czeka po wykonaniu na wciśnięcie dowolnego klawisza - opcję tę można wyłączyć, przekazując do programu argument `nowait`.

Pliki konfiguracyjne
--------------------

Aplikacja korzysta z pięciu plików konfiguracyjnych, formatu JSON, umiejscowionych w podkatalogu `config` katalogu programu.

---

[`db.json`](config/db.json.EXAMPLE)

Określa parametry połączenia z bazą danych turnieju:

 * `user` - nazwę użytkownika
 * `pass` - hasło użytkownika
 * `db` - nazwę bazy turnieju
 * `host` - serwer bazy danych

---

[`butler.json`](config/butler.json)

Definiuje parametry obliczania butlera znormalizowanego.

Butler dla pary w danym segmencie obliczany jest w następujący sposób:

 * butler danej pary ograniczany jest do wartości `cutoff_point`
 * wynik powyżej `cutoff_point` zaliczany jest jedynie w części, określonej przez `cutoff_rate` (np. domyślne: `32` i `0.1` oznacza, że zaliczane jest 10% wyniku powyżej 32 IMP)
 * tak uzyskany wynik przeliczany jest na średnią na rozdanie
 * do niego dodawana jest średnia na rozdanie pary przeciwnej (z butler nieznormalizowanego), przeskalowana o parametr `opponent_factor` (np. domyślne `0.5` oznacza, że dodawana jest połowa średniej na rozdanie przeciwników)
 * wynik przeliczany jest z powrotem na wartość w całym segmencie
 * jeśli ustawiony jest parametr `only_current`, średnia przeciwników wyliczana jest jedynie z niepóźniejszych segmentów - czyli tak wyliczony butler nie uwzględnia dla pierwszych segmentów średniej przeciwników z całych zawodów, ale wyniki dla wcześniejszych segmentów nie zmieniają się pod wpływem wyników kolejnych segmentów

Wszystkie obliczenia nie zależą od sposobu wyliczania nieznormalizowanego butlera dla wszystkich par.

W końcu, parametr `segments_in_table_limit` określa, ile segmentów najnowszych widocznych jest szczegółowo w zbiorczej tabeli znormalizowanego butlera (`PREFIXnormbutler.html`). Wszystkie wcześniejsze segmenty dołączone są w nagłówku tabeli, zgodnie z konwencją JFR Teamy.

Możliwe jest również ustawienie innej ścieżki wyjściowej niż ścieżka robocza turnieju. Odpowiada za to parametr `output_path`.

---

[`goniec.json`](config/goniec.json)

Określa standardowe parametry przesyłania plików Gońcem.

 * `enabled` włącza wysyłanie Gońcem
 * `host` i `port` wskazują lokalizację Gońca

---

[`logoh.json`](config/logoh.json)

Ustawia mapowanie łańcuchów tekstowych używanych przez aplikację w generowanych stronach na identyfikatory do pobrania tekstów z bazy danych turnieju. Przeważnie nie wymaga ingerencji.

Każdy tekst powinien znajdować się w tabeli `logoh` bazy danych turnieju.

**UWAGA**: w przypadku wystąpienia w programie błędu `KeyError: ID_TŁUMACZENIA` w liniach wskazujących na pobieranie tłumaczeń, należy do bazy danych turnieju w JFR Teamy wczytać ponownie poprawny plik `.language`.

---

[`translation.json`](config/translation.json)

Ustawia teksty tłumaczeń, używane w stronach generowanych przez program, a niezawarte domyślnie w bazach turniejów JFR Teamy.

Składa się ze słownika wartości określających polską (`pl`) i angielską (`en`) formę łańcucha tekstowego.

Program wykrywa wersję językową ustawioną w bazie danych turnieju na podstawie obecnego w bazie danych łańcucha o ID 18 (`ROUND` po angielsku, `RUNDA` po polsku).

Szablony stron
--------------

Katalog `template` zawiera w pełni modyfikowalne szablony stron generowanych przez program.

 * [`table.html`](template/table.html) to szablon tabeli zbiorczej znormalizowanego butlera - pliku `PREFIXnormbutler.html`
 * [`frame.html`](template/frame.html) to szablon ramki wyświetlającej wyniki znormalizowanego butlera pojedynczego segmentu - plików `PREFIXbutlerSEGMENT.htm`
 * [`segment.html`](template/segment.html) to szablon tabeli wyników znormalizowanego butlera dla poszczególnych par w pojedynczym segmencie - plików `PREFIXbutlerSEGMENT.html`
 * [`macros.html`](template/macros.html) zawiera szablony wstawek używanych w różnych miejscach innych szablonów - nagłówków, separatorów, wierszy tabeli wyników czy stopki stron

W większości przypadków użycia nie ma potrzeby modyfikowania tych szablonów - są one zgodne z formatowaniem JFR Teamy.

Autorzy
-------

Autorem programu jest Michał Klichowicz (mkl).

Program powstał na potrzeby Polskiego Związku Brydża Sportowego, za namową kapitana reprezentacji Polski open, Piotra Walczaka.

Metoda jest adaptacją znormalizowanego butlera obliczanego w rozgrywkach Australijskiej Federacji Brydżowej, wg opisu z [Mistrzostw Australii 2016](http://www.abfevents.com.au/events/spnot/2016/include/2016_SN_Supp_Regs.pdf).

Licencja
--------

Aplikacja udostępniana jest na [uproszczonej, 2-punktowej licencji BSD](LICENSE).

---

`Breathe on, little sister, breathe on.`
