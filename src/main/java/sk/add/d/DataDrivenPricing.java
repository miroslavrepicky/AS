package sk.add.d;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.Comparator;
import java.util.List;

import sk.add.domain.Money;
import sk.add.domain.Order;
import sk.add.domain.PriceCalculator;

public final class DataDrivenPricing implements PriceCalculator {
    private final RuleSpec[] rules;

    public DataDrivenPricing(List<RuleSpec> specs) {
        this.rules = specs.stream()
                .sorted(Comparator.comparingInt(RuleSpec::priority))
                .toArray(RuleSpec[]::new);
    }

    public static DataDrivenPricing fromResource(String path) {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(
                DataDrivenPricing.class.getResourceAsStream(path), StandardCharsets.UTF_8))) {
            return new DataDrivenPricing(RuleParser.parse(in));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public double calculate(Order order) {
        double price = order.base();
        for (RuleSpec rule : rules) {
            price = rule.apply(order, price);
        }
        return Money.round(price);
    }
}
