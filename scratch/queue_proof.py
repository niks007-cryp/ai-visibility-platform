"""
Proof of concept: asyncio.Queue cross-process failure demonstration.

Run this script to see exactly what happens when the API and Worker
are in separate processes — as they are in Railway multi-service deployments.
"""
import asyncio
import multiprocessing
import time


# ─────────────────────────────────────────────────────────────────
# This simulates the CURRENT queue_service singleton
# exactly as written in app/services/queue_service.py
# ─────────────────────────────────────────────────────────────────

class SimulatedQueueService:
    """Mirrors the real QueueService using asyncio.Queue."""
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def enqueue(self, job_id: str):
        await self._queue.put({"job_id": job_id})
        print(f"[API PROCESS]    Enqueued job_id={job_id} | queue_size={self._queue.qsize()}")

    async def dequeue(self, timeout=1.0):
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def size(self):
        return self._queue.qsize()


# ─────────────────────────────────────────────────────────────────
# PROCESS 1: Simulates the Railway API service container
# Enqueues 3 jobs via POST /projects/{id}/jobs
# ─────────────────────────────────────────────────────────────────

def api_process():
    async def run():
        qs = SimulatedQueueService()  # <-- SEPARATE IN-MEMORY INSTANCE
        print(f"\n[API PROCESS]    Starting. queue object id={id(qs._queue)}")
        for i in range(3):
            await qs.enqueue(f"job-{i+1:04d}")
            await asyncio.sleep(0.1)
        print(f"[API PROCESS]    Done. {qs.size()} jobs sitting in API memory.\n")
    asyncio.run(run())


# ─────────────────────────────────────────────────────────────────
# PROCESS 2: Simulates the Railway Worker service container
# Tries to dequeue and execute jobs
# ─────────────────────────────────────────────────────────────────

def worker_process():
    async def run():
        qs = SimulatedQueueService()  # <-- COMPLETELY DIFFERENT IN-MEMORY INSTANCE
        print(f"[WORKER PROCESS] Starting. queue object id={id(qs._queue)}")
        print(f"[WORKER PROCESS] Queue size at startup: {qs.size()}")
        
        found = 0
        for _ in range(5):  # poll 5 times
            payload = await qs.dequeue(timeout=0.5)
            if payload:
                found += 1
                print(f"[WORKER PROCESS] Got job: {payload['job_id']}")
            else:
                print(f"[WORKER PROCESS] Nothing in queue. Sleeping...")
            await asyncio.sleep(0.3)
        
        print(f"\n[WORKER PROCESS] Jobs processed: {found}/3")
        if found == 0:
            print("[WORKER PROCESS] *** FAILURE: Zero jobs received. All lost in API process memory. ***\n")

    asyncio.run(run())


# ─────────────────────────────────────────────────────────────────
# Run both processes — just like Railway runs two services
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("DEMONSTRATION: asyncio.Queue across separate processes")
    print("Simulating: Railway API service + Railway Worker service")
    print("=" * 60)

    api = multiprocessing.Process(target=api_process)
    worker = multiprocessing.Process(target=worker_process)

    api.start()
    time.sleep(0.3)   # Let API enqueue first
    worker.start()

    api.join()
    worker.join()

    print("=" * 60)
    print("VERDICT: asyncio.Queue is PROCESS-LOCAL.")
    print("Cross-process communication is IMPOSSIBLE with asyncio.Queue.")
    print("Railway deploys each service as an isolated container.")
    print("The API's queue and the Worker's queue are NEVER the same object.")
    print("=" * 60)
