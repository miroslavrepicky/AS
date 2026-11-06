package sk.add.b;

import sk.add.domain.Money;
import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;

public final class InlinePricing implements PriceCalculator {
    @Override
    public double calculate(Order o) {
        double p = o.base();
        int q = o.quantity();
        if (q >= 100) p *= 0.90; else if (q >= 10) p *= 0.95;
        if (o.month() >= 11) p *= 0.92;
        switch (o.tier()) { case GOLD -> p = Math.max(0, p - 5); case SILVER -> p = Math.max(0, p - 2); default -> { } }
        p *= 1.20;
        return Money.round(p);
    }
}
