package sk.add.bench;

import java.util.List;
import java.util.concurrent.TimeUnit;

import org.openjdk.jmh.annotations.*;

import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;
import sk.add.harness.Orders;
import sk.add.harness.Variants;

/** The four real rules (volume, seasonal, loyalty, VAT) in A, B, C and D. */
@State(Scope.Thread)
@BenchmarkMode({Mode.AverageTime, Mode.SampleTime})
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 5, time = 1)
@Fork(2)
public class BaselineBenchmark {
    @Param({"A", "B", "C", "D"})
    String variant;

    private PriceCalculator calc;
    private Order[] orders;
    private int i;

    @Setup
    public void setup() {
        calc = Variants.baseline(variant);
        List<Order> list = Orders.random(1024, 42);
        orders = list.toArray(new Order[0]);
    }

    @Benchmark
    public double calculate() {
        return calc.calculate(orders[i++ & 1023]);
    }
}
