import asyncio

import sys, os
_current_dir = os.path.dirname(__file__)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import aiorequests

async def task1():
    print("Task 1 is running")
    
    print("Task 1 completed")

async def main():
    # tasks = [task1(), task2()]
    tasks = [task1()]
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())