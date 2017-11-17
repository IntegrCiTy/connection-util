import logging
import ict.connection.node as node

if __name__ == "__main__":
    node.Node.activate_console_logging(logging.DEBUG)
    n = node.Node("localhost", "backend_vhost",  "tool", "tool", "send.json")
    n.send(
        "obnl.simulation.node."+n.name,
        "obnl.simulation.node.connection_test",
        "Hello world!"
    )
