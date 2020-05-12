import pause
from datetime import datetime

now = datetime.now()
dt = datetime(now.year, now.month, now.day, 6, 55)
print("Time is now", now)
print("Pausing until", dt)
pause.until(dt)
