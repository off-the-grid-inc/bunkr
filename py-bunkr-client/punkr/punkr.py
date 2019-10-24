import enum

from .rpc_client import *

_JSON_RPC_PROTOCOL = "1.0"
_RPC_CALL = "CommandProxy.HandleCommand"

class Command(enum.Enum):
    NEW_TEXT_SECRET = "new-text-secret"
    NEW_SSH_KEY = "new-ssh-key"
    NEW_FILE_SECRET = "new-file-secret"
    NEW_GROUP = "new-group"
    IMPORT_SSH_KEY = "import-ssh-key"
    LIST_SECRETS = "list-secrets"
    LIST_DEVICES = "list-devices"
    LIST_GROUPS = "list-groups"
    SEND_DEVICE = "send-device"
    RECEIVE_DEVICE = "receive-device"
    REMOVE_DEVICE = "remove-device"
    REMOVE_LOCAL = "remove-local"
    RENAME = "rename"
    CREATE = "create"
    WRITE = "write"
    ACCESS = "access"
    GRANT = "grant"
    REVOKE = "revoke"
    DELETE = "delete"
    RECEIVE_CAPABILITY = "receive-capability"
    RESET_TRIPLES = "reset-triples"
    NOOP = "noop-test"
    SECRET_INFO = "secret-info"
    SIGN_ECDSA = "sign-ecdsa"
    SSH_PUBLIC_DATA = "ssh-public-data"
    SIGNIN = "sigin"
    CONFIRM_SIGNIN = "confirm-signin"

class SecretType(enum.Enum):
    ECDSASECP256k1Key = "ECDSA-SECP256k1"
    ECDSAP256Key = "ECDSA-P256"
    HMACKey = "HMAC"
    GenericGF256 = "GENERIC-GF256"
    GenericPF = "GENERIC-PF"

class PunkrException(BaseException):
    pass

def build_operation_args(command, *args):
    return {
        "Command": command.value,
        "Args": args,
    }

