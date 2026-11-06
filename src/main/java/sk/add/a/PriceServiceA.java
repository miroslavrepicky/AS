package sk.add.a;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.ServiceLoader;

import sk.add.domain.Money;
import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;

public final class PriceServiceA implements PriceCalculator {
    private final PricingRule[] rules;

    public PriceServiceA() {
        this(loadRules());
    }

    public PriceServiceA(List<PricingRule> rules) {
        this.rules = rules.stream()
                .sorted(Comparator.comparingInt(PricingRule::priority))
                .toArray(PricingRule[]::new);
    }

    private static List<PricingRule> loadRules() {
        List<PricingRule> found = new ArrayList<>();
        ServiceLoader.load(PricingRule.class).forEach(found::add);
        return found;
    }

    @Override
    public double calculate(Order order) {
        double price = order.base();
        for (PricingRule rule : rules) {
            price = rule.apply(order, price);
        }
        return Money.round(price);
    }
}
