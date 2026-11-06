package sk.add.a.rules;

import sk.add.a.PricingRule;
import sk.add.domain.Order;

public class VolumeDiscount implements PricingRule {
    @Override
    public double apply(Order order, double price) {
        int q = order.quantity();
        if (q >= 100) return price * 0.90;
        if (q >= 10) return price * 0.95;
        return price;
    }

    @Override
    public int priority() {
        return 10;
    }
}
