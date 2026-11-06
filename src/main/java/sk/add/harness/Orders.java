package sk.add.harness;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import sk.add.domain.*;

/** Test/benchmark helper - not part of any variant. */
public final class Orders {
    private Orders() { }

    public static Order create(int q, double p, Tier t, int m) { return new Order(q, p, t, m); }

    public static List<Order> random(int count, long seed) {
        Random r = new Random(seed);
        Tier[] tiers = Tier.values();
        List<Order> out = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            out.add(create(1 + r.nextInt(1000), Math.round(r.nextDouble() * 9900 + 100) / 100.0,
                    tiers[r.nextInt(tiers.length)], 1 + r.nextInt(12)));
        }
        return out;
    }
}
