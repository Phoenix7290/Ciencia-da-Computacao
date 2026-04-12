def calculate_size(node: dict | int, depth: int = 0) -> int:
    if isinstance(node, int):
        return node

    total = 0
    for name, content in node.items():
        child_size = calculate_size(content, depth + 1)
        total     += child_size

    return total

def print_tree(node: dict | int, name: str = ".", depth: int = 0) -> int:
    indent  = "    " * depth
    is_file = isinstance(node, int)

    if is_file:
        print(f"{indent} {name:<30} {node:>6} KB")
        return node

    total = 0
    print(f"{indent} {name}/")

    for child_name, child_content in node.items():
        child_size = print_tree(child_content, child_name, depth + 1)
        total     += child_size

    print(f"{indent}   {'─' * 35} {total:>6} KB  ← total da pasta")
    return total

file_system = {
    "Documentos": {
        "Trabalho": {
            "projeto1.pdf": 500,
            "projeto2.pdf": 300,
        },
        "Pessoal": {
            "receitas.txt": 10,
        },
    },
    "Imagens": {
        "Ferias": {
            "foto1.jpg": 2000,
            "foto2.jpg": 3000,
        },
        "logo.png": 150,
    },
    "README.txt": 5,
}

deep_file_system = {
    "Projetos": {
        "2024": {
            "Q1": {
                "relatorio.pdf": 800,
                "dados.csv":     120,
            },
            "Q2": {
                "relatorio.pdf": 950,
            },
        },
        "2025": {
            "rascunho.txt": 30,
        },
    },
    "config.ini": 2,
}

def main():
    print("=" * 60)
    print("  Questão 7 — Tamanho de Pasta por Recursão")
    print("=" * 60)

    print("\n[1] Sistema de arquivos do enunciado:\n")
    total1 = print_tree(file_system, "raiz")
    print(f"\n  Tamanho total calculado por calculate_size() : "
          f"{calculate_size(file_system)} KB")
    print(f"  Tamanho total exibido por print_tree()       : {total1} KB")
    print(f"  Conferência: {'✓ iguais' if total1 == calculate_size(file_system) else '✗ divergem'}")

    print("\n" + "─" * 60)
    print("\n[2] Sistema com maior profundidade de aninhamento:\n")
    total2 = print_tree(deep_file_system, "raiz")
    print(f"\n  Tamanho total: {calculate_size(deep_file_system)} KB")

    print("\n" + "─" * 60)
    print("\n[3] Casos extremos:\n")

    empty_folder = {}
    print(f"  Pasta vazia             → {calculate_size(empty_folder)} KB")

    single_file = {"unico.txt": 42}
    print(f"  Pasta com 1 arquivo     → {calculate_size(single_file)} KB")

    flat_folder = {"a.txt": 10, "b.txt": 20, "c.txt": 30}
    print(f"  Pasta sem subpastas     → {calculate_size(flat_folder)} KB")

    print("\n" + "=" * 60)
    print("  Demonstração concluída.")
    print("=" * 60)


if __name__ == "__main__":
    main()