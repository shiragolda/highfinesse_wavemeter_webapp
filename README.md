# minimal wavemeter webserver

A simple python webserver that fetches the frequency from the HighFinesse WS8 wavemeter and sends it to any computer or phone in your network. 

See https://github.com/shiragolda/highfinesse_wavemeter for details about the linux backend. 

## Quick start

Requires [tornado framework](http://www.tornadoweb.org/en/stable/). You can install it via:

```
pip install tornado
```

To start the sudo server, you will need:

- Windows computer with HighFinesse software installed and running and wavemeter_wrapper.py running
   OR
- Windows computer with HighFinesse software installed and running and wlmDataServer.exe running (executable from HighFinesse) AND Linux computer with wavemeter_wrapper.py running

Just run in the command line:

```
python3 sudo_server.py
```

Web interface will be available on [http://localhost:8000](http://localhost:8000)


