# minimal wavemeter webserver

A simple python webserver that fetches the frequency from the HighFinesse WS8 wavemeter and sends it to any computer or phone in your network. 

See https://github.com/shiragolda/highfinesse_wavemeter for details about the linux backend. 

## Requirements

[tornado framework](http://www.tornadoweb.org/en/stable/). 
pyzmq
ctypes

You can install it via:

```
pip install tornado, ctypes, pyzmq
```

To start the webapp you will need:

- Windows computer with HighFinesse software installed
   OR
- Windows computer with HighFinesse software installed and running and wlmDataServer.exe running (executable from HighFinesse) AND Linux computer with libwlmData.so library installed (library from HighFinesse)


Just run in the command line:

```
python3 wavemeter_webapp.py
```

Web interface will be available on [http://localhost:8000](http://localhost:8000)


