import logging
from .wrapper import PipelineWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = PipelineWrapper()
    wrapper.run(None)

if __name__ == "__main__":
    main()
