import cv2
import os
from vidgear.gears import CamGear
import argparse
import time

path = "frames/"
source = "https://www.youtube.com/watch?v=jGwO_UgTS7I"

time_start = time.time()

stream = CamGear(
    source=source,
    stream_mode=True,
    time_delay=1,
    logging=True,
).start()

current_frame = 0
while True:
    frame = stream.read()
    if frame is None:
        break

    name = os.path.join(path, f"frame{current_frame}.jpg")
    print("Creating...", name)
    cv2.imwrite(name, frame)
    current_frame += 1

cv2.destroyAllWindows()
stream.stop()

time_end = time.time()
time_taken = round(time_end - time_start, 3)

print("=======================================================")
print("-------------------------------------------------------")
print(f"## The time taken to create dataset: {time_taken} seconds ##")
print("-------------------------------------------------------")
print("=======================================================")