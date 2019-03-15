import logging
from .stages import PipelineWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = PipelineWrapper()
    wrapper.run(None)

if __name__ == "__main__":
    main()
