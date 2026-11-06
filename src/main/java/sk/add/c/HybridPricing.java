package sk.add.c;

import sk.add.domain.Money;
import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;

public final class HybridPricing implements PriceCalculator {
    @Override
    public double calculate(Order o) {
        double p = o.base();
        int q = o.quantity();
        if (q >= 100) p *= 0.90; else if (q >= 10) p *= 0.95;
        for (Adjuster a : Extensions.ADJUSTERS) {
            p = a.adjust(o, p);
        }
        p *= 1.20;
        return Money.round(p);
    }
}
