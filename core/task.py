from transitions.extensions.asyncio import AsyncMachine
import pyperclip
import asyncio
import time


class AsyncModel:

    def prepare_model(self):
        print("I am synchronous.")
        self.start_time = time.time()

    async def before_change(self):
        print("I am asynchronous and will block now for 100 milliseconds.")
        await asyncio.sleep(1)
        print("I am done waiting.")

    def sync_before_change(self):
        print(
            "I am synchronous and will block the event loop (what I probably shouldn't)"
        )
        time.sleep(3)
        print("I am done waiting synchronously.")

    def after_change(self):
        print(
            f"I am synchronous again. Execution took {int((time.time() - self.start_time) * 1000)} ms."
        )


transition = dict(
    trigger="start",
    source="Start",
    dest="Done",
    prepare="prepare_model",
    before=["before_change"] * 5 + ["sync_before_change"],
    after="after_change")  # execute before function in asynchronously 5 times

model = AsyncModel()
machine = AsyncMachine(model,
                       states=["Start", "Done"],
                       transitions=[transition],
                       initial='Start')

asyncio.run(model.start())
# >>> I am synchronous.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am synchronous and will block the event loop (what I probably shouldn't)
#     I am done waiting synchronously.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am synchronous again. Execution took 101 ms.
# assert model.is_Done()
