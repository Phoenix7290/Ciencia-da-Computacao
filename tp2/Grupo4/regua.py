def draw_ruler(low: int, high: int, length: int, marks: dict) -> None:
    if low >= high - 1:
        return

    mid          = (low + high) // 2
    marks[mid]   = length

    if length == 1:
        return

    draw_ruler(low, mid, length - 1, marks)
    draw_ruler(mid, high, length - 1, marks)

def print_ruler(order: int) -> None:
    total_points = 2 ** order
    marks        = {}

    draw_ruler(0, total_points, order, marks)

    print(f"\n  Régua de ordem {order}  —  intervalo [0 … {total_points}]")
    print(f"  Total de marcas intermediárias: {len(marks)}")
    print()

    print(f"  {'Posição':>8}  {'Comprimento':>11}  Traço")
    print(f"  {'─'*8}  {'─'*11}  {'─'*20}")

    for pos in sorted(marks):
        length = marks[pos]
        bar    = "─" * length
        print(f"  {pos:>8}  {length:>11}  {bar}")

    if order <= 5:
        print()
        print("  Visualização vertical da régua:\n")

        print(f"  0 ┤")

        for pos in sorted(marks):
            length = marks[pos]
            bar    = "─" * length
            print(f"  {pos:>2} ┤{bar}")

        print(f"  {total_points} ┤")
    else:
        print(f"\n  (visualização omitida para ordem {order} — muitas linhas)")

def main():
    print("=" * 60)
    print("  Questão 8 — Régua Recursiva de Ordem n")
    print("=" * 60)

    print_ruler(4)

    print("\n" + "─" * 60)

    print_ruler(3)

    print("\n" + "─" * 60)

    print_ruler(2)

    print("\n" + "─" * 60)

    print_ruler(1)

    print("\n" + "─" * 60)

    print_ruler(5)

    print("\n" + "=" * 60)
    print("  Demonstração concluída.")
    print("=" * 60)


if __name__ == "__main__":
    main()