import logging
import ict.connection.logger as logger
import ict.connection.node as node

if __name__ == "__main__":
    logger.activate_console_logging(logging.DEBUG)
    n = node.Node("localhost", "backend_vhost",  "tool", "tool", "send.json")
    n.send(
        "obnl.simulation.node.send_test",
        "obnl.simulation.node.connection_test",
        "Hello world!"
    )
