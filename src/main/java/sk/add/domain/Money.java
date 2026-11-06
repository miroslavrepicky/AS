package sk.add.domain;

public final class Money {
    private Money() { }

    public static double round(double v) {
        return Math.round(v * 100.0) / 100.0;
    }
}
