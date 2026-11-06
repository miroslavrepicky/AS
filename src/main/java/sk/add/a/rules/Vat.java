package sk.add.a.rules;

import sk.add.a.PricingRule;
import sk.add.domain.Order;

public class Vat implements PricingRule {
    @Override
    public double apply(Order order, double price) {
        return price * 1.20;
    }

    @Override
    public int priority() {
        return 1000;
    }
}
