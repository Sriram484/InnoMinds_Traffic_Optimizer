# File for running in Pi terminal

import subprocess, time

subprocess.run(['lxterminal', '-e', 'python3', 'DemoModelTraffic/B.py', '--number', '30'])
time.sleep(30)