#!/usr/bin/env python3
"""Structural metrics of variants A-D and cost of 4 change scenarios (S1-S4).

Usage:  python3 tools/metrics.py            (needs `javac` and `java` on PATH)

Change cost = what must be touched in PRODUCTION code (src/main/java/sk/add/{domain,a,b,c,d} + resources).
Test/benchmark helpers (harness, bench) are patched automatically and NOT counted.
Every patched copy is compiled and run against expected prices -> column 'ok'.
"""
import difflib, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JAVA = "src/main/java/sk/add"
RES = "src/main/resources"
VARIANTS = {"A": "a", "B": "b", "C": "c", "D": "d"}
PROD = ["domain", "a", "b", "c", "d"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


# ------------------------------------------------------------------ structure
def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//.*", "", src)


def structure(root, sub):
    files = []
    for d, _, fs in os.walk(os.path.join(root, JAVA, sub)):
        files += [os.path.join(d, f) for f in fs if f.endswith(".java")]
    decl = {}
    loc = classes = 0
    for p in files:
        code = strip_comments(read(p))
        loc += sum(1 for l in code.splitlines() if l.strip())
        names = re.findall(r"\b(?:class|interface|enum|record)\s+(\w+)", code)
        classes += len(names)
        decl[p] = names
    edges = set()
    for p in files:
        code = strip_comments(read(p))
        for q, names in decl.items():
            if q == p:
                continue
            for n in names:
                if re.search(r"\b%s\b" % n, code):
                    edges.add((p, n))
    return dict(files=len(files), types=classes, loc=loc, deps=len(edges))


# ------------------------------------------------------------------ patches
def edit(tree, rel, old, new, count=1):
    p = os.path.join(tree, rel)
    s = read(p)
    assert s.count(old) == count, f"{rel}: expected {count}x {old!r}, found {s.count(old)}"
    write(p, s.replace(old, new))


def add_file(tree, rel, content):
    write(os.path.join(tree, rel), content)


def j(sub, name):
    return f"{JAVA}/{sub}/{name}.java"


SERVICES = f"{RES}/META-INF/services/sk.add.a.PricingRule"
CFG = f"{RES}/rules.cfg"

COUNTRY = """package sk.add.domain;

public enum Country { SK, CZ, AT }
"""
VAT_SWITCH = "switch (o.country()) { case SK -> 1.20; case CZ -> 1.21; case AT -> 1.22; }"


def s1(tree, v):  # new rule: BulkBonus (qty >= 500 -> -3 %), applied after the voucher, before VAT
    if v == "A":
        add_file(tree, j("a/rules", "BulkBonus"), """package sk.add.a.rules;

import sk.add.a.PricingRule;
import sk.add.domain.Order;

public class BulkBonus implements PricingRule {
    @Override
    public double apply(Order order, double price) {
        return order.quantity() >= 500 ? price * 0.97 : price;
    }

    @Override
    public int priority() {
        return 35;
    }
}
""")
        edit(tree, SERVICES, "sk.add.a.rules.Vat\n", "sk.add.a.rules.Vat\nsk.add.a.rules.BulkBonus\n")
    elif v == "B":
        edit(tree, j("b", "InlinePricing"), "        p *= 1.20;\n", "        if (q >= 500) p *= 0.97;\n        p *= 1.20;\n")
    elif v == "C":
        edit(tree, j("c", "Extensions"), "    public static final Adjuster[] ADJUSTERS = { Extensions::seasonal, Extensions::loyalty };",
             "    public static double bulkBonus(Order o, double p) {\n        return o.quantity() >= 500 ? p * 0.97 : p;\n    }\n\n"
             "    public static final Adjuster[] ADJUSTERS = { Extensions::seasonal, Extensions::loyalty, Extensions::bulkBonus };")
    elif v == "D":
        edit(tree, CFG, "1000 QUANTITY ALWAYS", "35 QUANTITY GE 500 - MUL 0.97\n1000 QUANTITY ALWAYS")


def s2(tree, v):  # the loyalty voucher must be applied BEFORE the volume discount
    if v == "A":
        edit(tree, j("a/rules", "LoyaltyVoucher"), "return 30;", "return 5;")
    elif v == "B":
        sw = "        switch (o.tier()) { case GOLD -> p = Math.max(0, p - 5); case SILVER -> p = Math.max(0, p - 2); default -> { } }\n"
        edit(tree, j("b", "InlinePricing"), sw, "")
        edit(tree, j("b", "InlinePricing"), "        int q = o.quantity();\n", "        int q = o.quantity();\n" + sw)
    elif v == "C":  # loyalty lives behind the extension point, which sits AFTER the core -> core must be touched
        edit(tree, j("c", "HybridPricing"), "        int q = o.quantity();\n", "        int q = o.quantity();\n        p = Extensions.loyalty(o, p);\n")
        edit(tree, j("c", "Extensions"), "{ Extensions::seasonal, Extensions::loyalty }", "{ Extensions::seasonal }")
    elif v == "D":
        edit(tree, CFG, "30 TIER EQ GOLD", "5 TIER EQ GOLD")
        edit(tree, CFG, "31 TIER EQ SILVER", "6 TIER EQ SILVER")


def s3(tree, v):  # change an existing rule: 10 % volume discount from 50 pcs instead of 100
    if v == "A":
        edit(tree, j("a/rules", "VolumeDiscount"), "if (q >= 100)", "if (q >= 50)")
    elif v in "BC":
        edit(tree, j(v.lower(), "InlinePricing" if v == "B" else "HybridPricing"), "if (q >= 100)", "if (q >= 50)")
    elif v == "D":
        edit(tree, CFG, "QUANTITY GE 100", "QUANTITY GE 50")
        edit(tree, CFG, "BETWEEN 10 99", "BETWEEN 10 49")


def s4(tree, v):  # new input field: country, VAT depends on it (SK 20 %, CZ 21 %, AT 22 %)
    add_file(tree, j("domain", "Country"), COUNTRY)
    edit(tree, j("domain", "Order"), "int month)", "int month, Country country)")
    # harness (not counted): keep helpers compiling, add overload with an explicit country
    edit(tree, j("harness", "Orders"),
         "    public static Order create(int q, double p, Tier t, int m) { return new Order(q, p, t, m); }",
         "    public static Order create(int q, double p, Tier t, int m) { return new Order(q, p, t, m, Country.SK); }\n"
         "    public static Order create(int q, double p, Tier t, int m, Country c) { return new Order(q, p, t, m, c); }")
    if v == "A":
        edit(tree, j("a/rules", "Vat"), "return price * 1.20;", "return price * " + VAT_SWITCH.replace("o.", "order.") + ";")
    elif v == "B":
        edit(tree, j("b", "InlinePricing"), "p *= 1.20;", "p *= " + VAT_SWITCH + ";")
    elif v == "C":
        edit(tree, j("c", "HybridPricing"), "p *= 1.20;", "p *= " + VAT_SWITCH + ";")
    elif v == "D":
        edit(tree, j("d", "Field"), "TIER { int of(Order o) { return o.tier().ordinal(); } int parse(String s) { return Tier.valueOf(s).ordinal(); } };",
             "TIER { int of(Order o) { return o.tier().ordinal(); } int parse(String s) { return Tier.valueOf(s).ordinal(); } },\n"
             "    COUNTRY { int of(Order o) { return o.country().ordinal(); } int parse(String s) { return Country.valueOf(s).ordinal(); } };")
        edit(tree, CFG, "1000 QUANTITY ALWAYS - - MUL 1.20",
             "1000 COUNTRY EQ SK - MUL 1.20\n1000 COUNTRY EQ CZ - MUL 1.21\n1000 COUNTRY EQ AT - MUL 1.22")


# (name, patch, checks: [(qty, unitPrice, tier, month, country|None, expected)])
O1 = (500, 10.0, "GOLD", 3)
O2 = (20, 10.0, "SILVER", 12)
O3 = (60, 10.0, "BASIC", 3)
SCENARIOS = [
    ("S1 new rule", s1, [O1 + (None, 5232.18), O2 + (None, 207.36), O3 + (None, 684.0)]),
    ("S2 rule order", s2, [O1 + (None, 5394.6), O2 + (None, 207.66), O3 + (None, 684.0)]),
    ("S3 change rule", s3, [O1 + (None, 5394.0), O2 + (None, 207.36), O3 + (None, 648.0)]),
    ("S4 new field", s4, [O1 + ("SK", 5394.0), O1 + ("CZ", 5438.95), O1 + ("AT", 5483.9)]),
]
BASE_CHECKS = [O1 + (None, 5394.0), O2 + (None, 207.36), O3 + (None, 684.0)]


def check_source(checks):
    lines = []
    for q, p, t, m, c, exp in checks:
        make = f"Orders.create({q}, {p}, Tier.{t}, {m}" + (f", Country.{c})" if c else ")")
        lines.append(f'        check(v, "{q}/{t}/{m}/{c}", {make}, {exp});')
    return """package sk.add.harness;

import sk.add.domain.*;

public final class Check {
    static int bad = 0;

    public static void main(String[] a) {
        for (String v : new String[] {a[0]}) {
%s
        }
        System.exit(bad == 0 ? 0 : 1);
    }

    static void check(String v, String what, Order o, double expected) {
        double got = Variants.baseline(v).calculate(o);
        if (Math.abs(got - expected) > 0.005) { System.out.println("FAIL " + v + " " + what + " expected " + expected + " got " + got); bad++; }
    }
}
""" % "\n".join(lines)


def compile_and_run(tree, checks, variant):
    add_file(tree, j("harness", "Check"), check_source(checks))
    out = os.path.join(tree, "out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    srcs = [os.path.join(d, f) for sub in PROD + ["harness"] for d, _, fs in os.walk(os.path.join(tree, JAVA, sub)) for f in fs if f.endswith(".java")]
    r = subprocess.run(["javac", "--release", "17", "-d", out] + srcs, capture_output=True, text=True)
    if r.returncode:
        return False, r.stderr.strip().splitlines()[0] if r.stderr else "compile error"
    shutil.copytree(os.path.join(tree, RES), out, dirs_exist_ok=True)
    r = subprocess.run(["java", "-cp", out, "sk.add.harness.Check", variant], capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def prod_files(tree):
    out = {}
    for sub in PROD:
        for d, _, fs in os.walk(os.path.join(tree, JAVA, sub)):
            for f in fs:
                p = os.path.join(d, f)
                out[os.path.relpath(p, tree)] = read(p)
    for d, _, fs in os.walk(os.path.join(tree, RES)):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, tree)] = read(p)
    return out


def cost(scenario_patch, v, checks):
    tree = tempfile.mkdtemp()
    for part in ("src",):
        shutil.copytree(os.path.join(ROOT, part), os.path.join(tree, part),
                        ignore=shutil.ignore_patterns("bench", "generated"))
    before = prod_files(tree)
    scenario_patch(tree, v)
    after = prod_files(tree)
    new = [p for p in after if p not in before]
    mod = [p for p in after if p in before and after[p] != before[p]]
    plus = minus = 0
    for p in mod:
        for l in difflib.unified_diff(before[p].splitlines(), after[p].splitlines(), lineterm="", n=0):
            if l.startswith("+") and not l.startswith("+++"): plus += 1
            if l.startswith("-") and not l.startswith("---"): minus += 1
    new_loc = sum(1 for p in new for l in after[p].splitlines() if l.strip())
    ok, msg = compile_and_run(tree, checks, v)
    shutil.rmtree(tree, ignore_errors=True)
    return dict(new=len(new), mod=len(mod), plus=plus, minus=minus, new_loc=new_loc, ok=ok, msg=msg)


if __name__ == "__main__":
    print("== Structure (production code of each variant) ==")
    print(f"{'':3}{'files':>6}{'types':>7}{'LOC':>6}{'deps':>6}")
    for k, sub in VARIANTS.items():
        s = structure(ROOT, sub)
        print(f"{k:3}{s['files']:>6}{s['types']:>7}{s['loc']:>6}{s['deps']:>6}")

    # baseline sanity (unpatched)
    tree = tempfile.mkdtemp()
    shutil.copytree(os.path.join(ROOT, "src"), os.path.join(tree, "src"), ignore=shutil.ignore_patterns("bench", "generated"))
    res = [compile_and_run(tree, BASE_CHECKS, v) for v in VARIANTS]
    shutil.rmtree(tree, ignore_errors=True)
    print(f"\nbaseline expected prices (A,B,C,D): {'OK' if all(r[0] for r in res) else 'FAIL ' + str(res)}")

    print("\n== Cost of change: new files / modified files / changed lines in existing files (+added -removed) ==")
    print(f"{'scenario':16}{'var':>4}{'new':>5}{'mod':>5}{'+':>5}{'-':>5}{'newLOC':>8}  ok")
    for name, patch, checks in SCENARIOS:
        for v in VARIANTS:
            c = cost(patch, v, checks)
            print(f"{name:16}{v:>4}{c['new']:>5}{c['mod']:>5}{c['plus']:>5}{c['minus']:>5}{c['new_loc']:>8}  {'OK' if c['ok'] else 'FAIL ' + c['msg']}")
        print()
