import signal
import time


class SignalHandler:
    alive = True

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print(f"Received signal {signum}, shutting down...")
        self.alive = False


def main():
    handler = SignalHandler()
    while handler.alive:
        print("Running")
        time.sleep(5)


if __name__ == "__main__":
    main()
