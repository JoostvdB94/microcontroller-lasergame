# microcontroller-lasergame
Github project that contains a starter simulation for a lasergame

## Import ``iotc``
      In most of the micropython capable boards, is sufficient to import library or install it if missing through upip.

      ```py
      try:
          import iotc
      except:
          import upip
          upip.install('micropython-iotc')
          import iotc
      ```

If running locally, you can download and unpack the following file to /lib/ in the root of your solution
https://files.pythonhosted.org/packages/f9/2a/bc30d6ee3665ea68690695aee0e15118203a1643fc3fc180be7b72f893b5/micropython-iotc-1.1.0.tar.gz

## Connecting
Currently only connection through Shared Access Keys is supported.
You can use both device keys or group keys.

### Init
```py
from iotc import IoTCConnectType
id_scope = 'scopeID'
device_id = 'device_id'
sasKey = 'masterKey' # or use device key directly
conn_type=IoTCConnectType.SYMM_KEY # or use DEVICE_KEY if working with device keys
client = IoTCClient(id_scope, device_id, conn_type, sasKey)
```

You can pass a logger instance to have your custom log implementation. (see [#Logging](#logging))

e.g.

```py
from iotc import ConsoleLogger,IoTCLogLevel
logger = ConsoleLogger(IoTCLogLevel.ALL)
client = IoTCClient(id_scope, device_id, conn_type, sasKey, logger)
```

### Connect

```py
client.connect()
```
After successfull connection, IOTC context is available for further commands.

## Operations

### Send telemetry

```py
client.send_telemetry(payload,properties=None)
```

e.g. Send telemetry every 3 seconds
```py
while client.is_connected():
    print('Sending telemetry')
    client.send_telemetry({'temperature':randint(0,20),'pressure':randint(0,20),'acceleration':{'x':randint(0,20),'y':randint(0,20)}})
    sleep(3)
```
An optional *properties* object can be included in the send methods, to specify additional properties for the message (e.g. timestamp,etc... ).
Properties can be custom or part of the reserved ones (see list [here](https://github.com/Azure/azure-iot-sdk-csharp/blob/master/iothub/device/src/MessageSystemPropertyNames.cs#L36)).

> **NOTE:** Payload content type and encoding are set by default to 'application/json' and 'utf-8'. Alternative values can be set using these functions:<br/>
_iotc.set_content_type(content_type)_ # .e.g 'text/plain'
_iotc.set_content_encoding(content_encoding)_ # .e.g 'ascii'
        
### Send property update
```py
client.send_property({'fieldName':'fieldValue'})
```

## Listen to events
Due to limitations of the Mqtt library for micropython, you must explictely declare your will to listen for incoming messages. This client implements a non-blocking way of receiving messages so if no messages are present, it will not wait for them and continue execution.

To make sure your client receives all messages just call _listen()_ function in your main loop. Be aware that some sleeping time (200 ms +) is needed in order to let the underlying library listen for messages and release the socket.

  ```py
  while client.is_connected():
      client.listen() # listen for incoming messages
      client.send_telemetry(...)
      sleep(3)
  ```
  You also need to subscribe to specific events to effectively process messages, otherwise client would just skip them (see below).

### Listen to properties update
Subscribe to properties update event before calling _connect()_:
```py
client.on(IoTCEvents.PROPERTIES, callback)
```
To provide property sync aknowledgement, the callback must return the 
property value if has been successfully applied or nothing.

e.g.
```py
def on_props(prop_name, prop_value, component):
    if prop_value>10:
        # process property
        return prop_value

client.on(IoTCEvents.PROPERTIES, on_props)
```

### Listen to commands
Subscribe to command events before calling _connect()_:
```py
client.on(IoTCEvents.COMMANDS, callback)
```
To provide feedbacks for the command like execution result or progress, the client can call the **ack** function available in the callback.

The function accepts 1 command argument: the command instance.
```py
def on_commands(command):
print(command.name)
command.reply()

client.on(IoTCEvents.COMMANDS, on_commands)
  ```
Call `reply()` to send an acknoledge back.

### How to set IoTC template ID in your device
Device template id (a.k.a Model Id) is used when obtaining authorization codes for new devices and automatically assign them to the right template. By providing template id during credentials generation, user doesn't need to manually migrate or assign device from IoT Central site.

In order to get the unique identifier, open configuration page for required model under "Device templates" section.
![Img](https://github.com/iot-for-all/iotc-micropython-client/tree/master/assets/modelId.png)

Click on "View Identity" and in next screen copy model urn.
![Img](https://github.com/iot-for-all/iotc-micropython-client/tree/master/assets/modelId_2.png)


Then call this method before connect():

```py
client.set_model_id(model_id)
```

 ### Automatic approval (default)
By default device auto-approval in IoT Central is enabled, which means that administrators don't need to approve device registration to complete the provisioning process when device is not already created.


### Manual approval
If auto-approval is disabled, administrators need to manually approve new devices.
This can be done from explorer page after selecting the device
