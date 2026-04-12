import os
import sys

class Node:
    def __init__(self, content: str):
        self.content = content
        self.prev    = None
        self.next    = None

class DoublyLinkedList:
    def __init__(self):
        self.head    = None
        self.tail    = None
        self.current = None
        self.size    = 0

    def get_node(self, position: int) -> "Node | None":
        if position < 1 or position > self.size:
            return None
        node = self.head
        for _ in range(position - 1):
            node = node.next
        return node

    def append(self, content: str) -> Node:
        new_node = Node(content)
        if self.head is None:
            self.head = self.tail = self.current = new_node
        else:
            new_node.prev  = self.tail
            self.tail.next = new_node
            self.tail      = new_node
            self.current   = new_node
        self.size += 1
        return new_node

    def insert_after(self, target_node: "Node | None", content: str) -> Node:
        if target_node is None or target_node is self.tail:
            return self.append(content)

        new_node  = Node(content)
        successor = target_node.next

        new_node.prev    = target_node
        new_node.next    = successor
        target_node.next = new_node
        if successor:
            successor.prev = new_node

        self.current = new_node
        self.size   += 1
        return new_node

    def delete(self, target_node: Node) -> None:
        if target_node is None:
            return

        predecessor = target_node.prev
        successor   = target_node.next

        if predecessor:
            predecessor.next = successor
        else:
            self.head = successor

        if successor:
            successor.prev = predecessor
        else:
            self.tail = predecessor

        # Move o cursor para o vizinho mais próximo
        self.current = predecessor if predecessor else successor

        target_node.prev = target_node.next = None
        self.size -= 1

