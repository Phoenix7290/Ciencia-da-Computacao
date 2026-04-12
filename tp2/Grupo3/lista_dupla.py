class Node:
    def __init__(self, content: str):
        self.content = content
        self.prev    = None
        self.next    = None

    def __repr__(self):
        return f'Node("{self.content}")'

class DoublyLinkedList:
    def __init__(self):
        self.head    = None
        self.tail    = None
        self.current = None
        self.size    = 0

    def append(self, content: str) -> Node:
        new_node = Node(content)

        if self.head is None:
            self.head    = new_node
            self.tail    = new_node
            self.current = new_node
        else:
            new_node.prev  = self.tail
            self.tail.next = new_node
            self.tail      = new_node
            self.current   = new_node

        self.size += 1
        return new_node

    def insert_after(self, target_node: Node, content: str) -> Node:
        if target_node is None:
            return self.append(content)

        new_node  = Node(content)
        successor = target_node.next

        new_node.prev      = target_node
        new_node.next      = successor

        target_node.next   = new_node

        if successor is not None:
            successor.prev = new_node
        else:
            self.tail = new_node

        self.current = new_node
        self.size   += 1
        return new_node

    def delete(self, target_node: Node) -> None:
        if target_node is None:
            return

        predecessor = target_node.prev
        successor   = target_node.next

        if predecessor is not None:
            predecessor.next = successor
        else:
            self.head = successor

        if successor is not None:
            successor.prev = predecessor
        else:
            self.tail = predecessor

        if predecessor is not None:
            self.current = predecessor
        else:
            self.current = successor

        target_node.prev = None
        target_node.next = None

        self.size -= 1

    def get_node(self, position: int) -> Node | None:
        if position < 1 or position > self.size:
            return None

        current_node = self.head
        for _ in range(position - 1):
            current_node = current_node.next

        return current_node

    def display(self, start: int = 1, end: int = None) -> None:
        if self.head is None:
            print("  (documento vazio)")
            return

        if end is None:
            end = self.size

        node    = self.get_node(start)
        line_no = start

        print(f"  {'Nº':<4}  {'Conteúdo'}")
        print(f"  {'-'*4}  {'-'*40}")

        while node is not None and line_no <= end:
            marker = " ←C" if node is self.current else ""
            print(f"  {line_no:<4}  {node.content}{marker}")
            node    = node.next
            line_no += 1

    def display_structure(self) -> None:
        if self.head is None:
            print("  (lista vazia)")
            return

        print(f"\n  P ──► ", end="")

        node     = self.head
        position = 1

        while node is not None:
            is_head    = (node is self.head)
            is_current = (node is self.current)

            prefix = "╔" if is_head else "║"
            suffix = "╗" if is_head else "║"

            print(f"[{prefix} {node.content[:28]:<28} {suffix}]", end="")

            if is_current:
                print(f"  ◄── C (linha corrente)", end="")

            print()

            if node.next is not None:
                print(f"           {'↑↓':>5}")

            node     = node.next
            position += 1

        print()

def main():
    print("=" * 60)
    print("  Lista Duplamente Encadeada — Editor de Linhas")
    print("=" * 60)

    print("\n[1] Construindo o texto do enunciado...\n")

    text = DoublyLinkedList()
    text.append('"A natureza,')
    text.append("dizem-nos,")
    text.append('É apenas o hábito..."')
    text.append("(Rousseau)")

    print("[2] Estrutura de ponteiros (P = primeira linha, C = corrente):")
    text.display_structure()

    print("[3] Texto completo:")
    text.display()

    print("\n[4] Inserindo 'boa amiga,' após a linha 2...")
    node2 = text.get_node(2)
    text.insert_after(node2, "boa amiga,")

    print("\n  Texto após inserção:")
    text.display()
    print()
    text.display_structure()

    print("[5] Removendo a linha 3 ('boa amiga,')...")
    node3 = text.get_node(3)
    text.delete(node3)

    print("\n  Texto após remoção:")
    text.display()

    print("\n[6] Navegação pelos ponteiros:")
    node = text.head
    print(f"  head.content          = \"{node.content}\"")
    print(f"  head.next.content     = \"{node.next.content}\"")
    print(f"  head.next.prev        = head? {node.next.prev is node}")
    print(f"  tail.content          = \"{text.tail.content}\"")
    print(f"  tail.prev.content     = \"{text.tail.prev.content}\"")
    print(f"  current.content       = \"{text.current.content}\"")

    print("\n" + "=" * 60)
    print("  Demonstração concluída.")
    print("=" * 60)


if __name__ == "__main__":
    main()