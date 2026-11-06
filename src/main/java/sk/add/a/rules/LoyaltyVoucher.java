package sk.add.a.rules;

import sk.add.a.PricingRule;
import sk.add.domain.Order;

public class LoyaltyVoucher implements PricingRule {
    @Override
    public double apply(Order order, double price) {
        return switch (order.tier()) {
            case GOLD -> Math.max(0, price - 5);
            case SILVER -> Math.max(0, price - 2);
            default -> price;
        };
    }

    @Override
    public int priority() {
        return 30;
    }
}
