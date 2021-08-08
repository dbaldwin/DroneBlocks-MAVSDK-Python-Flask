import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)

async def run():
    drone = System()
    await drone.connect("udp://:14540")
    await drone.action.arm()

    try:
        # We must set the initial state before starting offboard
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        return

    # Yaw
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -1, 10))

    # Yaw for 10 seconds
    await asyncio.sleep(10)

    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")
        return

    await drone.action.land()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())