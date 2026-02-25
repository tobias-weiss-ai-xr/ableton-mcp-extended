Asyncio-thread bridge patterns for audio analysis in MCP

Summary
- This document records patterns for bridging synchronous sounddevice callbacks and separate threading in the MCP server with an asyncio event loop. It focuses on three patterns you will typically need: using asyncio.run_coroutine_threadsafe, using asyncio.Queue for inter-thread data transfer, and a thread-safe cache alternative. It also includes minimal, copy-paste-ready code examples that align with the MCP server role in this repository.

Context in this repo
- sounddevice-based audio analysis runs in a separate, synchronous callback thread.
- The MCP server runs an asyncio-based event loop for its tools and tasks.
- Task 3 will implement the actual bridge using the patterns described here.

Pattern 1: Schedule coroutines from a producer thread using asyncio.run_coroutine_threadsafe
- When a sounddevice callback or a background worker (threads) needs to trigger an asyncio coroutine, the safe approach is to schedule it on the running loop with run_coroutine_threadsafe.
- Requirements:
  - A reference to the asyncio loop that runs the MCP server (often the main loop).
  - The data that should be consumed by an asyncio coroutine is passed to the coroutine.

Example:
```python
import asyncio
import numpy as np

# This should reference the running MCP asyncio loop in your process.
loop = asyncio.get_event_loop()

async def process_audio_chunk(chunk: np.ndarray):
    # Your async processing logic here (e.g., feed results to a rule engine)
    await asyncio.sleep(0)  # placeholder for real work
    return len(chunk)

# Producer (sounddevice callback) runs in its own thread
def audio_callback(indata, frames, time, status):
    chunk = indata.copy()
    # Schedule the async processing on the MCP loop safely from another thread
    asyncio.run_coroutine_threadsafe(process_audio_chunk(chunk), loop)
```

- Notes:
  - If you need the producer to await a result, you can capture the returned Future and add a callback.
  - If you cannot hold a reference to the loop, store it in a module-global variable during startup.

Pattern 2: Inter-thread data transfer with asyncio.Queue
- Use an asyncio.Queue to pass data from a producer thread to an asyncio consumer coroutine.
- From the producer thread, push items into the queue via loop.call_soon_threadsafe or via run_coroutine_threadsafe(q.put(...)).
- In the asyncio task, await q.get() and process items as they arrive.

Example (using loop.call_soon_threadsafe to enqueue):
```python
import asyncio
import numpy as np

loop = asyncio.get_event_loop()
audio_queue = asyncio.Queue(maxsize=1024)

def enqueue(chunk: np.ndarray):
    # thread-safe enqueue from a non-async thread
    loop.call_soon_threadsafe(asyncio.create_task, _consume_and_process(chunk))

async def _consume_and_process(chunk: np.ndarray):
    # This coroutine runs on the MCP loop
    await audio_queue.put(chunk)

async def consumer():
    while True:
        chunk = await audio_queue.get()
        # Process the chunk asynchronously
        await process_chunk(chunk)

async def process_chunk(chunk: np.ndarray):
    # Implement your analysis step here
    await asyncio.sleep(0)
    return len(chunk)

# Sounddevice callback
def audio_callback(indata, frames, time, status):
    enqueue(indata.copy())
```

- Alternative: push using run_coroutine_threadsafe(q.put(chunk)) to avoid extra wrappers, if you prefer direct put:
```python
def audio_callback(indata, frames, time, status):
    asyncio.run_coroutine_threadsafe(audio_queue.put(indata.copy()), loop)
```

Important note on thread-safety
- asyncio.Queue operations may be used safely from a single producer/consumer model within the same event loop, but pushing from an external thread must go through loop.call_soon_threadsafe or asyncio.run_coroutine_threadsafe to ensure thread-safety.

Pattern 3: Thread-safe caches for fast access by asyncio tasks
- If your bridge must share a small amount of state without triggering awaitable operations, a tiny thread-safe cache guarded by a Lock can be used.
- The asyncio side can read the cache within a coroutine, ensuring memory visibility with proper locking.

Example:
```python
import threading
import time

_cache = {}
_lock = threading.Lock()

def producer_tick(key, value):
    with _lock:
        _cache[key] = value

async def consumer_read(key):
    # Read under the same lock to maintain consistency
    with _lock:
        return _cache.get(key)
```

Bridge choice and recommendations
- For real-time audio, prefer a small bounded asyncio.Queue with a single consumer to keep latency low.
- If you can tolerate occasional data drops and want simpler code, a thin thread-safe cache with periodic async reads can work, but ensure memory visibility is correct.
- In the MCP project, plan to implement a single producer per analysis stream and one or more asyncio consumers to feed the rule engines.

Code references in this repository
- MCP_Server/server.py demonstrates asyncio-based tool endpoints and the use of an event loop for async work.
- MCP_Server/audio_analysis/polling.py shows a separate thread performing polling and dispatching via callbacks. This is the exact scenario where bridging to asyncio is needed.

Appendix: recommended starter bridge (pseudo-structure)
- Sounddevice callback → data to a thread-safe queue OR run_coroutine_threadsafe onto the MCP loop
- Async worker consumes from queue or awaits work via coroutines
- Any results needed by synchronous code should be fed back through a thread-safe cache or a future from run_coroutine_threadsafe.
