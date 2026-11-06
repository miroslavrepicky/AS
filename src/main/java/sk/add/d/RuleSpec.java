package sk.add.d;

import sk.add.domain.Order;

public record RuleSpec(int priority, Field field, Op op, int a, int b, Action action, double amount) {
    double apply(Order order, double price) {
        return op.test(field.of(order), a, b) ? action.apply(price, amount) : price;
    }
}
