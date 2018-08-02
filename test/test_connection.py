from ict.connection.logs import logger
import ict.connection.node as node


# TODO: switch to Pytest
class TestNode(node.Node):

    def __init__(self, host, vhost,  username, password, config_file="connection.json"):
        super().__init__(host, vhost,  username, password, config_file)

    def on_simulation_message(self, ch, method, props, body):
        self._channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(self.name + ': ' + str(body))

    def on_local_message(self, ch, method, props, body):
        logger.info(self.name + ': ' + str(body))
        self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def on_data_message(self, ch, method, props, body):
        logger.info(self.name + ': ' + str(body))
        self._channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    n = TestNode("localhost", "backend_vhost",  "tool", "tool")
    n.start()

    while True:
        pass
