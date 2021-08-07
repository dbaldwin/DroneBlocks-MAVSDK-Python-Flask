import os
import json
from flask import Flask, Response, render_template, request, jsonify, send_from_directory
from flask_mqtt import Mqtt
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityNedYaw)
import asyncio

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '127.0.0.1'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 18830  # default port for non-tls connection
#app.config['MQTT_USERNAME'] = 'dennistest'  # set the username here if you need authentication for the broker
#app.config['MQTT_PASSWORD'] = 'Testing123'  # set the password here if the broker demands authentication
#app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/takeoff")
async def takeoff():
    drone = System() # Figure out how to pull this out into a global
    await drone.connect("udp://:14540")

    # Let's pull this logic out into its own method
    if (await is_in_air(drone)):
        return "drone is already in air"
    elif (await is_armed(drone) == False):
        await drone.action.arm()
    
    await drone.action.takeoff()

    return "drone is taking off"

@app.route("/land")
async def land():
    drone = System()
    await drone.connect("udp://:14540")

    if (await is_in_air(drone) == False):
        return "drone is already on the ground"
    else:
        await drone.action.land()
        return "drone is landing"

@app.route("/yaw")
async def yaw():

    drone = System()
    await drone.connect("udp://:14540")
    await drone.action.arm()

    try:
        #await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        return "error starting offboard"

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, -1.5, -90))
    await asyncio.sleep(10)

    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")
        return "error stopping offboard"

    return "yaw complete"


@app.route("/mqtt")
def mqtt():
    mqtt = Mqtt(app)
    data = {"servo": "servo_123", "action": "open"}
    mqtt.publish('vrc/pcc/set_servo_open_close', json.dumps(data))
    return "mqtt message published"


async def is_armed(drone):
    async for is_armed in drone.telemetry.armed():
        return is_armed

async def is_in_air(drone):
    async for is_in_air in drone.telemetry.in_air():
        return is_in_air

@app.route("/test")
async def test():
    drone = System()
    await drone.connect("udp://:14540")

    if(await is_armed(drone) and await is_in_air(drone)):
        return "drone is armed and drone is in air"
    else:
        return "else"

@app.route('/video_stream')
def video_feed():
    camera.get_video()
    return Response(get_frame(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_frame(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/connect")
def connect():
    udp.send_command("command")
    udp.get_response()

    if status == "ok":
        drone.is_connected = True
    else:
        drone.is_connected = False
    
    return drone.toJSON()

@app.route("/status")
def status():
    return drone.toJSON()

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json['command']
    udp.send_command(command)
    response = udp.get_response()
    return response

@app.route('/take_photo')
def take_photo():
    camera.take_photo()
    return drone.toJSON()

@app.route('/start_recording')
def start_recording():
    camera.start_recording()
    return drone.toJSON()

@app.route('/stop_recording')
def stop_recording():
    camera.stop_recording()
    return drone.toJSON()

@app.route('/launch_mission', methods=['POST'])
def launch_mission():
    mission_code = request.json['mission_code']
    mission.parse_mission(mission_code)
    return ""

@app.route('/pause_mission')
def pause_mission():
    mission.pause_mission()
    return ""

@app.route('/resume_mission')
def resume_mission():
    mission.resume_mission()
    return ""

# So that we can load DroneBlocks in an iframe
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'droneblocks/dist')
@app.route('/droneblocks/<path:path>', methods=['GET'])
def droneblocks(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = os.path.join(path, 'tello.html')

    return send_from_directory(static_file_dir, path)


if __name__ == "__main__":

    # # Initialize the drone class
    # drone = Drone(is_aruco_tracking_enabled=True)

    # # Camera for stream, photo, video
    # camera = Camera(drone)

    # # Udp for sending commands
    # udp = UDP()
    # udp.start_listening()

    # # Create the mission handler
    # mission = Mission(udp, camera, drone)

    # # Handle Tello's state information
    # telemetry = Telemetry(drone)
    # telemetry.receive_telemetry()

    # Initialize the drone object
    drone = System()
   
    # Fire up the app
    app.run(host="0.0.0.0")