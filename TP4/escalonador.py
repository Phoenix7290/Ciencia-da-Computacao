import time
import random
import textwrap



QUANTUM      = 3
VELOCIDADE   = 0.15
IO_MIN       = 1
IO_MAX       = 4

random.seed(42)



class MinHeap:


    def __init__(self):
        self._data: list = []



    @staticmethod
    def _pai(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _esq(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _dir(i: int) -> int:
        return 2 * i + 2



    def _sobe(self, i: int) -> None:

        while i > 0:
            p = self._pai(i)
            if self._data[i] < self._data[p]:
                self._data[i], self._data[p] = self._data[p], self._data[i]
                i = p
            else:
                break

    def _desce(self, i: int) -> None:

        n = len(self._data)
        while True:
            menor = i
            e = self._esq(i)
            d = self._dir(i)
            if e < n and self._data[e] < self._data[menor]:
                menor = e
            if d < n and self._data[d] < self._data[menor]:
                menor = d
            if menor == i:
                break
            self._data[i], self._data[menor] = self._data[menor], self._data[i]
            i = menor



    def inserir(self, item) -> None:

        self._data.append(item)
        self._sobe(len(self._data) - 1)

    def extrair_min(self):

        if not self._data:
            raise IndexError("Heap vazia.")
        self._data[0], self._data[-1] = self._data[-1], self._data[0]
        minimo = self._data.pop()
        if self._data:
            self._desce(0)
        return minimo

    def espiar(self):

        if not self._data:
            return None
        return self._data[0]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)




class Processo:


    _contador = 0

    def __init__(self, nome: str, prioridade: int, burst_total: int):
        Processo._contador += 1
        self.pid          = Processo._contador
        self.nome         = nome
        self.prioridade   = prioridade
        self.burst_total  = burst_total
        self.burst_restante = burst_total
        self.estado       = "Nova"
        self.fatias_cpu   = 0
        self.tempo_inicio : float | None = None
        self.tempo_fim    : float | None = None


    def __lt__(self, other: "Processo") -> bool:
        return self.prioridade < other.prioridade

    def __repr__(self) -> str:
        return f"P{self.pid}({self.nome})"




class SimuladorCPU:

    def __init__(self, processos: list[Processo], quantum: int, velocidade: float):
        self.processos      = processos
        self.quantum        = quantum
        self.velocidade     = velocidade
        self.ready_queue    = MinHeap()
        self.waiting_queue  = MinHeap()
        self.em_execucao    : Processo | None = None
        self.terminados     : list[Processo]  = []
        self.log_eventos    : list[dict]      = []
        self._clock         = 0.0



    def _dormir(self, segundos_simulados: float) -> None:
        time.sleep(segundos_simulados * self.velocidade)
        self._clock += segundos_simulados

    def _registrar(self, processo: Processo, evento: str, detalhe: str = "") -> None:
        self.log_eventos.append({
            "clock"  : round(self._clock, 2),
            "pid"    : processo.pid,
            "nome"   : processo.nome,
            "estado" : processo.estado,
            "evento" : evento,
            "detalhe": detalhe,
        })
        largura = 60
        print(
            f"  [{self._clock:6.2f}s]  P{processo.pid:<2} {processo.nome:<14}"
            f"  {processo.estado:<12}  {evento}"
            + (f"  ({detalhe})" if detalhe else "")
        )

    def _atualizar_waiting(self) -> None:

        while self.waiting_queue:
            tempo_saida, proc = self.waiting_queue.espiar()
            if tempo_saida <= self._clock:
                self.waiting_queue.extrair_min()
                proc.estado = "Pronta"
                self.ready_queue.inserir((proc.prioridade, proc))
                self._registrar(proc, "E/S concluída → Pronta")
            else:
                break



    def executar(self) -> None:
        print()
        print("  SIMULADOR DE ESCALONAMENTO CPU — Round-Robin + Prioridade")
        print(f"  Quantum : {self.quantum}s   |   Processos : {len(self.processos)}")
        print()
        print(f"\n  {'[clock]':>10}  {'PID':<4} {'Nome':<14}  {'Estado':<12}  Evento\n"
              + "  " + "-" * 66)


        for proc in self.processos:
            proc.estado = "Pronta"
            self.ready_queue.inserir((proc.prioridade, proc))
            self._registrar(proc, "Nova → Pronta", f"burst={proc.burst_total}s  prio={proc.prioridade}")

        print("  " + "-" * 66)


        while self.ready_queue or self.waiting_queue or self.em_execucao:


            if self.em_execucao is None and self.ready_queue:
                _, proc = self.ready_queue.extrair_min()
                proc.estado = "Executando"
                self.em_execucao = proc
                if proc.tempo_inicio is None:
                    proc.tempo_inicio = self._clock
                self._registrar(proc, "Pronta → Executando",
                                f"burst_restante={proc.burst_restante}s")


            if self.em_execucao is None:
                if self.waiting_queue:
                    prox_evento, _ = self.waiting_queue.espiar()
                    salto = prox_evento - self._clock
                    self._dormir(max(salto, 0.01))
                    self._atualizar_waiting()
                continue


            proc = self.em_execucao
            fatia = min(self.quantum, proc.burst_restante)
            self._dormir(fatia)
            proc.burst_restante -= fatia
            proc.fatias_cpu += 1

            self._atualizar_waiting()


            if proc.burst_restante <= 0:

                proc.estado    = "Terminada"
                proc.tempo_fim = self._clock
                self.terminados.append(proc)
                self.em_execucao = None
                self._registrar(proc, "Executando → Terminada",
                                f"fatias={proc.fatias_cpu}")
            else:

                if random.random() < 0.40:
                    io_tempo = random.randint(IO_MIN, IO_MAX)
                    proc.estado = "Suspensa"
                    self.em_execucao = None
                    tempo_saida = self._clock + io_tempo
                    self.waiting_queue.inserir((tempo_saida, proc))
                    self._registrar(proc, "Executando → Suspensa",
                                    f"E/S por {io_tempo}s")
                else:

                    proc.estado = "Pronta"
                    self.em_execucao = None
                    self.ready_queue.inserir((proc.prioridade, proc))
                    self._registrar(proc, "Executando → Pronta (quantum)",
                                    f"burst_restante={proc.burst_restante}s")

        print("  " + "-" * 66)
        print(f"\n  Todos os processos concluídos.  Clock final: {self._clock:.2f}s\n")



    def imprimir_tabela(self) -> None:
        print()
        print("  TABELA DE RESULTADOS")
        print()
        cab = (
            f"  {'PID':<4} {'Nome':<14} {'Prio':>4} {'Burst':>5} "
            f"{'Fatias':>6} {'Início':>7} {'Fim':>7} {'Turnaround':>10}"
        )
        print(cab)
        print("  " + "-" * 66)
        for proc in sorted(self.terminados, key=lambda p: p.pid):
            ta = round(proc.tempo_fim - proc.tempo_inicio, 2) if proc.tempo_fim else "-"
            print(
                f"  {proc.pid:<4} {proc.nome:<14} {proc.prioridade:>4} "
                f"{proc.burst_total:>5} {proc.fatias_cpu:>6} "
                f"{proc.tempo_inicio:>7.2f} {proc.tempo_fim:>7.2f} {ta:>10}"
            )
        print("  " + "-" * 66)

        turnarounds = [
            (p.tempo_fim - p.tempo_inicio)
            for p in self.terminados if p.tempo_fim
        ]
        media_ta = sum(turnarounds) / len(turnarounds) if turnarounds else 0
        print(f"\n  Turnaround médio : {media_ta:.2f}s")
        print(f"  Processos        : {len(self.terminados)}")
        print(f"  Clock total      : {self._clock:.2f}s")
        print()

    def imprimir_log_eventos(self) -> None:
        print("\n")
        print("  LOG COMPLETO DE EVENTOS")
        print()
        print(f"  {'Clock':>7}  {'PID':<4} {'Nome':<14}  {'Estado':<12}  {'Evento':<35}  Detalhe")
        print("  " + "-" * 90)
        for ev in self.log_eventos:
            print(
                f"  {ev['clock']:>7.2f}  P{ev['pid']:<3} {ev['nome']:<14}"
                f"  {ev['estado']:<12}  {ev['evento']:<35}  {ev['detalhe']}"
            )
        print()




def main() -> None:

    processos = [

        Processo("Navegador",          2,   10),
        Processo("Editor",             3,   12),
        Processo("Compilador",         1,   15),
        Processo("Banco_Dados",        1,   18),
        Processo("Antivirus",          5,   10),
        Processo("Reprodutor",         4,   11),
        Processo("Backup",             6,   13),
        Processo("Atualiz.",           7,   10),
        Processo("Servidor_HTTP",      2,   16),
        Processo("Monitor_Rede",       3,   12),
    ]

    sim = SimuladorCPU(processos, quantum=QUANTUM, velocidade=VELOCIDADE)
    sim.executar()
    sim.imprimir_tabela()
    sim.imprimir_log_eventos()


if __name__ == "__main__":
    main()
