# Punkr


Punkr (Python Bunkr) is a python wrapper around the RPC server running within the Bunkr daemon. It requires the daemon to be running to send the Bunkr operations.

## Install

Install punkr with pip:
`$ pip install punkr`

*Compatible with python 3.6+*

#### Punkr class

`Punkr` class is the main structure to use. It can work either synchronously or asynchronously. All methods have their async replica, they can be identified by the `async_*` prefix in the method names.

The available commands are:

* create
* write
* access
* delete
* new-text-secret
* sign-ecdsa


## Examples

```python
if __name__ == "__main__":
    import asyncio
    from punkr import Punkr, PunkrException
    
    # create a connection to the local Bunkr RPC server
    punkr = Punkr("127.0.0.1", 7860)
    try:
        # create a new text secret (synchronously)
        print(punkr.new_text_secret("MySuperSecret", "secret created from punkr"))
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
        results2 = punkr.batch_commands(*commands)
        print(results2)
        assert results1 == results2
    except PunkrException as e:
        print(e)
    finally:
        # delete the secret (synchronously)
        punkr.delete("MySuperSecret")
```





Copyright (c) [2019] [Off-the-grid-inc]
