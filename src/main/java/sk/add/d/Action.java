package sk.add.d;

public enum Action {
    MUL, SUB;

    double apply(double price, double x) {
        return this == MUL ? price * x : Math.max(0, price - x);
    }
}
