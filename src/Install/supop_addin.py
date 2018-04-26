# Import all required modules
import pythonaddins  # ESRI Module which provides access to Python Add-In functions
import os            # Module which provides access to low-level Operating System functions

class ODTA(object):
    """
    Implementation for ODTA (Button)
    Invoked whenever the user presses the ODTA button
    """

    def __init__(self):
        """ Defines the button's settings at initialization """
        # Run isGISAdmin to determine if user can run tool
        self.enabled = True
        # Button is not pressed by default
        self.checked = False

    def onClick(self):
        """ Defines what actions/events occur when the button is clicked by the user """
        # Lookup the directory to where this file is located on the local system and
        # append to the end of that result, the directory, 'TBX' followed by the name
        # of the Toolbox File, 'GeoWhiz.pyt' as store this result as 'ToolboxPath'
        ToolboxPath = os.path.dirname(__file__) + r"\TBX\retop.pyt"
        # Establish the 'ToolName' as the name of the tool within the toolbox to be
        # called
        ToolName = "ODTA"
        # Raise the Dialog of the given Tool ('ToolName') hosted within the given
        # Toolbox ('ToolboxPath')
        try:
            pythonaddins.GPToolDialog(ToolboxPath, ToolName)
        except Exception as e:
            pythonaddins.MessageBox(e.message)
            pass


