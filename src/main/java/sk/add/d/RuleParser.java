package sk.add.d;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public final class RuleParser {
    private RuleParser() { }

    /** Line format: priority FIELD OP a b ACTION amount   ('-' = unused, '#' = comment). */
    public static List<RuleSpec> parse(BufferedReader in) throws IOException {
        List<RuleSpec> rules = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            line = line.strip();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] t = line.split("\\s+");
            if (t.length != 7) throw new IllegalArgumentException("Bad rule: " + line);
            Field f = Field.valueOf(t[1]);
            rules.add(new RuleSpec(Integer.parseInt(t[0]), f, Op.valueOf(t[2]),
                    num(f, t[3]), num(f, t[4]), Action.valueOf(t[5]), Double.parseDouble(t[6])));
        }
        return rules;
    }

    private static int num(Field f, String s) {
        return s.equals("-") ? 0 : f.parse(s);
    }
}
