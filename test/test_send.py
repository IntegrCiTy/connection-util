import ict.connection.node as node

if __name__ == "__main__":

    with open("send.json") as json_file:
        content = json_file.read()

        n = node.Node("localhost", "backend_vhost",  "tool", "tool", content)
        n.send(
            "obnl.simulation.node."+n.name,
            "obnl.simulation.node.connection_test",
            "Hello world!"
        )
