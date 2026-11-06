package sk.add.a.rules;

import sk.add.a.PricingRule;
import sk.add.domain.Order;

public class SeasonalDiscount implements PricingRule {
    @Override
    public double apply(Order order, double price) {
        return order.month() >= 11 ? price * 0.92 : price;
    }

    @Override
    public int priority() {
        return 20;
    }
}
