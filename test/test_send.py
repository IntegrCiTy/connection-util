import logging
import json
import ict.connection.node as node

if __name__ == "__main__":
    node.Node.activate_console_logging(logging.DEBUG)

    with open("send.json") as json_file:
        content = json_file.read()
        # content = json.loads(content)

        n = node.Node("localhost", "backend_vhost",  "tool", "tool", content)
        n.send(
            "obnl.simulation.node."+n.name,
            "obnl.simulation.node.connection_test",
            "Hello world!"
        )
