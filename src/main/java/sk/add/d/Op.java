package sk.add.d;

public enum Op {
    GE, EQ, BETWEEN, ALWAYS;

    boolean test(int v, int a, int b) {
        return switch (this) {
            case GE -> v >= a;
            case EQ -> v == a;
            case BETWEEN -> v >= a && v <= b;
            case ALWAYS -> true;
        };
    }
}
