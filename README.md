# ADD: modifikovateľnosť vs. výkon – experiment (Java)

Štyri implementácie tej istej cenotvornej služby: **A** (Strategy + ServiceLoader), **B** (inline),
**C** (inline jadro + jeden bod rozšírenia), **D** (pravidlá ako dáta v `rules.cfg`).

```
src/main/java/sk/add/{domain,a,b,c,d}   produkčný kód variantov
src/main/java/sk/add/harness            pomocné triedy (Orders, Variants) – nepočítajú sa do metrík
src/main/java/sk/add/bench              JMH benchmarky + syntetické pravidlá + EquivalenceCheck
src/main/java/sk/add/bench/generated    GENEROVANÉ (tools/gen_inline.py): InlineN (B), HybridN (C_stable)
docs/ADD_artefakty.md                   utility tree, ciele iterácií, taktiky, rozhodnutia
tools/metrics.py                        štruktúrne metriky + cena zmien S1–S4 (kompiluje a overuje každú zmenu)
tools/report.py                         JMH JSON -> tabuľka
```

## Spustenie (Maven, JDK 17+)

```
mvn clean package
java -cp target/classes sk.add.bench.EquivalenceCheck            # všetky varianty musia dať rovnaké ceny
java -jar target/benchmarks.jar BaselineBenchmark  -rf json -rff results_baseline.json
java -jar target/benchmarks.jar ScalingBenchmark   -rf json -rff results_scaling.json
python3 tools/report.py results_scaling.json results_baseline.json
python3 tools/metrics.py                                         # štruktúra + cena zmien
```

Extra beh: obmedzenie JIT pre veľké metódy (B a C_stable pri N = 1000):

```
java -jar target/benchmarks.jar ScalingBenchmark -p variant=B,C_stable -p n=1000 \
     -jvmArgsAppend "-XX:-DontCompileHugeMethods" -rf json -rff results_hugemethod.json
```

Pri meraní zatvorte ostatné aplikácie, nechajte stroj zapojený do siete a nič iné nespúšťajte.

## Scenáre zmeny (tools/metrics.py)

S1 nové pravidlo (BulkBonus), S2 zmena poradia (kupón pred objemovou zľavou), S3 zmena parametra (prah 100 → 50 ks),
S4 nový vstupný údaj (krajina → DPH podľa krajiny).
