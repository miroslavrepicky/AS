package sk.add.domain;

public record Order(int quantity, double unitPrice, Tier tier, int month) {
    public double base() {
        return quantity * unitPrice;
    }
}
