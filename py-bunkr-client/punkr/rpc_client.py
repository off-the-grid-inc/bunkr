import socket
import json
import uuid
import asyncio


class JsonProtocol(object):
    def __init__(self, version, method, *params):
        self.version = version
        self.method  = method
        self.params  = list(params)
        self.id      = str(uuid.uuid4())

    def __repr__(self):
        return json.dumps(
            {
                "version"   : self.version,
                "method"    : self.method,
                "params"    : self.params,
                "id"        : self.id}
        )

    @staticmethod
    def BuildMessage(version, method, *params):
        return str(JsonProtocol(list(params), version, method))

class RpcTcpClient(object):
    def __init__(self, address):
        self.address      = address
        self.socket       = None
        self.writer       = None
        self.reader       = None
        self.__connected  = False

    def connect(self):
        if not self.__connected:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.address)
            self.__connected = True

    def disconnect(self):
        if self.__connected and self.socket:
            self.socket.close()
            self.__connected = False

    async def async_connect(self):
        if not self.__connected:
            self.__connected = True
            self.reader, self.writer = await asyncio.open_unix_connection(self.address)

    async def async_disconnect(self):
        if self.__connected and self.writer:
            self.writer.close()
            # This should be call in python version > 3.7.4
            # await self.writer.wait_close()
            self.__connected = False

    def send(self, message):
        if not self.__connected:
            raise ConnectionError("Client is not connected to any TCP server.")
        self.socket.sendall(message.encode())
        data = self.socket.recv(1024)
        return json.loads(data.decode())

    async def async_send(self, message):
        if not self.__connected or not self.writer or not self.reader:
            raise ConnectionError("Client is not connected to any TCP server.")
        self.writer.write(message.encode())
        data = await self.reader.read(1024)
        return json.loads(data.decode())

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __await__(self):
        yield

    async def __aenter__(self):
        await self.async_connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_disconnect()


if __name__ == "__main__":
    bunkr_address = "/tmp/bunkr_daemon.sock"
    create = str(JsonProtocol("1.0", "CommandProxy.HandleCommand", {"Line": "new-text-secret foo foocontent"}))
    access = str(JsonProtocol("1.0", "CommandProxy.HandleCommand", {"Line": "access foo"}))
    delete = str(JsonProtocol("1.0", "CommandProxy.HandleCommand", {"Line": "delete foo"}))

    with RpcTcpClient(bunkr_address) as client:
        print(client.send(create))

    async def test_send_message():
        async with RpcTcpClient(bunkr_address) as client:
            for c in (access, delete):
                data = await client.async_send(c)
                print(data)

    asyncio.run(test_send_message())