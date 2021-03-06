# GenerateXcus

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/generatexcs.py">generatexcs.py</a>

This is the LibreOffice Python macro that creates the following 6 xcs files from xcd files in the share/registry folder.

<a href="https://github.com/p--q/GenerateXcus/tree/master/GenerateXcus/src/xcs">GenerateXcus/GenerateXcus/src/xcs</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/ProtocolHandler.xcs">ProtocolHandler.xcs
</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/Jobs.xcs">Jobs.xcs
</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/OptionsDialog.xcs">OptionsDialog.xcs
</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/Addons.xcs">Addons.xcs
</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/CalcWindowState.xcs">CalcWindowState.xcs</a>

- <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs/WriterWindowState.xcs">WriterWindowState.xcs
</a>

These xcs files are output to the xcs folder under the folder containing this Python macro file.

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcs2xml.py">xcs2xml.py
</a>

This Python script expands the templates node of the component node of the component schema node in the xcs files.

The expanded component schema node is output to the xml file in the xml folder.

<a href="https://github.com/p--q/GenerateXcus/tree/master/GenerateXcus/src/xml">GenerateXcus/GenerateXcus/src/xml</a>

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xml2ini.py">xml2ini.py
</a>

This Python script will output the ini file to the ini/template folder based on the xml file created in xcs2xml.py.

This ini file can be read by <a href="https://docs.python.org/3.5/library/configparser.html#module-configparser">14.2. configparser — Configuration file parser — Python 3.5.5 documentation</a>.

<a href="https://github.com/p--q/GenerateXcus/tree/master/GenerateXcus/src/ini/template">GenerateXcus/GenerateXcus/src/ini/template</a>

### <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/ini2xcu.py">ini2xcu.py
</a>

This Python script creates an xcu file from an ini file.

Puts the ini file with values created by xml2ini.py in the ini folder.

To output the xcu file, you need the xml file created by xcs2xml.py, which is in the xml folder.

Create <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xcu/OptionsDialog.xcu">OptionsDialog.xcu
</a> from <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/ini/OptionsDialog.ini">OptionsDialog.ini
</a> and <a href="https://github.com/p--q/GenerateXcus/blob/master/GenerateXcus/src/xml/OptionsDialog.xml">OptionsDialog.xml
</a>, for example.
