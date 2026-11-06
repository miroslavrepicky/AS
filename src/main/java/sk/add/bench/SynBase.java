package sk.add.bench;

import sk.add.a.PricingRule;

/** Synthetic rule "if quantity > threshold(i) then price *= 0.9999". */
abstract class SynBase implements PricingRule {
    final int threshold;
    final int prio;

    SynBase(int index) {
        this.threshold = BenchFactory.threshold(index);
        this.prio = index;
    }

    @Override
    public int priority() {
        return prio;
    }
}
