import time
print('Testing progress indicators...')

# Simulate the progress monitoring
import threading

stop_progress = threading.Event()

def progress_monitor():
    elapsed = 0
    while not stop_progress.is_set():
        time.sleep(5)  # Check every 5 seconds for testing
        elapsed += 5
        print(f'[LLM] {time.strftime("%H:%M:%S")} - Still generating... ({elapsed}s elapsed)')
        if elapsed > 30:  # Stop after 30 seconds for testing
            print(f'[LLM] {time.strftime("%H:%M:%S")} - Test completed')
            break

progress_thread = threading.Thread(target=progress_monitor, daemon=True)
progress_thread.start()

# Simulate work
time.sleep(15)
stop_progress.set()
progress_thread.join(timeout=1)

print('Progress indicator test completed successfully!')
