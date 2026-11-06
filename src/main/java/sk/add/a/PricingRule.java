package sk.add.a;

import sk.add.domain.Order;

public interface PricingRule {
    double apply(Order order, double price);

    default int priority() {
        return 100;
    }
}
