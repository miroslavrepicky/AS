package sk.add.d;

import sk.add.domain.*;

public enum Field {
    QUANTITY { int of(Order o) { return o.quantity(); } int parse(String s) { return Integer.parseInt(s); } },
    MONTH { int of(Order o) { return o.month(); } int parse(String s) { return Integer.parseInt(s); } },
    TIER { int of(Order o) { return o.tier().ordinal(); } int parse(String s) { return Tier.valueOf(s).ordinal(); } };

    abstract int of(Order o);

    abstract int parse(String s);
}
