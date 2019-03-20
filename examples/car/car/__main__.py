import logging
from .wrapper import PipelineWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = PipelineWrapper()
    wrapper.run("data/1.jpg")

if __name__ == "__main__":
    main()
