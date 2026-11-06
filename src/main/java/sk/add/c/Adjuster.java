package sk.add.c;

import sk.add.domain.Order;

@FunctionalInterface
public interface Adjuster {
    double adjust(Order order, double price);
}
