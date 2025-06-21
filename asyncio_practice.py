import asyncio


async def task1():
    print("starting task1")
    await asyncio.sleep(2)
    print("task1 ended")

async def task2():
    print("starting task2")
    await asyncio.sleep(1)
    print("task2 ended")
async def main():
    t1=asyncio.create_task(task1())
    t2=asyncio.create_task(task2())
    
    print("Main: Waiting for tasks...")
    await t1
    await t2
    print("Main: All done")
    
asyncio.run(main())