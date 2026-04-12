import asyncio
import random
import time

ARQUIVOS = [
    "relatorio_anual.pdf",
    "dataset_treino.csv",
    "virus.exe",
    "imagem_satellite.tif",
    "backup_banco.sql",
    "modelo_ml.pkl",
    "documentacao.zip",
]

ARQUIVO_PROIBIDO = "virus.exe"

async def baixar_arquivo(nome_arquivo: str) -> str:
    if nome_arquivo == ARQUIVO_PROIBIDO:
        raise ValueError(
            f"[BLOQUEADO] '{nome_arquivo}' foi recusado por política de segurança."
        )

    tempo_download = random.uniform(1.0, 5.0)

    print(f"  ⬇  Iniciando download: {nome_arquivo}")

    await asyncio.sleep(tempo_download)

    print(f"  ✓  Concluído: {nome_arquivo:<30} ({tempo_download:.2f}s)")

    return f"{nome_arquivo} ({tempo_download:.2f}s)"

async def main():
    print("=" * 60)
    print("  Motor de Downloads Assíncrono — asyncio")
    print("=" * 60)
    print(f"  Arquivos na fila : {len(ARQUIVOS)}")
    print(f"  Arquivo proibido : {ARQUIVO_PROIBIDO}")
    print("-" * 60)
    print("  Iniciando downloads simultâneos...\n")

    inicio = time.perf_counter()

    resultados = await asyncio.gather(
        *[baixar_arquivo(arq) for arq in ARQUIVOS],
        return_exceptions=True
    )

    fim = time.perf_counter()
    tempo_total = fim - inicio

    print()
    print("=" * 60)
    print("  RELATÓRIO FINAL")
    print("=" * 60)

    arquivos_ok     = []
    arquivos_falha  = []

    for arquivo, resultado in zip(ARQUIVOS, resultados):
        if isinstance(resultado, Exception):
            arquivos_falha.append(arquivo)
            print(f"  ✗  ERRO  | {arquivo}")
            print(f"           └─ {resultado}")
        else:
            arquivos_ok.append(resultado)
            print(f"  ✓  OK    | {resultado}")

    print("-" * 60)
    print(f"  Downloads bem-sucedidos : {len(arquivos_ok)}")
    print(f"  Downloads com falha     : {len(arquivos_falha)}")
    print(f"  Tempo total (paralelo)  : {tempo_total:.2f}s")

    tempos_individuais = []
    for r in resultados:
        if not isinstance(r, Exception):
            t = float(r.split("(")[1].replace("s)", ""))
            tempos_individuais.append(t)

    tempo_sequencial = sum(tempos_individuais)
    speedup = tempo_sequencial / tempo_total if tempo_total > 0 else 1.0

    print(f"  Tempo sequencial (est.) : {tempo_sequencial:.2f}s")
    print(f"  Speedup obtido          : {speedup:.1f}×")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())