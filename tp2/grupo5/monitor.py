import asyncio
import random
import time

QUEUE_MAX_SIZE   = 10
PRODUCE_INTERVAL = 0.5
RUNTIME_SECONDS  = 10
BPM_MIN          = 40
BPM_MAX          = 180
ALERT_THRESHOLD  = 120


async def producer(queue: asyncio.Queue, stop_event: asyncio.Event) -> None:
    reading = 0
    while not stop_event.is_set():
        bpm = random.randint(BPM_MIN, BPM_MAX)
        reading += 1

        await queue.put(bpm)
        print(f"  [Sensor #{reading:03d}] Leitura enviada: {bpm} bpm")

        try:
            await asyncio.wait_for(
                asyncio.shield(stop_event.wait()),
                timeout=PRODUCE_INTERVAL
            )
        except asyncio.TimeoutError:
            pass

    await queue.put(None)
    print("\n  [Sensor] Encerrado.")


async def consumer(queue: asyncio.Queue, stop_event: asyncio.Event) -> None:
    while True:
        bpm = await queue.get()

        if bpm is None:
            queue.task_done()
            break

        if bpm > ALERT_THRESHOLD:
            print(f"  ALERTA: Batimento em {bpm} bpm!")
        else:
            print(f"  Normal: {bpm} bpm")

        queue.task_done()

    print("  [Monitor] Encerrado.")


async def timer(stop_event: asyncio.Event) -> None:
    await asyncio.sleep(RUNTIME_SECONDS)
    print(f"\n[Sistema] {RUNTIME_SECONDS}s atingidos — encerrando...")
    stop_event.set()


async def main() -> None:
    queue       = asyncio.Queue(maxsize=QUEUE_MAX_SIZE)
    stop_event  = asyncio.Event()

    print("=" * 55)
    print("  Monitor Cardíaco — Sistema Produtor/Consumidor")
    print(f"  Duração: {RUNTIME_SECONDS}s | Alerta acima de {ALERT_THRESHOLD} bpm")
    print("=" * 55 + "\n")

    start = time.perf_counter()

    await asyncio.gather(
        timer(stop_event),
        producer(queue, stop_event),
        consumer(queue, stop_event),
    )

    elapsed = time.perf_counter() - start
    print(f"\n[Sistema] Finalizado em {elapsed:.2f}s.")

if __name__ == "__main__":
    asyncio.run(main())
