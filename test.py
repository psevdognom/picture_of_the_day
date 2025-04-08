from asyncio import sleep
import random

class Task:

    def __init__(self, name):
        self.name = name
        self.duration = random.randint(1, 10)

    def __str__(self):
        return f'task: {self.name}'

    async def run(self):
        print(f'{self.name} started')
        await sleep(self.duration)
        print(f'{self.name} finished')



