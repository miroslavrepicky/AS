# ADD 3.0 – artefakty pre cenotvornú službu (koncept)

> Koncept pre sekciu „Návrh variantov“. Názvy taktík a krokov si overte voči Bass, Clements, Kazman:
> *Software Architecture in Practice* (4. vyd.) a Cervantes, Kazman: *Designing Software Architectures*.
> Hodnoty „riziko po meraní“ doplňte až z vašich vlastných výsledkov.

## Krok 1 – Review inputs

**Účel systému:** služba vypočíta konečnú cenu objednávky z množstva, jednotkovej ceny, vernostnej úrovne a mesiaca.

**Primárna funkcionalita:** `calculate(Order) -> cena` (objemová zľava, sezónna zľava, vernostný kupón, DPH).

**Obmedzenia:** Java 17, jedna služba (jeden proces), pravidlá sa menia častejšie ako zvyšok systému.

### Scenáre kvality a utility tree

Priorita = (dôležitosť pre stakeholderov, technické riziko), škála H/M/L.

| ID | Atribút | Scenár | Miera | (dôležitosť, riziko) pred meraním |
|----|---------|--------|-------|------|
| QA-1 | Modifikovateľnosť | Biznis analytik žiada nové cenové pravidlo | pridanie bez zásahu do existujúceho kódu (0 zmenených riadkov), odozva výpočtu < 50 ms | (H, M) |
| QA-2 | Výkon | Checkout volá výpočet ceny pri bežnej záťaži | latencia p99 < 50 ms pri N ≤ 1 000 pravidlách | (H, M) |
| QA-3 | Modifikovateľnosť | Zmena poradia pravidiel (kupón pred objemovou zľavou) | počet zmenených súborov a riadkov | (M, M) |
| QA-4 | Modifikovateľnosť | Zmena parametra existujúceho pravidla (prah 100 → 50 ks) | počet zmenených súborov a riadkov | (M, L) |
| QA-5 | Modifikovateľnosť | Nový vstupný údaj (krajina → DPH podľa krajiny) | počet zmenených súborov a riadkov | (M, H) |

```
Utility
├── Modifikovateľnosť
│   ├── pridať pravidlo ........... QA-1 (H, M)
│   ├── zmeniť poradie ............ QA-3 (M, M)
│   ├── zmeniť parameter .......... QA-4 (M, L)
│   └── nový vstupný údaj ......... QA-5 (M, H)
└── Výkon
    └── latencia výpočtu .......... QA-2 (H, M)
```

> Poznámka k metóde: riziko QA-2 sa po meraní zníži (v Pythone aj v Jave je latencia rádovo mikrosekundy až
> stovky mikrosekúnd). Toto prehodnotenie je výsledok experimentu, nie vstup – do eseje ho dajte do Interpretácie.

## Krok 2 – Cieľ iterácie (rozdiel medzi variantmi je práve tu)

| Var. | Cieľ iterácie (poradie driverov) | Ako sa líši priorita |
|------|-----------------------------------|----------------------|
| A | QA-1, QA-3, QA-5 > QA-2 | modifikovateľnosť má prednosť, výkon je „len“ obmedzenie |
| B | QA-2 > QA-1, QA-3 | výkon má prednosť, modifikovateľnosť sa akceptuje na úrovni „upravím jeden súbor“ |
| C | QA-1 ≈ QA-2 | modifikovateľnosť len v jednom bode rozšírenia, jadro je inline |
| D | QA-1, QA-3, QA-4 pre ne-vývojárov | pravidlá menia dáta (konfigurácia), nie kód |

## Kroky 3–5 – Prvky, návrhové koncepty, rozhrania

Jediný prvok k rozpracovaniu: **PriceService** (modul na výpočet ceny). Návrhové koncepty (taktiky):

| Var. | Taktika modifikovateľnosti / výkonu | Realizácia v kóde |
|------|--------------------------------------|-------------------|
| A | zníženie väzby: sprostredkovateľ + polymorfizmus; odloženie väzby: registrácia za behu | rozhranie `PricingRule`, `ServiceLoader` (`META-INF/services`) |
| B | výkon: zníženie réžie (bez sprostredkovateľov) | všetko v jednej metóde `InlinePricing.calculate` |
| C | zapuzdrenie + obmedzenie závislostí; jadro inline kvôli výkonu | `HybridPricing` + jediný bod `Extensions.ADJUSTERS` |
| D | odloženie väzby: konfiguračný súbor | `rules.cfg` + interpreter (`RuleSpec`, `Field`, `Op`, `Action`) |

## Krok 6 – Záznam rozhodnutí

| Rozhodnutie | Alternatívy | Dôvod | Dôsledok (nameraný) |
|-------------|-------------|-------|----------------------|
| A: pravidlá ako objekty cez ServiceLoader | rovnaké cez ručný zoznam | pridanie pravidla = nová trieda | doplniť z S1 |
| B: všetko inline | A, C, D | minimálna réžia | doplniť z S1–S4 a z limitu veľkosti metódy v JIT |
| C: jeden bod rozšírenia | viac bodov | zachovať jednoduchosť jadra | doplniť zo S2 (poradie cez hranicu jadra) |
| D: pravidlá ako dáta | A | zmena bez kompilácie | doplniť zo S3, S4 |

## Krok 7 – Analýza a overenie

Overenie scenárov QA-1…QA-5 meraním: latencia (JMH) a cena zmien (`tools/metrics.py`). Výsledky a ich interpretácia patria
do sekcií Výsledky a Interpretácia eseje.
