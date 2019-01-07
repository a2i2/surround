import pika

class Queue(object):
    connection = None
    channel = None

    @staticmethod
    def build_connection(connect_to):
        """Build connection to the broker.

        Parameters:
            connect_to (str): Broker to connect to. For same machine, pass localhost else specify IP.
        """
        Queue.connection = pika.BlockingConnection(pika.ConnectionParameters(connect_to))

    @staticmethod
    def create_channel():
        Queue.channel = Queue.connection.channel()

    @staticmethod
    def declare_queue(queue_name):
        """Create the recipient queue. If not present, message will be dropped.
        Parameters:
            queue_name (str): Name of the queue.
        """
        Queue.channel.queue_declare(queue=queue_name)