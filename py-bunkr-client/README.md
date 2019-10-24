# Punkr


Punkr (Python Bunkr) is a python wrapper around the RPC server running within the Bunkr daemon. It requires the daemon to be running to send the Bunkr operations.

## Install

Install punkr with pip:
`$ pip install punkr`

*Compatible with python 3.6+*

#### Punkr class

`Punkr` class is the main structure to use. It can work either synchronously or asynchronously. All methods have their async replica, they can be identified by the `async_*` prefix in the method names.
* new-text-secret       -> create a new secret whose content is a simple text
* new-ssh-key           -> create a new secret whose content is an ECDSA ssh key
* new-file-secret       -> dump a file content as a new secret
* new-group             -> create a new group
* import-ssh-key        -> import an ssh key from a file into a secret
* list-secrets          -> list all stored secrets
* list-devices          -> list all shared devices
* list-groups           -> list all tracked groups
* send-device           -> share the current Bunkr device
* receive-device        -> import a shared Bunkr device
* remove-device         -> remove a shared device reference from Bunkr
* remove-local          -> untrack a secret, it does not delete the secret from the plattform
* rename                -> rename a secret, device or group
* create                -> create a new empty secret
* write                 -> write a secret with new content
* access                -> retrieve the content of a secret
* grant                 -> grant capabilities to a group or device for an specified secret or group
* revoke                -> revoke a given capability
* delete                -> erase a secret existence
* receive-capability    -> import a capability for a given secret
* reset-triples         -> synchronize triples for a secret
* noop-test             -> health check operation over a secret
* secret-info           -> get secret public information
* sign-ecdsa            -> make an ECDSA signature with a ECDSA Bunkr secret
* ssh-public-data       -> retrieve a secret public data
* signin                -> signin into the platfform
* confirm-signin        -> confirm the signin process

## Examples

```python
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
```





Copyright (c) [2019] [Off-the-grid-inc]
