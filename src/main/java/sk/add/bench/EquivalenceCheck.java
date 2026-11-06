package sk.add.bench;

import java.util.List;

import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;
import sk.add.harness.Orders;
import sk.add.harness.Variants;

/** Sanity check: all variants must return the same prices. Run before benchmarking. */
public final class EquivalenceCheck {
    public static void main(String[] args) {
        List<Order> orders = Orders.random(5000, 1);
        PriceCalculator ref = Variants.baseline("B");
        for (String v : new String[] {"A", "C", "D"}) {
            PriceCalculator c = Variants.baseline(v);
            for (Order o : orders) check("baseline " + v, ref.calculate(o), c.calculate(o), o);
        }
        System.out.println("OK baseline: A, B, C, D agree on " + orders.size() + " orders");
        for (int n : new int[] {4, 10, 100, 1000}) {
            PriceCalculator base = BenchFactory.create("B", n);
            for (String v : new String[] {"A", "A8", "C_naive", "C_stable", "D"}) {
                PriceCalculator c = BenchFactory.create(v, n);
                for (Order o : orders) check(v + " n=" + n, base.calculate(o), c.calculate(o), o);
            }
        }
        System.out.println("OK synthetic: A, A8, B, C_naive, C_stable, D agree for n = 4, 10, 100, 1000");
    }

    private static void check(String what, double expected, double actual, Order o) {
        if (Math.abs(expected - actual) > 1e-9) {
            throw new AssertionError(what + ": expected " + expected + " but got " + actual + " for " + o);
        }
    }
}
