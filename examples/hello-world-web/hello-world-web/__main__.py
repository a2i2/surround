import logging
from .stages import WebWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = WebWrapper()
    wrapper.run()

if __name__ == "__main__":
    main()
