#!/bin/sh
# Sandbox run without Maven: short settings (1 fork, 3x1s warmup, 3x1s measurement).
cd "$(dirname "$0")/.."
DEPS=/usr/share/java/commons-math3.jar:/usr/share/java/joptsimple.jar
CP=target/classes:/tmp/jmhbuild/jmh-core.jar:$DEPS
java -cp $CP org.openjdk.jmh.Main BaselineBenchmark -f 1 -wi 3 -i 3 -w 1 -r 1 -rf json -rff results_baseline.json > jmh_baseline.log 2>&1
java -cp $CP org.openjdk.jmh.Main ScalingBenchmark -f 1 -wi 3 -i 3 -w 1 -r 1 -rf json -rff results_scaling.json > jmh_scaling.log 2>&1
echo done > bench_done.flag
