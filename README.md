# GenerateXcus

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/generatexcs.py">generatexcs.py</a>

This is the LibreOffice Python macro that creates the following 6 xcs files from xcd files in the share/registry folder.

- OptionsDialog.xcs

- ProtocolHandler.xcs

- Addons.xcs

- Jobs.xcs

- CalcWindowState.xcs

- WriterWindowState.xcs

These xcs files are output to the xcs folder under the folder containing this Python macro file.

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs2xml.py">xcs2xml.py
</a>

This Python script expands the templates node of the component node of the component schema node in the xcs files.

The expanded component schema node is output to the xml file in the xml folder.

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xml2ini.py">xml2ini.py
</a>

This Python script will output the ini file to the ini folder based on the xml file created in xcs2xml.py.

This ini file can be read by <a href="https://docs.python.org/3.5/library/configparser.html#module-configparser">14.2. configparser — Configuration file parser — Python 3.5.5 documentation</a>.



