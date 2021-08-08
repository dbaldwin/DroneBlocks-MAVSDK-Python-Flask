import asyncio
from mavsdk.offboard import (Attitude, OffboardError)
from mavsdk import System

async def run():
    drone = System()
    
    await drone.connect("udp://:14540")
    await drone.action.arm()

    # Initialize setpoint
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))

    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        await drone.action.disarm()
        return


    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 180.0, 0.6))
    await asyncio.sleep(5)

    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 90.0, 0.6))
    await asyncio.sleep(5)

    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")

    await drone.action.land()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())