package sk.add.c;

import sk.add.domain.Order;

public final class Extensions {
    private Extensions() { }

    public static double seasonal(Order o, double p) {
        return o.month() >= 11 ? p * 0.92 : p;
    }

    public static double loyalty(Order o, double p) {
        return switch (o.tier()) {
            case GOLD -> Math.max(0, p - 5);
            case SILVER -> Math.max(0, p - 2);
            default -> p;
        };
    }

    public static final Adjuster[] ADJUSTERS = { Extensions::seasonal, Extensions::loyalty };
}
