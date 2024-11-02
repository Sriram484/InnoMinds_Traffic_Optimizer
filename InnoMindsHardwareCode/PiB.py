import argparse, time

parser = argparse.ArgumentParser()
parser.add_argument('--delay', type=int, help="delay in seconds")

delay = parser.parse_args().delay


print(f"Sleeping for {delay}s...")
time.sleep(delay)
