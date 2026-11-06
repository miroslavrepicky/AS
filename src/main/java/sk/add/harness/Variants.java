package sk.add.harness;

import sk.add.a.PriceServiceA;
import sk.add.b.InlinePricing;
import sk.add.c.HybridPricing;
import sk.add.d.DataDrivenPricing;
import sk.add.domain.PriceCalculator;

public final class Variants {
    private Variants() { }

    public static PriceCalculator baseline(String name) {
        return switch (name) {
            case "A" -> new PriceServiceA();
            case "B" -> new InlinePricing();
            case "C" -> new HybridPricing();
            case "D" -> DataDrivenPricing.fromResource("/rules.cfg");
            default -> throw new IllegalArgumentException(name);
        };
    }
}
