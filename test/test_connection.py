import logging
import ict.connection.logger as logger
import ict.connection.node as node


class TestNode(node.Node):

    def __init__(self, host, vhost,  username, password, config_file="connection.json"):
        super().__init__(host, vhost,  username, password, config_file)

    def on_simulation_message(self, ch, method, props, body):
        TestNode.LOGGER.info(self.name + ': ' + str(body))

    def on_local_message(self, ch, method, props, body):
        TestNode.LOGGER.info(self.name + ': ' + str(body))

    def on_data_message(self, ch, method, props, body):
        TestNode.LOGGER.info(self.name + ': ' + str(body))


if __name__ == "__main__":
    logger.activate_console_logging(logging.DEBUG)
    n = TestNode("localhost", "backend_vhost",  "tool", "tool")
    n.start()
