from collections import namedtuple
import parse

from .rpc_client import *


_FmtCommand =  namedtuple("CommandData", ("fmt_command", "fmt_result"))


class PunkrException(BaseException):
    pass

class Punkr(object):
    """
    Punkr (Python Bunkr) is the wrapper class around Bunkr operations
    Internally it uses a custom RPC TCP client to communicate with a daemonized Bunkr

    Punkr.FmtCommands is an addressing dictionary that contains matching pairs of:
        command_name : (command_string_to_format, command_result_string_to_format or None in case it can't be parsed)
    """
    _FmtCommands = {
        "new-text-secret": _FmtCommand(
            fmt_command='new-text-secret {secret_name} "{content}"',
            fmt_result=None
        ),
        "create": _FmtCommand(
            fmt_command="create {secret_name} {secret_type}",
            fmt_result=None
        ),
        "write": _FmtCommand(
            fmt_command='write {secret_name} {content_type} "{content}"',
            fmt_result=None
        ),
        "access": _FmtCommand(
            fmt_command="access {secret_name}",
            fmt_result=None
        ),
        "delete": _FmtCommand(
            fmt_command="delete {secret_name}",
            fmt_result=None
        ),
        "sign-ecdsa": _FmtCommand(
            fmt_command="sign-ecdsa {secret_name} {hash_content}",
            fmt_result=None
        ),
        "new-group": _FmtCommand(
            fmt_command="new-group {group_name}",
            fmt_result=None
        ),
        "grant": _FmtCommand(
            fmt_command="grant {device_name} {secret_name}",
            fmt_result=None
        ),
    }

    @staticmethod
    def ListCommands():
        """
        List the available commands for batching operations
        :return: List of available command keys
        """
        return Punkr._FmtCommands.keys()

    def __init__(self, address):
        """
        Class init method
        :param address:
        :param port:
        """
        self.__address  = address
        self.__client   = RpcTcpClient(address)

    def __exec_cmd(self, client, cmd_name, **kwargs):
        """
        __exec_cmd wraps the rpc call to a bunkr command.
        :param cmd_name: Name of the command registered in Punkr.FmtCommands
        :param client: RPC client to be use for the connection
        :param kwargs: Named arguments to be injected in the formatting commands
        :return: The result returned from the Bunkr command
        :raises: PunkrException wrapping the error returning from the Bunkr command
        """
        # Retrieve command parsing information
        cmd = Punkr._FmtCommands[cmd_name]
        cmd_fmt, result_fmt = cmd.fmt_command, cmd.fmt_result
        # Build message
        message = str(
            JsonProtocol(
                "1.0",
                "CommandProxy.HandleCommand",
                {"Line": cmd_fmt.format(**kwargs)}
            )
        )
        data = client.send(message)
        # Check if we had any error with the communications
        if data["error"] is not None:
            raise PunkrException(data["error"])
        # check if we had some operation error
        operation_error = data["result"]["Error"]
        if operation_error != "":
            raise PunkrException(operation_error)
        # result is wrapped by the jsonrpc protocol (result) and the Result go object (Result)
        result =  data["result"]["Result"]
        if result_fmt is not None:
            parsed_result = result_fmt.parse(result)
            return parsed_result["content"]
        return result


    async def __async_exec_cmd(self, client, cmd_name, **kwargs):
        """
        __async_exec_cmd wraps the asynchronous rpc call to a bunkr command.
        :param cmd_name: Name of the command registered in Punkr.FmtCommands
        :param client: Asynchronous RPC client to be use for the connection
        :param kwargs: Named arguments to be injected in the formatting commands
        :return: The result returned from the Bunkr command
        :raises: PunkrException wrapping the error returning from the Bunkr command
        """
        # Retrieve command parsing information
        cmd = Punkr._FmtCommands[cmd_name]
        cmd_fmt, result_fmt = cmd.fmt_command, cmd.fmt_result
        # Build message
        message = str(
            JsonProtocol(
                "1.0",
                "CommandProxy.HandleCommand",
                {"Line": cmd_fmt.format(**kwargs)}
            )
        )
        data = await client.async_send(message)
        # Check if we had any error with the operation
        if data["error"] is not None:
            raise PunkrException(data["error"])
        # check if we had some operation error, the error goes inside the go object (Result.Error)
        operation_error = data["result"]["Error"]
        if operation_error != "":
            raise PunkrException(operation_error)
        # result is wrapped by the jsonrpc protocol (result) and the Result go object (Result.Result)
        result = data["result"]["Result"]
        if result_fmt is not None:
            parsed_result = result_fmt.parse(result)
            return parsed_result["content"]
        return result

    def new_text_secret(self, secret_name, content):
        """
        new_text_secret creates and writes a secret
        :param secret_name: name of secret to write
        :param content: secret content
        :param group_name: optional name of group (defaults to empty string)
        :return: command execution result ("Secret created")
        """
        with self.__client as client:
            return self.__exec_cmd(client, "new-text-secret", secret_name=secret_name, content=content)
            
    def access(self, secret_name):
        """
        access command to get the content of a secret
        :param secret_name: name of the secret to query
        :return: secret content
        """
        with self.__client as client:
            return self.__exec_cmd(client, "access", secret_name=secret_name)

    def create(self, secret_name, secret_type):
        """
        write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param content: new secret content
        :return: command execution result ("Secret written")
        """
        with self.__client as client:
            return self.__exec_cmd(client, "create", secret_name=secret_name, secret_type=secret_type)

    def write(self, secret_name, content, content_type="b64"):
        """
        write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param content: new secret content
        :return: command execution result ("Secret written")
        """
        with self.__client as client:
            return self.__exec_cmd(client, "write", secret_name=secret_name, content_type=content_type, content=content)

    def delete(self, secret_name):
        """
        delete, delete specified secret
        :param secret_name: name of the secret to be deleted
        :return: command execution result ("Secret deleted")
        """
        with self.__client as client:
            return self.__exec_cmd(client, "delete", secret_name=secret_name)

    def sign_ecdsa(self, secret_name, hash_content):
        """
        sign_ecdsa requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :param hash_content: hash to be signed
        :return: signed hash
        """
        with self.__client as client:
            return self.__exec_cmd(client, "sign-ecdsa", secret_name=secret_name, hash_content=hash_content)

    def new_group(self, group_name):
        """
        delete, delete specified secret
        :param group_name: name of the group to be created
        :param parent_group_name: name of the parent group of this secret (defaults to no parent)
        :return: command execution result ("Secret created")
        """
        with self.__client as client:
            return self.__exec_cmd(client, "new-group", group_name=group_name)

    def grant(self, device_name, secret_name):
        """
        grant, grant a device or group a capability on a secret
        :param device_name: name of the device (or group)
        :param parent_group_name: name of the secret to grant
        """
        with self.__client as client:
            return self.__exec_cmd(client, "grant", device_name=device_name, secret_name=secret_name)

    def batch_commands(self, *args):
        """
        batch_commands receives a variable number of arguments of the type:
        `(operation_name, {operation_arg_name:operarion_arg_value})`
        where `operation_name` is the name of a command registered in `Punkr._FmtCommands`,
        or listed in `Punkr.ListCommands` and the second tuple element is a dictionary with the named format arguments
        of the `Punk._FmtCommands[operation_name].fmt_command`
        :yields: ordered command results
        """
        with self.__client as client:
            yield from (self.__exec_cmd(client, command_name, **kw) for command_name, kw in args)

    async def async_new_text_secret(self, secret_name, content):
        """
        async_new_text_secret creates and writes a secret
        :param secret_name: name of secret to write
        :param content: secret content
        :return: command execution result ("Secret created")
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "new-text-secret", secret_name=secret_name, content=content)

    async def async_access(self, secret_name):
        """
        async_access command to get the content of a secret
        :param secret_name: name of the secret to query
        :return: secret content
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "access", secret_name=secret_name)

    async def async_write(self, secret_name, content, content_type="b64"):
        """
        async_write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param content: new secret content
        :return: command execution result ("Secret written")
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "write", secret_name=secret_name, content_type=content_type, content=content)

    async def async_delete(self, secret_name):
        """
        async_delete, delete specified secret
        :param secret_name: name of the secret to be deleted
        :return: command execution result ("Secret deleted")
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "delete", secret_name=secret_name)

    async def async_sign_ecdsa(self, secret_name, hash_content):
        """
        async_sign_ecdsa requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :param hash_content: hash to be signed
        :return: signed hash
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "sign-ecdsa", secret_name=secret_name, hash_content=hash_content)

    async def async_new_group(self, group_name):
        """
        async_delete, delete specified secret
        :param secret_name: name of the secret to be deleted
        :return: command execution result ("Secret deleted")
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, "new-group", group_name=group_name)

    async def async_batch_commands(self, *args):
        """
        async_batch_commands receives a variable number of arguments of the type:
        `(operation_name, {operation_arg_name:operarion_arg_value})`
        where `operation_name` is the name of a command registered in `Punkr._FmtCommands`, or listed in `Punkr.ListCommands`
        and the second tuple element is a dictionary with the named format arguments of the `Punk._FmtCommands[operation_name].fmt_command`
        :yields: unordered command results
        """
        async def wrapped_command(command_name, **kw):
            async with RpcTcpClient(self.__address) as client:
                return await self.__async_exec_cmd(client, command_name, **kw)
        commands = [wrapped_command(command_name, **kw) for command_name, kw in args]
        for result in asyncio.as_completed(commands):
            ret = await result
            yield ret

    async def async_ordered_batch_commands(self, *args):
        """
        async_batch_commands receives a variable number of arguments of the type:
        `(operation_name, {operation_arg_name:operarion_arg_value})`
        where `operation_name` is the name of a command registered in `Punkr._FmtCommands`, or listed in `Punkr.ListCommands`
        and the second tuple element is a dictionary with the named format arguments of the `Punk._FmtCommands[operation_name].fmt_command`
        :returns: ordered command results
        """
        async def wrapped_command(command_name, **kw):
            async with RpcTcpClient(self.__address) as client:
                return await self.__async_exec_cmd(client, command_name, **kw)
        commands = [wrapped_command(command_name, **kw) for command_name, kw in args]
        return await asyncio.gather(*commands)


if __name__ == "__main__":
    import asyncio
    # create a connection to the local Bunkr RPC server
    punkr = Punkr("/tmp/bunkr_daemon.sock")
    try:
        # create a new text secret (synchronously)
        print(punkr.new_text_secret("MySuperSecret", 'secret created from punkr'))
        commands = (
            ("access", {"secret_name": "MySuperSecret"}), # This is the structure of a batch command argument
            ("access", {"secret_name": "MySuperSecret"}),
            ("access", {"secret_name": "MySuperSecret"}),
        )
        # create corutine to access the secret (asynchronously, order of results is not guaranteed)
        async def async_test():
            async for result in punkr.async_batch_commands(*commands):
                print(result)
        # run corutine
        asyncio.run(async_test())
        # run corutine and get the results (order of result is guaranteed, but not ordered of execution)
        results1 = asyncio.run(punkr.async_ordered_batch_commands(*commands))
        print(results1)
        # execute a synchronous batch, ordered of execution and results ir guaranteed
        results2 = list(punkr.batch_commands(*commands))
        print(results2)
        assert results1 == results2
    except PunkrException as e:
        print(e)
    finally:
        # delete the secret (synchronously)
        punkr.delete("MySuperSecret")

