# DroneBlocks-MAVSDK-Python-Flask
DroneBlocks proof of concept for block coding with PX4 based aircraft and companion computer

## Getting up and running
1. python3 -m venv venv
2. source venv/bin/activate (MacOS)
3. pip install -r requirements.txt
    * If you end up seeing an error about Python modules not being found be sure to upgrade your pip and this should address the issue: **python -m pip install pip --upgrade**
4. flask run --host=0.0.0.0
    * The host argument allows the Flask server to be accessible outside localhost


