import logging
from .wrapper import PipelineWrapper

logging.basicConfig(level=logging.INFO)

def main():
    wrapper = PipelineWrapper()
    with open("data/1.jpg", "rb")  as outfile:
        data = outfile.read()
    wrapper.run(data)

if __name__ == "__main__":
    main()
