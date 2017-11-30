from types import MethodType
import uuid
import logging
import logging.handlers
import json
import pika


class Node(object):
    """
    This is the base class for all Nodes of the system.
    """
    # TODO: put str in variable to identify the key in the file.
    TAG_SEPARATOR = '|'

    LOGGER = logging.getLogger(__name__)

    DEFAULT_LOGGING_FORMAT = '%(levelname)s - %(asctime)s - %(message)s'
    """The default logging format using standard logging library"""

    CONSOLE_HANDLER = logging.StreamHandler()
    FILE_HANDLERS = {}

    def __init__(self, host, vhost, username, password, config="connection.json"):
        """

        :param host: the host of AMQP server
        :param vhost: the virtual host name
        :param username: the username to connect to the server
        :param password: the associated password
        :param config: the location of the file to load AMQP topology (queues, exchanges, bindings, etc.)
        """
        super().__init__()

        self._config = config
        self._queues = {}
        self._exchanges = {}

        self._host = host
        self._vhost = vhost

        Node.LOGGER.debug("Connecting to AMQP server " + str(host) + '/' + str(vhost) + "...")

        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self._host, virtual_host=self._vhost, credentials=credentials)
        )
        self._channel = connection.channel()

        Node.LOGGER.info("Connected to " + str(host) + '/' + str(vhost))

        json_data = self._load_config_file()

        self._name = json_data["name"] if "name" in json_data else self.__class__.__name__ + '_' + str(uuid.uuid1())

        self._create_queues(json_data)

        self._create_exchanges(json_data)

        Node.LOGGER.info(self._name + " initialised.")

    def _load_config_file(self):
        res = None
        if type(self._config) is dict:
            res = self._config
        elif type(self._config is str):
            try:
                with open(self._config) as json_file:
                    content = json_file.read()
            except FileNotFoundError:
                content = self._config
            res = json.loads(content)

        return res

    def _create_queues(self, dict_data):
        Node.LOGGER.debug("Creation of queues...")

        if "queues" in dict_data:
            queues_data = dict_data["queues"]

            for name, func in queues_data.items():
                if name.endswith('.'):
                    name = name + self.name

                if type(func) is dict:
                    onlyone = func["get"]
                    func = func["callback"]

                if not hasattr(self, func):
                    info_func = str(self.__class__) + "." + func + "(self, ch, method, props, body)"
                    Node.LOGGER.warning("Abstract function '" + info_func + "' not implemented.")

                    def callback_func(the_self, ch, method, props, body):
                        raise NotImplementedError("Abstract function call from " + info_func + " must be implemented.")
                    setattr(self, func, MethodType(callback_func, self))

                self._queues[name] = self._channel.queue_declare(queue=name)
                self._channel.basic_consume(getattr(self, func),
                                            consumer_tag=name + Node.TAG_SEPARATOR + self._name,
                                            queue=self._queues[name].method.queue)
                Node.LOGGER.debug("Queue '" + str(name) + "' connected to '" + func + "'.")
        Node.LOGGER.debug("All Queues are created.")

    def _create_exchanges(self, dict_data):
        Node.LOGGER.debug("Creation of exchanges...")

        if "exchanges" in dict_data:
            exchanges_data = dict_data["exchanges"]

            for name, infos in exchanges_data.items():
                if name.endswith('.'):
                    name = name + self.name
                exchange_id = name
                self._exchanges = self._channel.exchange_declare(exchange=exchange_id)
                if "binding" in infos:
                    for bind in infos["binding"]:
                        if type(bind) is str:
                            if bind.endswith('.'):
                                bind = bind + self.name
                            self._channel.queue_declare(bind)
                            self._channel.queue_bind(exchange=exchange_id,
                                                     queue=bind
                                                     )
                            Node.LOGGER.debug("Exchange '" + name + "' is connected to the Queue '" + bind + "'.")
                        elif type(bind) is dict:
                            for queue, routing_key in bind:
                                if routing_key.endswith('.'):
                                    routing_key = routing_key + self.name
                                self._channel.queue_declare(queue)
                                self._channel.queue_bind(exchange=exchange_id,
                                                         queue=queue,
                                                         routing_key=routing_key
                                                         )
                                Node.LOGGER.debug("Exchange '" + name +
                                                  "' is connected to the Queue '" + queue +
                                                  "' with the routing key '" + routing_key + "'.")
                        else:
                            raise TypeError("Unsupported type "+type(bind)+" for binding.")
                else:
                    Node.LOGGER.debug("Exchange '" + name + "' is created with no binding.")
        Node.LOGGER.debug("All Exchanges are created.")

    @property
    def host(self):
        """

        :return: the connected host.
        """
        return self._host

    @property
    def vhost(self):
        """

        :return: The RabbitMQ virtual host.
        """
        return self._vhost

    @property
    def name(self):
        """

        :return: the name of the Node
        """
        return self._name

    def start(self):
        """
        Starts listening.
        """
        Node.LOGGER.debug("Start consuming.")
        self._channel.start_consuming()

    def send(self, exchange, routing, message, reply_to=None):
        """

        :param exchange: the AMQP/MQTT exchange
        :param routing: the AMQP/MQTT routing key
        :param message: the message content
        :param reply_to: the routing key to reply to
        """
        Node.LOGGER.debug("Send message: " + repr(message) + " from '" + str(exchange) + "' to '" + str(routing) + "'.")
        self._channel.publish(exchange=exchange,
                              routing_key=routing,
                              properties=pika.BasicProperties(reply_to=reply_to),
                              body=message)

    @staticmethod
    def activate_console_logging(log_level=logging.INFO):
        if Node.CONSOLE_HANDLER not in Node.LOGGER.handlers:
            Node._add_handler(Node.CONSOLE_HANDLER, log_level)

    @staticmethod
    def deactivate_console_logging():
        if Node.CONSOLE_HANDLER in Node.LOGGER.handlers:
            Node._remove_handler(Node.CONSOLE_HANDLER)

    @staticmethod
    def activate_file_logging(filename, log_level=logging.INFO):
        if filename not in Node.FILE_HANDLERS:
            handler = logging.handlers.TimedRotatingFileHandler(filename)
            Node.FILE_HANDLERS[filename] = handler
            Node._add_handler(handler, log_level)

    @staticmethod
    def deactivate_file_logging(filename):
        if filename in Node.FILE_HANDLERS:
            Node._remove_handler(Node.FILE_HANDLERS.pop(filename))

    @staticmethod
    def _add_handler(handler, log_level):
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(Node.DEFAULT_LOGGING_FORMAT))
        Node.LOGGER.setLevel(1)  # TODO log all data
        Node.LOGGER.addHandler(handler)

    @staticmethod
    def _remove_handler(handler):
        Node.LOGGER.removeHandler(handler)
