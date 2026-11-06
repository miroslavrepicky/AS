package sk.add.bench;

import java.util.ArrayList;
import java.util.List;

import sk.add.a.PriceServiceA;
import sk.add.a.PricingRule;
import sk.add.d.Action;
import sk.add.d.DataDrivenPricing;
import sk.add.d.Field;
import sk.add.d.Op;
import sk.add.d.RuleSpec;
import sk.add.domain.Money;
import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;

/**
 * Builds N synthetic rules ("if quantity > threshold(i) then price *= 0.9999") in every variant.
 * A: N rule objects (A = 1 rule class, A8 = 8 rule classes), B: N inline ifs (generated source),
 * C_naive: 2 inline rules + N-2 through the extension point, C_stable: 90 % inline + 10 % hooks (generated),
 * D: N rows interpreted from data.
 */
public final class BenchFactory {
    private BenchFactory() { }

    public static int threshold(int i) {
        return (i * 7919) % 1000 + 1;
    }

    static PricingRule rule(int i, int types) {
        return switch (i % types) {
            case 0 -> new Syn0(i);
            case 1 -> new Syn1(i);
            case 2 -> new Syn2(i);
            case 3 -> new Syn3(i);
            case 4 -> new Syn4(i);
            case 5 -> new Syn5(i);
            case 6 -> new Syn6(i);
            default -> new Syn7(i);
        };
    }

    public static PricingRule[] rules(int from, int to, int types) {
        PricingRule[] r = new PricingRule[to - from];
        for (int i = from; i < to; i++) r[i - from] = rule(i, types);
        return r;
    }

    public static PriceCalculator create(String variant, int n) {
        try {
            switch (variant) {
                case "A": return new PriceServiceA(List.of(rules(0, n, 1)));
                case "A8": return new PriceServiceA(List.of(rules(0, n, 8)));
                case "B": return (PriceCalculator) Class.forName("sk.add.bench.generated.Inline" + n)
                        .getDeclaredConstructor().newInstance();
                case "C_stable": return (PriceCalculator) Class.forName("sk.add.bench.generated.Hybrid" + n)
                        .getDeclaredConstructor().newInstance();
                case "C_naive": return new CNaive(n);
                case "D": {
                    List<RuleSpec> specs = new ArrayList<>();
                    for (int i = 0; i < n; i++) {
                        specs.add(new RuleSpec(i, Field.QUANTITY, Op.GE, threshold(i) + 1, 0, Action.MUL, 0.9999));
                    }
                    return new DataDrivenPricing(specs);
                }
                default: throw new IllegalArgumentException(variant);
            }
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException(e);
        }
    }

    /** Core with 2 inline rules, everything else goes through the single extension point. */
    static final class CNaive implements PriceCalculator {
        private final int t0 = threshold(0);
        private final int t1 = threshold(1);
        private final PricingRule[] hooks;

        CNaive(int n) {
            hooks = rules(2, n, 1);
        }

        @Override
        public double calculate(Order o) {
            double p = o.base();
            int q = o.quantity();
            if (q > t0) p *= 0.9999;
            if (q > t1) p *= 0.9999;
            for (PricingRule h : hooks) p = h.apply(o, p);
            return Money.round(p);
        }
    }
}
