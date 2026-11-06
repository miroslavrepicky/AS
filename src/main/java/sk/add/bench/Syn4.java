package sk.add.bench;

import sk.add.domain.Order;

final class Syn4 extends SynBase {
    Syn4(int index) { super(index); }

    @Override
    public double apply(Order o, double p) {
        return o.quantity() > threshold ? p * 0.9999 : p;
    }
}
