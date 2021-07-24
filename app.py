import os
from flask import Flask, Response, render_template, request, jsonify, send_from_directory
from mavsdk import System

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/takeoff")
async def takeoff():
    drone = System()
    await drone.connect("udp://:14540")

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
    await drone.action.land()
    return "drone is landing"

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