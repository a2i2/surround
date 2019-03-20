import logging
from .wrapper import PipelineWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = PipelineWrapper()
    wrapper.run("data/output.txt")

if __name__ == "__main__":
    main()
