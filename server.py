
import spotbot
import spotstatus

from threading import Thread, Lock
import time


print("thread testing...")

theLock = Lock()

spotter_thread = Thread(target=spotbot.spotserver, args=(theLock, ) )
status_thread = Thread(target=spotstatus.statusServer, args=(theLock, '10.0.1.4', 8000) )


status_thread.start()
time.sleep(5)
spotter_thread.start()

status_thread.join()
spotter_thread.join()