class Punkr(object):
    """
    Punkr (Python Bunkr) is the wrapper class around Bunkr operations
    Internally it uses a custom RPC TCP client to communicate with a daemonized Bunkr
    """

    def __init__(self, address):
        """
        Class init method
        :param address:
        :param port:
        """
        self.__address  = address
        self.__client   = RpcTcpClient(address)

    def __exec_cmd(self, client, command, *args):
        """
        __exec_cmd wraps the rpc call to a bunkr command.
        :param cmd_name: Name of the command registered in Punkr.FmtCommands
        :param client: RPC client to be use for the connection
        :param args: arguments to be injected in the JSON RPC Command object
        :return: The result returned from the Bunkr command
        :raises: PunkrException wrapping the error returning from the Bunkr command
        """
        # Build message
        message = str(
            JsonProtocol(
                _JSON_RPC_PROTOCOL,
                _RPC_CALL,
                build_operation_args(command, *args)
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
        result = data["result"]["Result"]
        return result


    async def __async_exec_cmd(self, client, command, *args):
        """
        __async_exec_cmd wraps the asynchronous rpc call to a bunkr command.
        :param cmd_name: Name of the command registered in Punkr.FmtCommands
        :param client: Asynchronous RPC client to be use for the connection
        :param kwargs: Named arguments to be injected in the formatting commands
        :return: The result returned from the Bunkr command
        :raises: PunkrException wrapping the error returning from the Bunkr command
        """
        # Build message
        message = str(
            JsonProtocol(
                _JSON_RPC_PROTOCOL,
                _RPC_CALL,
                build_operation_args(command, *args)
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
        return result

    def new_text_secret(self, secret_name, content):
        """
        new_text_secret creates and writes a secret
        :param secret_name: name of secret to write
        :param content: secret content
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.NEW_TEXT_SECRET, secret_name, content)

    def new_ssh_key(self, secret_name):
        """
        new_ssh_key creates a new ecdsa key and stores it as a secret
        :param secret_name: name of secret to write
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.NEW_SSH_KEY, secret_name)

    def new_file_secret(self, secret_name, file_path):
        """
        new_file_secret creates a secret with the content of an specified file
        :param secret_name: name of secret to write
        :param file_path: path of the file to upload
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.NEW_FILE_SECRET, secret_name, file_path)

    def new_group(self, group_name):
        """
        :param group_name: name of secret to write
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.NEW_GROUP, group_name)

    def import_ssh_key(self, secret_name, key_path):
        """
        import_ssh_key uploads an ecdsa key to Bunkr
        :param secret_name: name of secret to write
        :param key_path: path of the file to upload
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.IMPORT_SSH_KEY, secret_name, key_path)

    def list_secrets(self):
        """
        :return: json like object (dict)
        {
            "msg"     : "",
            "content" : {
                "secrets" : [string], # secrets names
                "devices" : {
                    "<device name>" : [string], # secrets names
                    ...
                },
                "groups" : {
                    "<group name>" : [string], # secrets names
                    ...
                },
            }
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.LIST_SECRETS)

    def list_devices(self):
        """
        :return: json like object (dict)
        {
            "msg" : "",
            "devices" : [string] # devices names
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.LIST_DEVICES)

    def list_groups(self):
        """
        :return: json like object (dict)
        {
            "msg"    : "",
            "groups" : [string] # groups names
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.LIST_GROUPS)

    def send_device(self, device_name=None):
        """
        :param send_device:  optional, name for the shared device
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "url_raw"   : "<shared static url>",
            "url_short" : "<shared short url>",
        }
        """
        with self.__client as client:
            if device_name is not None:
                return self.__exec_cmd(client, Command.SEND_DEVICE, device_name)
            return self.__exec_cmd(client, Command.SEND_DEVICE)

    def receive_device(self, url):
        """
        :param url: shared Bunkr send device url (either shortened or static)
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.RECEIVE_DEVICE, url)

    def remove_device(self, device_name):
        """
        :param device_name: device name to be removed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.REMOVE_DEVICE, device_name)

    def remove_local(self, secret_name):
        """
        :param secret_name: secret name to be removed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.REMOVE_LOCAL, secret_name)

    def rename(self, old_secret_name, new_secret_name):
        """
        :param old_secret_name:
        :param new_secret_name:
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.RENAME, old_secret_name, new_secret_name)

    def create(self, secret_name, secret_type):
        """
        write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param secret_type: secret type one of SecretType enum
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.CREATE, secret_name, secret_type.value)

    def write(self, secret_name, content, content_type="b64"):
        """
        write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param content: new secret content
        :param content_type: type of content, one of ("b64", "text")
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.WRITE, secret_name, content_type, content)

    def access(self, secret_name, mode="text", file_path=None):
        """
        access command to get the content of a secret
        :param secret_name: name of the secret to query
        :param mode: access mode, any of ["b64", "text", "file"], "text" by default
        :param file_path, file path to dump the secret content, must provide with "file" mode
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "mode"      : "<access mode>"
            "content"   : "<secret content just for (b64 and text)>",
        }
        """
        with self.__client as client:
            if mode == "file" and file_path:
                return self.__exec_cmd(client, Command.ACCESS, secret_name, mode, file_path)
            return self.__exec_cmd(client, Command.ACCESS, secret_name, mode)

    def grant(self, target, secret_name, admin=False):
        """
        grant command shares a secret to a device or group
        :param target: device or group name to grant a new capability to
        :param secret_name: granted secret
        :param admin: grant admin capability
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "url_raw"   : "<shared static url>",
            "url_short" : "<shared short url>",
        }
        """
        with self.__client as client:
            if admin:
                return self.__exec_cmd(client, Command.GRANT, target, secret_name, "admin")
            return self.__exec_cmd(client, Command.GRANT, target, secret_name)

    def revoke(self, target, secret_name):
        """
        revoke command removes a capability from a secret to the specified device or group
        :param target: device or group name to revoke the granted capability
        :param secret_name: secret with capability granted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.REVOKE, target, secret_name)

    def delete(self, secret_name):
        """
        delete, delete specified secret
        :param secret_name: name of the secret to be deleted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.DELETE, secret_name)

    def receive_capability(self, url):
        """
        receive_capability, load a capability into your Bunkr
        :param url: shared capability url (either static or shortened link)
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.RECEIVE_CAPABILITY, url)

    def reset_triples(self, secret_name):
        """
        reset_triples launches a reseting operation to synchronize the triples in a secret coalition
        :param: secret_name
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.RESET_TRIPLES, secret_name)

    def noop(self, secret_name):
        """
        noop is a health status operation
        :param secret_name:
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.NOOP, secret_name)

    def secret_info(self, secret_name):
        """
        secret_info return public secret info for the specified secret
        :param secret_name: name of the secret to be deleted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.SECRET_INFO, secret_name)

    def sign_ecdsa(self, secret_name, hash_content):
        """
        sign_ecdsa requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :param hash_content: hash to be signed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
            "r"   : "<R component of the signature>",
            "s"   : "<S component of the signature>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.SIGN_ECDSA, secret_name, hash_content)

    def ssh_public_data(self, secret_name):
        """
        ssh_public_data requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :return: json like object (dict)
        {
            "msg"           : "<feedback message>",
            "public_data"   : {
                "name"       : "<secret name>",
                "public_key" : "<b64 encoded public key>",
            }
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.SSH_PUBLIC_DATA, secret_name)

    def sigin(self, email, device_name):
        """
        sigin performs a Bunkr signin process
        :param email:
        :param device_name: identifier for current Bunkr device
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.SIGNIN, email, device_name)

    def confirm_signin(self, email, code):
        """
        confirm_signin verifies the sigin verification code to access the Bunkr
        :param email:
        :param code: verification code sent to email
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        with self.__client as client:
            return self.__exec_cmd(client, Command.CONFIRM_SIGNIN, email, code)

    def batch_commands(self, *args):
        """
        batch_commands receives a variable number of arguments of the type:
        `(Command, [<args list>])`
        where `operation_name` is the name of a command registered in the `Command` enum,
        and the second tuple element is a list with the operation arguments`
        :yields: ordered command results
        """
        with self.__client as client:
            yield from (self.__exec_cmd(client, command_name, *arguments) for command_name, arguments in args)

    async def async_new_text_secret(self, secret_name, content):
        """
        async_new_text_secret creates and writes a secret
        :param secret_name: name of secret to write
        :param content: secret content
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.NEW_TEXT_SECRET, secret_name, content)

    async def async_new_ssh_key(self, secret_name):
        """
        async_new_ssh_key creates a new ecdsa key and stores it as a secret
        :param secret_name: name of secret to write
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.NEW_SSH_KEY, secret_name)

    async def async_new_file_secret(self, secret_name, file_path):
        """
        async_new_file_secret creates a secret with the content of an specified file
        :param secret_name: name of secret to write
        :param file_path: path of the file to upload
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.NEW_FILE_SECRET, secret_name, file_path)

    async def async_new_group(self, group_name):
        """
        :param group_name: name of secret to write
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.NEW_GROUP, group_name)

    async def async_import_ssh_key(self, secret_name, key_path):
        """
        async_import_ssh_key uploads an ecdsa key to Bunkr
        :param secret_name: name of secret to write
        :param key_path: path of the file to upload
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.IMPORT_SSH_KEY, secret_name, key_path)

    async def async_list_secrets(self):
        """
        :return: json like object (dict)
        {
            "msg"     : "",
            "content" : {
                "secrets" : [string], # secrets names
                "devices" : {
                    "<device name>" : [string], # secrets names
                    ...
                },
                "groups" : {
                    "<group name>" : [string], # secrets names
                    ...
                },
            }
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.LIST_SECRETS)

    async def async_list_devices(self):
        """
        :return: json like object (dict)
        {
            "msg" : "",
            "devices" : [string] # devices names
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.LIST_DEVICES)

    async def async_list_groups(self):
        """
        :return: json like object (dict)
        {
            "msg"    : "",
            "groups" : [string] # groups names
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.LIST_GROUPS)

    async def async_send_device(self, device_name=None):
        """
        :param send_device:  optional, name for the shared device
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "url_raw"   : "<shared static url>",
            "url_short" : "<shared short url>",
        }
        """
        async with self.__client as client:
            if device_name is not None:
                return await self.__async_exec_cmd(client, Command.SEND_DEVICE, device_name)
            return await self.__async_exec_cmd(client, Command.SEND_DEVICE)

    async def asyn_receive_device(self, url):
        """
        :param url: shared Bunkr send device url (either shortened or static)
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.RECEIVE_DEVICE, url)

    async def async_remove_device(self, device_name):
        """
        :param device_name: device name to be removed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.REMOVE_DEVICE, device_name)

    async def async_remove_local(self, secret_name):
        """
        :param secret_name: secret name to be removed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.REMOVE_LOCAL, secret_name)

    async def async_rename(self, old_secret_name, new_secret_name):
        """
        :param old_secret_name:
        :param new_secret_name:
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.RENAME, old_secret_name, new_secret_name)

    async def async_create(self, secret_name, secret_type):
        """
        async_create, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param secret_type: secret type one of SecretType enum
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.CREATE, secret_name, secret_type.value)

    async def async_write(self, secret_name, content, content_type="b64"):
        """
        async_write, overwrite a secret content
        :param secret_name: name of the secret to overwrite
        :param content: new secret content
        :param content_type: type of content, one of ("b64", "text")
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.WRITE, secret_name, content_type, content)

    async def async_access(self, secret_name, mode="text", file_path=None):
        """
        async_access command to get the content of a secret
        :param secret_name: name of the secret to query
        :param mode: access mode, any of ["b64", "text", "file"], "text" by default
        :param file_path, file path to dump the secret content, must provide with "file" mode
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "mode"      : "<access mode>"
            "content"   : "<secret content just for (b64 and text)>",
        }
        """
        async with self.__client as client:
            if mode == "file" and file_path:
                return await self.__async_exec_cmd(client, Command.ACCESS, secret_name, mode, file_path)
            return await self.__async_exec_cmd(client, Command.ACCESS, secret_name, mode)

    async def async_grant(self, target, secret_name, admin=False):
        """
        async_grant command shares a secret to a device or group
        :param target: device or group name to grant a new capability to
        :param secret_name: granted secret
        :param admin: grant admin capability
        :return: json like object (dict)
        {
            "msg"       : "<feedback message>",
            "url_raw"   : "<shared static url>",
            "url_short" : "<shared short url>",
        }
        """
        async with self.__client as client:
            if admin:
                return await self.__async_exec_cmd(client, Command.GRANT, target, secret_name, *[] if not admin else "admin")
            return await self.__async_exec_cmd(client, Command.GRANT, target, secret_name)

    async def async_revoke(self, target, secret_name):
        """
        async_revoke command removes a capability from a secret to the specified device or group
        :param target: device or group name to revoke the granted capability
        :param secret_name: secret with capability granted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.REVOKE, target, secret_name)

    async def async_delete(self, secret_name):
        """
        async_delete, delete specified secret
        :param secret_name: name of the secret to be deleted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.DELETE, secret_name)

    async def async_receive_capability(self, url):
        """
        async_receive_capability, load a capability into your Bunkr
        :param url: shared capability url (either static or shortened link)
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.RECEIVE_CAPABILITY, url)

    async def async_reset_triples(self, secret_name):
        """
        async_reset_triples launches a reseting operation to synchronize the triples in a secret coalition
        :param: secret_name
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.RESET_TRIPLES, secret_name)

    async def async_noop(self, secret_name):
        """
        noop is a health status operation
        :param secret_name:
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.NOOP, secret_name)

    async def async_secret_info(self, secret_name):
        """
        async_secret_info return public secret info for the specified secret
        :param secret_name: name of the secret to be deleted
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.SECRET_INFO, secret_name)

    async def async_sign_ecdsa(self, secret_name, hash_content):
        """
        async_sign_ecdsa requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :param hash_content: hash to be signed
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
            "r"   : "<R component of the signature>",
            "s"   : "<S component of the signature>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.SIGN_ECDSA, secret_name, hash_content)

    async def async_ssh_public_data(self, secret_name):
        """
        async_ssh_public_data requests a signing with the specified secret content
        :param secret_name: secret name of the ecdsa key that should sign
        :return: json like object (dict)
        {
            "msg"           : "<feedback message>",
            "public_data"   : {
                "name"       : "<secret name>",
                "public_key" : "<b64 encoded public key>",
            }
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.SSH_PUBLIC_DATA, secret_name)

    async def async_sigin(self, email, device_name):
        """
        async_sigin performs a Bunkr signin process
        :param email:
        :param device_name: identifier for current Bunkr device
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.SIGNIN, email, device_name)

    async def async_confirm_signin(self, email, code):
        """
        confirm_signin verifies the sigin verification code to access the Bunkr
        :param email:
        :param code: verification code sent to email
        :return: json like object (dict)
        {
            "msg" : "<feedback message>",
        }
        """
        async with self.__client as client:
            return await self.__async_exec_cmd(client, Command.CONFIRM_SIGNIN, email, code)

    async def async_batch_commands(self, *args):
        """
        async_batch_commands receives a variable number of arguments of the type:
        `(Command, [<args list>])`
        where `operation_name` is the name of a command registered in the `Command` enum,
        and the second tuple element is a list with the operation arguments`
        :yields: unordered command results
        """
        async def wrapped_command(command_name, *arguments):
            async with RpcTcpClient(self.__address) as client:
                return await self.__async_exec_cmd(client, command_name, *arguments)
        commands = [wrapped_command(command_name, *arguments) for command_name, arguments in args]
        for result in asyncio.as_completed(commands):
            ret = await result
            yield ret

    async def async_ordered_batch_commands(self, *args):
        """
        async_batch_commands receives a variable number of arguments of the type:
        `(Command, [<args list>])`
        where `operation_name` is the name of a command registered in the `Command` enum,
        and the second tuple element is a list with the operation arguments`
        :returns: ordered command results
        """
        async def wrapped_command(command_name, *arguments):
            async with RpcTcpClient(self.__address) as client:
                return await self.__async_exec_cmd(client, command_name, *arguments)
        commands = [wrapped_command(command_name, *arguments) for command_name, arguments in args]
        return await asyncio.gather(*commands)


if __name__ == "__main__":
    import asyncio
    # create a connection to the local Bunkr RPC server
    punkr = Punkr("/tmp/bunkr_daemon.sock")
    to_delete = []
    try:
        # create a new text secret (synchronously)
        print(punkr.new_text_secret("MySuperSecret", 'secret created from punkr'))
        to_delete.append("MySuperSecret")
        commands = (
            (Command.ACCESS, ["MySuperSecret"]), # This is the structure of a batch command argument
            (Command.ACCESS, ["MySuperSecret"]),
            (Command.ACCESS, ["MySuperSecret"]),
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

        # create group
        punkr.new_group("the_group")
        to_delete.append("the_group")
        # create ssh key
        punkr.new_ssh_key("test_key")
        to_delete.append("test_key")
        # listing
        res = punkr.list_secrets()
        assert len(res["content"]["secrets"]) > 0
        res = punkr.list_devices()
        assert len(res["devices"]) > 0
        res = punkr.list_groups()
        assert len(res["groups"]) > 0

        # rename
        punkr.rename("the_group", "useless_group")
        punkr.rename("useless_group", "the_group")

        # create, write, access cycle
        content = "some useless content"
        punkr.create("useless_secret", SecretType.GenericGF256)
        punkr.write("useless_secret", content, "text")
        to_delete.append("useless_secret")

        res = punkr.access("useless_secret")
        assert res["content"] ==  content
        assert res["mode"] == "text"

        # granting
        punkr.grant("the_group", "useless_secret")
        # revoke
        punkr.revoke("the_group", "useless_secret")

        # reset triples
        punkr.reset_triples("useless_secret")
        # noop
        punkr.noop("useless_secret")
        # secret info
        res = punkr.secret_info("useless_secret")
        print(res["msg"])

        # ecdsa signature
        res = punkr.sign_ecdsa("test_key", "Zm9v")
        print(res["r"])
        print(res["s"])

        # ssh public data
        res = punkr.ssh_public_data("test_key")
        print(res["public_data"]["public_key"])

        # send device
        res = punkr.send_device("my_device")
        print(res["url_short"])
        print(res["url_raw"])

    except PunkrException as e:
        print("Error while performing a Bunkr operation:")
        print(e)
    except Exception as e:
        print(e)
    finally:
        # delete the secret (synchronously)

        for s in to_delete:
            try:
                punkr.delete(s)
            except PunkrException as e:
                print(f"Error deleting secret {s}: {e}")