class TextEditor:
    def __init__(self):
        self.doc = DoublyLinkedList()

    def _current_position(self) -> int:
        if self.doc.current is None:
            return 0
        node     = self.doc.head
        position = 1
        while node is not None and node is not self.doc.current:
            node     = node.next
            position += 1
        return position

    def _clamp(self, value: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(value, max_val))

    def _parse_int(self, token: str, default: int) -> int:
        try:
            return int(token.strip())
        except (ValueError, AttributeError):
            return default

    def cmd_insert(self, args: str) -> None:
        current_pos = self._current_position()
        after_pos   = self._parse_int(args, current_pos) if args.strip() else current_pos
        after_pos   = self._clamp(after_pos, 0, self.doc.size)

        after_node = self.doc.get_node(after_pos) if after_pos > 0 else None

        print("  [Modo inserção — linha em branco para encerrar]")

        insert_count = 0
        while True:
            try:
                line = input("  > ")
            except EOFError:
                break

            if line == "":
                break

            after_node = self.doc.insert_after(after_node, line)
            insert_count += 1

        print(f"  {insert_count} linha(s) inserida(s).")

    def cmd_delete(self, args: str) -> None:
        if self.doc.size == 0:
            print("  Documento vazio.")
            return

        current_pos = self._current_position()

        if not args.strip():
            start = end = current_pos
        else:
            parts = args.split(",")
            start = self._parse_int(parts[0], current_pos)
            end   = self._parse_int(parts[1] if len(parts) > 1 else "", start)

        start = self._clamp(start, 1, self.doc.size)
        end   = self._clamp(end,   1, self.doc.size)
        if start > end:
            start, end = end, start

        nodes_to_delete = []
        node = self.doc.get_node(start)
        for _ in range(end - start + 1):
            if node is None:
                break
            nodes_to_delete.append(node)
            node = node.next

        for n in nodes_to_delete:
            self.doc.delete(n)

        print(f"  {len(nodes_to_delete)} linha(s) excluída(s) (linhas {start}–{end}).")

    def cmd_duplicate(self, args: str) -> None:
        if self.doc.size == 0:
            print("  Documento vazio.")
            return

        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 3:
            print("  Uso: D <i>,<f>,<p>")
            return

        start    = self._clamp(self._parse_int(parts[0], 1), 1, self.doc.size)
        end      = self._clamp(self._parse_int(parts[1], start), 1, self.doc.size)
        dest_pos = self._clamp(self._parse_int(parts[2], self.doc.size), 0, self.doc.size)

        if start > end:
            start, end = end, start

        block_contents = []
        node = self.doc.get_node(start)
        for _ in range(end - start + 1):
            if node is None:
                break
            block_contents.append(node.content)
            node = node.next

        insert_after_node = self.doc.get_node(dest_pos) if dest_pos > 0 else None
        for content in block_contents:
            insert_after_node = self.doc.insert_after(insert_after_node, content)

        print(f"  Bloco linhas {start}–{end} duplicado após a linha {dest_pos} "
              f"({len(block_contents)} linha(s) inserida(s)).")

    def cmd_list(self, args: str) -> None:
        if self.doc.size == 0:
            print("  Documento vazio.")
            return

        if not args.strip():
            start = 1
            end   = self.doc.size
        else:
            parts = args.split(",")
            start = self._parse_int(parts[0], 1)
            end   = self._parse_int(parts[1] if len(parts) > 1 else "", self.doc.size)

        start = self._clamp(start, 1, self.doc.size)
        end   = self._clamp(end,   1, self.doc.size)
        if start > end:
            start, end = end, start

        current_pos = self._current_position()

        print(f"\n  {'Nº':<5} {'Conteúdo'}")
        print(f"  {'─'*5} {'─'*45}")

        node    = self.doc.get_node(start)
        line_no = start
        while node is not None and line_no <= end:
            marker = " ◄ corrente" if line_no == current_pos else ""
            print(f"  {line_no:<5} {node.content}{marker}")
            node    = node.next
            line_no += 1

        print(f"  {'─'*5} {'─'*45}")
        print(f"  Total exibido: {end - start + 1} linha(s) "
              f"| Documento: {self.doc.size} linha(s)\n")

    def cmd_load(self, args: str) -> None:
        parts    = args.split(",", 1)
        filename = parts[0].strip()
        current_pos = self._current_position()
        after_pos   = self._parse_int(parts[1] if len(parts) > 1 else "", current_pos)
        after_pos   = self._clamp(after_pos, 0, self.doc.size)

        if not filename:
            print("  Nome de arquivo não fornecido.")
            return

        if not os.path.isfile(filename):
            print(f"  Arquivo '{filename}' não encontrado.")
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            print(f"  Erro ao abrir '{filename}': {e}")
            return

        after_node = self.doc.get_node(after_pos) if after_pos > 0 else None
        for line in lines:
            after_node = self.doc.insert_after(after_node, line)

        print(f"  {len(lines)} linha(s) carregada(s) de '{filename}' "
              f"após a linha {after_pos}.")

    def cmd_save(self, args: str) -> None:
        parts    = args.split(",", 2)
        filename = parts[0].strip()

        if not filename:
            print("  Nome de arquivo não fornecido.")
            return

        if self.doc.size == 0:
            print("  Documento vazio — nada a salvar.")
            return

        start = self._parse_int(parts[1] if len(parts) > 1 else "", 1)
        end   = self._parse_int(parts[2] if len(parts) > 2 else "", self.doc.size)
        start = self._clamp(start, 1, self.doc.size)
        end   = self._clamp(end,   1, self.doc.size)
        if start > end:
            start, end = end, start

        lines_to_save = []
        node    = self.doc.get_node(start)
        line_no = start
        while node is not None and line_no <= end:
            lines_to_save.append(node.content)
            node    = node.next
            line_no += 1

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines_to_save) + "\n")
            print(f"  {len(lines_to_save)} linha(s) salva(s) em '{filename}'.")
        except OSError as e:
            print(f"  Erro ao salvar '{filename}': {e}")

    def cmd_alter(self, args: str) -> None:
        if self.doc.size == 0:
            print("  Documento vazio.")
            return

        current_pos = self._current_position()
        line_no     = self._parse_int(args, current_pos)
        line_no     = self._clamp(line_no, 1, self.doc.size)

        node = self.doc.get_node(line_no)
        if node is None:
            print(f"  Linha {line_no} não existe.")
            return

        print(f"  Linha {line_no} atual : {node.content}")
        try:
            new_content = input("  Novo conteúdo       : ")
        except EOFError:
            return

        node.content     = new_content
        self.doc.current = node
        print(f"  Linha {line_no} alterada.")

    def run(self) -> None:
        print("=" * 60)
        print("  Editor de Textos — Lista Duplamente Encadeada")
        print("=" * 60)
        print("  Comandos: I, E, D, L, C, S, A, F")
        print("  Digite F para sair.\n")

        dispatch = {
            "I": self.cmd_insert,
            "E": self.cmd_delete,
            "D": self.cmd_duplicate,
            "L": self.cmd_list,
            "C": self.cmd_load,
            "S": self.cmd_save,
            "A": self.cmd_alter,
        }

        while True:
            current_pos = self._current_position()
            prompt      = f"[linha {current_pos}/{self.doc.size}] > "

            try:
                raw = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Encerrando.")
                break

            if not raw:
                continue

            command = raw[0].upper()
            args    = raw[1:].strip()

            if command == "F":
                print("  Editor encerrado.")
                break

            if command in dispatch:
                dispatch[command](args)
            else:
                print(f"  Comando desconhecido: '{command}'")
                print("  Comandos válidos: I, E, D, L, C, S, A, F")

if __name__ == "__main__":
    editor = TextEditor()
    editor.run()