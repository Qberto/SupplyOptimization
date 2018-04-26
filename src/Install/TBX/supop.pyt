import arcpy
import os


def ArcGISVersionChecker():
    """
    Determines the version of ArcGIS Desktop that the user has installed and returns outputs based on the input parameter
    :args:
    :return:
    desktop_version (string) - String corresponding to the full version of ArcGIS Desktop
    guid_folder (string) - String corresponding to the installation GUID key
    program_files_folder (string) - String corresponding to the program files folder based on the version
    """
    installer_folder = r"C:\Windows\Installer"  # Establishes a path to the default Windows installer folder

    # Establishes a version dictionary containing the guid values and program files folder corresponding to each
    # version of ArcGIS Desktop
    arcgis_version_dictionary = {
    "ArcGIS_10.5": {"guid": "{76B58799-3448-4DE4-BA71-0FDFAA2A2E9A}", "program_files_folder": "Desktop10.5"},
    "ArcGIS_10.3.1": {"guid": "{831DD630-F230-49C6-AD41-312E8E0F9CEE}", "program_files_folder": "Desktop10.3"},
    "ArcGIS_10.3": {"guid": "{9A0BC33A-EAA8-4ED4-8D0C-CB9B42B06D7F}", "program_files_folder": "Desktop10.3"},
    "ArcGIS_10.2.2": {"guid": "{761CB033-D425-4A16-954D-EA8DEF4D053B}", "program_files_folder": "Desktop10.2"},
    "ArcGIS_10.2.1": {"guid": "{8777990C-4F53-4782-9A38-E60343B5053D}", "program_files_folder": "Desktop10.2"},
    "ArcGIS_10.2": {"guid": "{44EF0455-5764-4158-90B3-CA483BCB1F75}", "program_files_folder": "Desktop10.2"},
    "ArcGIS_10.1": {"guid": "{6C8365F4-1102-4064-B696-68842D20B933}", "program_files_folder": "Desktop10.1"}
    }

    """ Main iteration """
    # Iterate on each key in the arcgis_version_dictionary
    for version in arcgis_version_dictionary:
        # Create the installer_path variable by linking it to the installer_folder string
        installer_path = str(installer_folder) + "\\" + str(arcgis_version_dictionary[version]["guid"])

        # Perform verification to determine if the installer_path exists
        if arcpy.Exists(installer_path):
            # Designate the desktop_version variable for output
            desktop_version = str(version)
            # Designate the guid_folder folder for output
            guid_folder = arcgis_version_dictionary[version]["guid"]
            # Designate the program_files_folder variable for output
            program_files_folder = arcgis_version_dictionary[version]["program_files_folder"]

            # Break iteration upon the first installation folder found in sequence from newest to oldest
            break

        else:
            desktop_version = None
            guid_folder = None
            program_files_folder = None

    #TODO Check Business Analyst data

    #TODO Check BG Geoprocessing result

    return desktop_version, guid_folder, program_files_folder


def NetworkDatasetFinder():
    DesktopVersion = ArcGISVersionChecker()[2]
    in_NetworkDataset = None
    if DesktopVersion == "Desktop10.5" or DesktopVersion == "Desktop10.3":
        if os.path.exists(r"C:\ArcGIS\Business Analyst\US_2017"):
            in_NetworkDataset = r"C:\ArcGIS\Business Analyst\US_2017\Data\Streets Data\NorthAmerica.gdb\Routing\Routing_ND"    	
        elif os.path.exists(r"C:\ArcGIS\Business Analyst\US_2015"):
            in_NetworkDataset = r"C:\ArcGIS\Business Analyst\US_2015\Data\Streets Data\NAVTEQ_2014_Q3_NA.gdb\Routing\Routing_ND"
        elif os.path.exists(r"C:\ArcGIS\Business Analyst\US_2014"):
            in_NetworkDataset = r"C:\ArcGIS\Business Analyst\US_2014\Data\Streets Data\NAVTEQ_2014_Q1_NA.gdb\Routing\Routing_ND"
    elif DesktopVersion == "Desktop10.2":
        in_NetworkDataset = r"C:\ArcGIS\Business Analyst\US_2013\Data\Streets Data\NAVTEQ_2013_Q1_NA.gdb\Routing\Routing_ND"
    return in_NetworkDataset


def get_subgeography_id_from_point(point_fc, point_id_field, point_id, subgeography_fc, subgeography_id_field):
    """
    Extracts the subgeography id that a point feature resides on

    :param point_fc: Point feature class containing the record to check subgeography ID
    :param point_id_field: Field in point feature class designating the point unique ID
    :param point_id: Current ID in iteration
    :param subgeography_fc: Feature class containing the subgeography coverage that the point resides on
    :param subgeography_id_field: Field in subgeography feature class containing the subgeography unique ID value
    :return: ID for the subgeography record that the point_id record resides on
    """

    arcpy.env.overwriteOutput = True

    method_message = "get_subgeography_id_from_point: "

    arcpy.AddMessage(
        "\t\t\t\t" + "get_subgeography_id_from_point: Determining ID of subgeography record containing ID " + str(
            point_id) + "...")
    # Create where_clause to select the point_id value from the point_fc
    # during the generation of a point_ly feature layer
    where_clause = arcpy.AddFieldDelimiters(point_fc, str(point_id_field)) + " = '" + str(point_id) + "'"

    # Perform verification/deletion of existing feature layer
    if arcpy.Exists("point_lyr"):
        arcpy.Delete_management("point_lyr")

    # Create 'point_ly' feature layer from point_fc to facilitate selections
    # against the dataset
    arcpy.MakeFeatureLayer_management(point_fc, "point_lyr", where_clause)

    # Perform verification that point_lyr contains one record
    count = int(arcpy.GetCount_management("point_lyr").getOutput(0))
    if count == 1:
        pass
    elif count > 1:
        arcpy.AddMessage(method_message + "WARNING: Destination ID " + str(
            point_id) + " provided resulted in a selection of more than one record. Verify that the Destination ID field in the destinations Feature Class has unique values.")
    else:
        arcpy.AddMessage(method_message + "ERROR: Destination ID " + str(
            point_id) + " provided resulted in NO records from a selection in the Destinations feature class. Verify that your Destinations feature class was correctly generated and that the Destination ID is valid.")

    # Perform verification/deletion of existing feature layer
    if arcpy.Exists("subgeography_lyr"):
        arcpy.Delete_management("subgeography_lyr")

    # Create 'subgeography_ly' feature layer from subgeography_fc to
    # facilitate selections against the dataset
    arcpy.MakeFeatureLayer_management(subgeography_fc, "subgeography_lyr")

    # Create a "selectLayerByLocation" analysis to determine the
    # subgeography record that the point resides on
    arcpy.SelectLayerByLocation_management("subgeography_lyr", "CONTAINS", "point_lyr", "", "NEW_SELECTION")

    # Read the subgeograhy_id_field value for the selected subgeography
    # record and return
    with arcpy.da.SearchCursor("subgeography_lyr", subgeography_id_field) as cursor:
        for row in cursor:
            subgeography_id = str(row[0])
    arcpy.AddMessage(method_message + "Subgeography ID is " + subgeography_id)
    return subgeography_id


def append_struct_to_nparray(target_array, struct_name, struct_data_array="zeroes", dtype=None):
    """
    Appends a struct (field) to a structured array
    :param target_array: Structured array that the struct will be appended to
    :param struct_name: Name of the struct to be appended
    :param struct_data_array: Array containing data to populate the new struct
    :param dtype: Defaults to None. Data type of the new struct to be appended
    :return: New structured array containing the appended struct
    """
    import numpy as np
    # Determine if the default struct_data_array was submitted
    if struct_data_array == "zeroes":
        # Generate a zeroes array of len = target_array
        struct_data_array = np.zeros(len(target_array))
    # Otherwise, if the user provided their own struct_data_array
    else:
        # Ensure the struct_data_array is an array
        struct_data_array = np.asarray(struct_data_array)
    # If the dtype parameter is not changed
    if dtype is None:
        # data type will be inherited from the struct_data_array data type
        dtype = struct_data_array.dtype
    # Create a new data type object by reading the target_array and
    # appending the struct_name and dtype
    newdtype = np.dtype(target_array.dtype.descr + [(struct_name, dtype)])
    # Create a new empty array
    newarray = np.empty(target_array.shape, dtype=newdtype)
    # Hydrate the new empty array with the fields in the target_array
    for field in target_array.dtype.fields:
        newarray[field] = target_array[field]
    # Hydrate the new array with the struct_data_array data
    newarray[struct_name] = struct_data_array
    #TODO Determine if input arrays that are not needed after creating the newarray object can be deleted
    #TODO May be able to add parameter to designate input array deletion
    # Return the new array
    return newarray

def MessageBox(Title, Message, ButtonStyle=0, MessageboxType="NOICON"):
    """
    Raises a custom messagebox with the given title and message
    with the specified ButtonStyle and MessageboxType

    Value                    ButtonType
        0                        OK (Default)
        1                        OK | Cancel
        2                        Abort | Retry | Ignore
        3                        Yes | No | Cancel
        4                        Yes | No
        5                        Retry | No
        6                        Cancel | Try Again | Continue

    Value                    MessageboxType
        NOICON                   No Icon (Default)
        INFO                     Information Icon
        QUESTION                 Question Mark Icon
        WARNING                  Warning Exclamation
        ERROR                    Error Icon

    Returns an integer value indicating the button in the Messagebox pressed by the user

    Return Value             Button Pressed
        1                        OK
        2                        Cancel
        3                        Abort
        4                        Retry
        5                        Ignore
        6                        Yes
        7                        No
        10                       Try Again
        11                       Continue

    Usage:
        MessageBox("ASK QUESTION?", "Would you like to ask a question?", 4, "QUESTION")
    """
    if MessageboxType == "NOICON":
        MB_STYLE = 0x00
    elif MessageboxType == "INFO":
        MB_STYLE = 0x40
    elif MessageboxType == "QUESTION":
        MB_STYLE = 0x20
    elif MessageboxType == "WARNING":
        MB_STYLE = 0x30
    elif MessageboxType == "ERROR":
        MB_STYLE = 0x10
    else:
        raise Exception("Value given for 'MessageboxType' parameter is not valid")

    if ButtonStyle not in range(0, 7):
        raise Exception("Value given for 'ButtonStyle' parameter is not valid")

    import ctypes

    buttonPressed = ctypes.windll.user32.MessageBoxA(0, Message, Title, ButtonStyle | MB_STYLE | 0x40000)
    return buttonPressed

#========================================================================================#
#                                  TOOLBOX INITIALIZATION                                #
# Define the Toolbox Class to serve as a container for its associated tools              #
#========================================================================================#
class Toolbox(object):
    def __init__(self):
        """
        Toolbox Initialization Settings
        This function is invoked whenever ArcGIS Software is initialized and defines
        what is displayed within the ArcToolbox.
        """
        # Assign the Toolbox Label
        self.label = "Supply Optimization Analysis"
        # Assign the Toolbox alias used to call the toolbox programmatically
        self.alias = "SupOp"
        # List of the tools contained within the Toolbox
        self.tools = [ODTA]


# Define a class to perform diff checks on input dictionaries
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


"""Create an instance of the ODTA Tool"""


class ODTA(object):
    # Create the tool's 'Intialize' function, which is executed when the tool is initialized.
    def __init__(self):
        self.category = "Exploration Tools"
        self.label = "Origin-Destination Trade Area"
        self.description = ""
        self.canRunInBackground = True

    def user(self):
        """Returns as a string the Login ID of the User on the Host System"""
        from getpass import getuser
        # Get the login ID of the current user and convert the characters to lowercase
        User = getuser().lower()
        # Return the value held in the 'User' variable
        return User

    """Establish the Tool parameters."""

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Workspace (Folder)",
            name="in_workspace",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Destinations Feature Class",
            name="in_AOIs",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Point"]

        param2 = arcpy.Parameter(
            displayName="Destination ID Field",
            name="in_AOI_IDField",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param2.filter.list = ["TEXT"]
        param2.parameterDependencies = [param1.name]

        param3 = arcpy.Parameter(
            displayName="Destination Score Field",
            name="in_AOI_SjField",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param3.filter.list = ["Double", "Long", "Short"]
        param3.parameterDependencies = [param1.name]

        # Beta checkbox for field vs analysis beta
        param4 = arcpy.Parameter(
            displayName="Use 'Beta' field within input dataset",
            name="use_beta_field",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")
        param4.value = False

        # Friction of Distance parameter
        param5 = arcpy.Parameter(
            displayName='Friction of Distance (Beta)',
            name="in_beta",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        param5.value = 1.25

        # Impedance Cutoff parameter
        param6 = arcpy.Parameter(
            displayName="Impedance Cutoff Value",
            name="in_impedanceCutoff",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param6.value = 15
        param6.category = "Impedance Cutoff"

        param7 = arcpy.Parameter(
            displayName="Impedance Cutoff Attribute",
            name="in_impedanceAttribute",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param7.filter.type = "ValueList"
        param7.filter.list = ["Minutes", "Miles", "TravelTime", "Kilometers"]
        param7.value = "TravelTime"
        param7.category = "Impedance Cutoff"

        param8 = arcpy.Parameter(
            displayName="Decay Index used to calculate Market Div50 Value",
            name="in_decayIndex",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param8.value = 4
        param8.category = "Distance Decay Index / Div50"

        param9 = arcpy.Parameter(
            displayName="Market Div50 Value (Using Index of 4)",
            name="in_div50",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param9.value = 16.5
        param9.category = "Distance Decay Index / Div50"

        param10 = arcpy.Parameter(
            displayName="CBSA Boundary Extension (Miles)",
            name="CBE",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param10.value = 0
        param10.category = "Business Constraints"

        param11 = arcpy.Parameter(
            displayName="ODTA Minimum Demand Threshold (%)",
            name="MDT",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        # Apply a default value
        param11.value = 0
        param11.category = "Business Constraints"

        param12 = arcpy.Parameter(
            displayName="Draw Trade Areas",
            name="drawODTA",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")
        param12.value = True
        param12.enabled = False

        param13 = arcpy.Parameter(
            displayName="Use Default Origin BG Points Feature Class",
            name="in_defaultDemandBGs",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param13.value = False
        param13.category = "Alternative Block Group Demand"

        param14 = arcpy.Parameter(
            displayName="Origin Point Feature Class",
            name="in_demandBGs",
            datatype="Feature Layer",
            parameterType="Optional",
            direction="Input")
        param14.filter.list = ["Point"]
        param14.category = "Origin Data"

        # anchorSite ID Field Parameter
        param15 = arcpy.Parameter(
            displayName="Origin ID Field",
            name="in_altIDField",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param15.category = "Origin Data"
        param15.filter.list = ["TEXT"]
        param15.parameterDependencies = [param14.name]

        param16 = arcpy.Parameter(
            displayName="Origin Value Field",
            name="in_altDemandField",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param16.category = "Origin Data"
        param16.filter.list = ["Double", "Long"]
        param16.parameterDependencies = [param14.name]

        param17 = arcpy.Parameter(
            displayName="Market Name (City or Metropolitan Area)",
            name="in_marketName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param18 = arcpy.Parameter(
            displayName="Cumulative Trade Area Percentage",
            name="in_demandPercentage",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param18.value = 100
        param18.category = "Basis for Cumulative Trade Area"

        param19 = arcpy.Parameter(
            displayName="Basis for Cumulative Trade Area Percentage",
            name="in_demandPercentageBasis",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param19.filter.type = "ValueList"
        param19.filter.list = ["Demand Allocation", "Demand Share"]
        param19.value = "Demand Allocation"
        param19.category = "Basis for Cumulative Trade Area"

        param20 = arcpy.Parameter(
            displayName="Artificially include home block group in each ODTA",
            name="in_homeBG_flag",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param20.category = "Business Constraints"
        param20.value = True

        param21 = arcpy.Parameter(
            displayName="Artificially include block groups that contribute above a demand percentage threshold in each ODTA",
            name="in_dptBG_flag",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param21.category = "Business Constraints"
        param21.value = True

        param22 = arcpy.Parameter(
            displayName="Demand Percentage Threshold",
            name="in_dbtBG_value",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        param22.category = "Business Constraints"
        param22.value = 95

        param23 = arcpy.Parameter(
            displayName="Reverse ODTA (Pij Prime)",
            name="pijprime",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param23.category = "Business Constraints"
        param23.value = False

        param24 = arcpy.Parameter(
            displayName="Analysis Boundary Feature Class",
            name="in_analysisbdryfc",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input")
        param24.filter.list = ["Polygon"]
        param24.category = "Analysis Boundary Data"

        param25 = arcpy.Parameter(
            displayName="Analysis Boundary FC ID Field",
            name="in_analysisbdryfcidfield",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param25.filter.list = ["TEXT"]
        param25.category = "Analysis Boundary Data"
        param25.parameterDependencies = [param24.name]

        param26 = arcpy.Parameter(
            displayName="Origin Polygon Feature Class",
            name="in_originPolys",
            datatype="Feature Layer",
            parameterType="Optional",
            direction="Input")
        param26.filter.list = ["Polygon"]
        param26.category = "Origin Data"



        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10,
                  param11, param12, param13, param14, param15, param16, param17, param18, param19, param20,
                  param21, param22, param23, param24, param25, param26]
        return params


    """Determine whether or not the tool is licensed and can be executed according to what user is logged into the executing system and
       the machine's operating system and platform architecture"""

    def isLicensed(self):
        if arcpy.CheckExtension("Network") != "Available":
            MessageBox("License Error", "A network analyst license is not available; the tool cannot be executed.")
            return False
        else:
            arcpy.CheckOutExtension("Network")
            return True

    # Method to verify if the layer contains a join
    def join_check(self, lyr):
        field_list = arcpy.Describe(lyr).fields
        for field in field_list:
            if field.name.find(lyr.datasetName) > -1:
                return True
            return False

    """Enable/Disable parameters dynamically within the tool based on the user's inputs"""

    def updateParameters(self, parameters):

        # If the user changed the boolean checkbox parameter for using the Beta field within the dataset
        if parameters[4].value == False:
            parameters[5].enabled = True
        # Otherwise, param9 ('Friction of Distance') is disabled
        else:
            parameters[5].enabled = False
            parameters[5].value = None

        parameters[7].enabled = True
        parameters[8].enabled = True
        parameters[9].enabled = True

        parameters[13].enabled = False

        # If the boolean alternative demand source parameter has been checked, enable the alternative demand source
        # subparameters
        if parameters[13].value == False:
            parameters[14].enabled = True
            parameters[15].enabled = True
            parameters[16].enabled = True
        else:
            parameters[14].enabled = False
            parameters[15].enabled = False
            parameters[16].enabled = False
            # Reset the alternate demand source parameter to 'None' to prevent any entered value from being used if the
            # Boolean flag for the original demand source is True
            parameters[14].value = None

        # If the 'draw ODTAs' boolean checkbox parameter is disabled, disable the cumulative percentage fields and reset
        # the percentage value to 100
        if parameters[12].value == False:
            parameters[18].enabled = False
            parameters[19].enabled = False
            parameters[18].value = 100
        else:  # If the 'draw ODTAs' parameter is True, enable the cumulative percentage fields
            parameters[18].enabled = True
            parameters[19].enabled = True

        if parameters[19].altered:
            if parameters[19].value == "Demand Share":
                parameters[21].enabled = False
            else:
                parameters[21].enabled = True
        else:
            parameters[21].enabled = True

        # If the DPT Flag has been checked, enable the DPT value field designating the demand percentage threshold
        # contribution value to use
        if parameters[21].value == True:
            parameters[22].enabled = True

        else:
            parameters[22].enabled = False

        # Return to the top of Dynamic Parameter Handling and await any parameter amendment
        return

    ##-------------------------------------------------------------------------------------------------------##
    ##          ODTA TOOL VALIDATION                                                                         ##
    ##-------------------------------------------------------------------------------------------------------##
    def updateMessages(self, parameters):
        """ Validate that the user has all required datasets installed on their local machine"""

        in_NetworkDataset = NetworkDatasetFinder()
        
        # Establish a List of the Required Datasets
        ReqDataList = [in_NetworkDataset]
        # For each required dataset in the required dataset list:
        for ReqData in ReqDataList:
            # If the given require dataset does not exist on the system:
            if arcpy.Exists(ReqData) == False:
                # Raise a Fatal Error
                parameters[1].setErrorMessage(
                    "Required Dataset not found. The Required Dataset " + str(ReqData) + " could not be " \
                                                                                         "located on the system.")
            # Otherwise:
            else:
                print "All required datasets have been found. Proceeding..."
                # Continue
                pass

        # Verification logic for existing geodatabase conflicts using the workspace parameters
        if parameters[17].value and parameters[0].value:
            folder = str(parameters[0].value) + "\\"
            market_name = str(parameters[17].value).replace(" ", "_")
            gdbs_list = [folder + market_name + "_ODTAs.gdb"]
            for gdb in gdbs_list:
                if os.path.exists(gdb):
                    parameters[17].setErrorMessage(
                        "A ODTA output geodatabase using this market name already exists. Please change the market name or workspace folder.")
                # Otherwise, continue validation without error.
                else:
                    pass

        """ [SP] If input by the user, validate the Spatial Reference of the 'AOIs' dataset."""
        # If param1 ('AOIs') has been populated with a dataset:
        if parameters[1].value:
            # Extract the input feature's metadata as plain text for evaluation:
            p2_Desc = arcpy.Describe(parameters[1].valueAsText)
            # Extract the name of the Spatial Reference system assigned to the input dataset and give it a Variable Assignment of 'p2_SR':
            p2_SR = format(p2_Desc.spatialReference.name)
            # If value contained in 'p2_SR' is not equal to 'WGS_1984_Web_Mercator_Auxiliary_Sphere':
            if not p2_SR == "WGS_1984_Web_Mercator_Auxiliary_Sphere":
                # Raise a Fatal Error preventing the tool from executing and present the user with the following error message.
                parameters[1].setErrorMessage(
                    "Input Dataset's Spatial Reference is set to " + p2_SR + ". Input's Spatial Reference " \
                                                                             "must be set to WGS 1984 Web Mercator Auxillary Sphere. Please use the Project tool found in 'ArcToolbox | Data " \
                                                                             "Management Tools | Projections and Transformations | Feature | Project' to transform your data's Spatial Reference " \
                                                                             "to WGS 1984 Web Mercator Auxillary Sphere.")
            # Otherwise, continue validation without error
            else:
                pass

        """ [SP] If input by user, validate that the 'AOI Sites' dataset bears a field "Beta" and that the field is of the DataType
                 "DOUBLE"."""
        # If param4 ('AOI Network') has been populated with a dataset:
        if parameters[1].value:
            # has_join = self.join_check(parameters[4].value)
            # if has_join:
            #     parameters[4].setErrorMessage("The input dataset cannot contain a join.")
            # else:
            #     pass

            # If param9 ('BetaField') has been checked and validated:
            if parameters[4].value == True:

                # Scan the param4 input dataset('AOI Network') for a field named "Beta" with a DataType of "Double".
                # If found, populate it in the variable 'p4_Beta'
                try:
                    p4_Beta = arcpy.ListFields(parameters[1].valueAsText, "Beta", "DOUBLE")

                    # Scan the param4 input dataset('AOI Network') and extract every unique value found in the "Beta" field and place it
                    # into the parameter 'p4_Bset'
                    p4_BetaSet = set([r[0] for r in arcpy.da.SearchCursor(parameters[1].value, ["Beta"])])
                    # Iterate through every value in 'p4_BetaSet':
                    for val in p4_BetaSet:
                        # If a given value exceeds a value of '4':
                        if val > 4:
                            # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                            parameters[1].setErrorMessage(
                                "One or more records in the input dataset contains a value in the field ''Beta'' " \
                                "which exceeds a value of '4'. Values held in the field ''Beta'' must be greater than or equal to '0', less than " \
                                "or equal to '4' and cannot be Null.")
                        # If a given value is less than a value of '0' ('Null' values are also captured by this condition):
                        elif val < 0:
                            # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                            parameters[1].setErrorMessage(
                                "One or more records in the input dataset contains a value in the field ''Beta'' " \
                                "which is either or Negative or Null. Values held in the field ''Beta'' must be greater than or equal to '0', less " \
                                "than or equal to '4' and cannot be Null.")
                        # Otherwise, continue validation without error.
                        else:
                            pass
                except:
                    # If no items are populated in the variable 'p4_Beta':
                    ##                if len(p1_Beta) == 0:
                    # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                    parameters[1].setErrorMessage(
                        "Field ''Beta'' could not be found. Please ensure your input dataset contains a field " \
                        "named''Beta'' and that the field's DataType is set to ''DOUBLE'', or uncheck the " \
                        "'Use Beta field' checkbox and designate an analysis Beta value.")
                # Otherwise, continue validation without error.
                else:
                    pass

            else:
                pass

        # Sj Verification Logic
        """ [SP] If input by user, validate that the values held in the 'AOIs' "ID" field do not contain null values."""
        # If param2 (AOIs) has been populated with a dataset:
        if parameters[1].value and parameters[2].value:
            # Scan the param2 input dataset('AOIs') and extract every unique value found in the "Sj" field and place it into the
            # parameter 'p2_SjSet'
            with arcpy.da.SearchCursor(parameters[1].value, [parameters[2].valueAsText]) as cursor:
                for row in cursor:
                    if row[0] == None:
                        parameters[2].setErrorMessage(
                            "One or more records in the input dataset contains a NULL value in the designated 'ID' field.")
                    else:
                        pass

        # Sj Verification Logic
        """ [SP] If input by user, validate that the values held in the 'AOIs' "Sj" field do not exceed a value of 4000 and do not contain null values."""
        # If param2 (AOIs) has been populated with a dataset:
        if parameters[1].value and parameters[3].value:
            # Scan the param2 input dataset('AOIs') and extract every unique value found in the "Sj" field and place it into the
            # parameter 'p2_SjSet'
            with arcpy.da.SearchCursor(parameters[1].value, [parameters[3].valueAsText]) as cursor:
                for row in cursor:
                    if row[0] == None:
                        parameters[3].setErrorMessage(
                            "One or more records in the input dataset contains a value in the field ''Sj'' which " \
                            "is Null. Values held in the field ''Sj'' must have a value greater than '0', less than or " \
                            "equal to '1500'.")
                    elif row[0] > 1500:
                        # Raise a Warning, presenting the user with the following Warning Message to inform them of the value irregularity
                        # in the dataset.
                        parameters[3].setErrorMessage(
                            "One or more records in the input dataset contains a value in the field ''Sj'' which " \
                            "exceeds a value of '1500'. Values held in the field ''Sj'' must be greater than or equal to '0', less than or equal " \
                            "to '1500' and cannot be Null.")
                    # If a given value is less than a value of '0' ('Null' values are also captured by this condition):
                    elif row[0] <= 0:
                        # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                        parameters[3].setErrorMessage(
                            "One or more records in the input dataset contains a value in the field ''Sj'' which " \
                            "is zero or negative. Values held in the field ''Sj'' must be greater than or equal to '0', less than or " \
                            "equal to '1500' and cannot be Null.")
                    # Otherwise, continue validation without error.
                    else:
                        pass

        """ [SP] Validate that the user has not left the 'CBSA Boundary Extension' parameter empty."""
        # If param4 ('CBSA Boundary Extension') is empty:
        if parameters[10].value == None:
            # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
            parameters[10].setErrorMessage("'CBSA Boundary Extension' parameter cannot be left blank. If you do not want to extend the \
            CBSA Boundary, please enter a value of '0'.")

        """ [SP] Validate the the value populated in the 'CBSA Boundary Extension' parameter is within established thresholds."""
        # If param4 ('CBSA Boundary Extension') is populated with a value:
        if parameters[10].value:
            # If the given value is less than a value of '0':
            if parameters[10].value < 0:
                # Raise a Fatal Error, preventing the tool from executing and present the following error message to the user.
                parameters[10].setErrorMessage("'CBSA Boundary Extension' parameter cannot be a negative value. This creates an illegal \
                operation which creates inverse buffer which shrinks the actual CBSA Boundary.  If you do not want to extend the CBSA \
                Boundary, please enter a value of '0'.")
            # If the given value is greater than '5':
            elif parameters[10].value > 5:
                # Raise a Fatal Error, preventing the tool from executing and present the following error message to the user.
                parameters[10].setErrorMessage("'CBSA Boundary Extension' parameter cannot exceed a value of '5.0' miles due to the \
                Origin-Destination Cost Matrix limitation of 5 Miles.")

        """ [SP] Validate that the user has not left the 'Minimum Demand Threshold (%)' parameter empty."""
        # If param5 ('Minimum Demand Threshold') is empty:
        if parameters[11].value == None:
            # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
            parameters[11].setErrorMessage("Minimum Demand Threshold parameter must be populated with a value greater than or equal to \
            '0' but less than '1'. The default value is '0.15'.")
        else:
            # If the given value is less than a value of '0':
            if parameters[12].value < 0:
                # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                parameters[12].setErrorMessage("Minimum Demand Threshold parameter must be populated with a value greater than or equal \
                to '0' but less than '1'. The default value is '0.15'.")
            # If the given value is greater than a value of '1':
            if parameters[12].value > 1:
                # Raise a Fatal Error, preventing the tool from executing and present the user with the following error message.
                parameters[12].setErrorMessage("Minimum Demand Threshold parameter must be populated with a value greater than or equal \
                to '0' but less than '1'. The default value is '0.15'.")

        # End of Validation: Return to top of 'updateMessages' validation function and await amendment to any parameter.
        return

    # Method used to perform ranking designation based on the values of an attribute table field
    def rankDemand(self, table, rankedField, newRankField, order):
        demand_rank = 1
        rows = arcpy.UpdateCursor(table, "", "", "", str(rankedField) + " " + str(order))
        for row in rows:
            row.setValue(newRankField, demand_rank)
            demand_rank += 1
            rows.updateRow(row)

    # Method used to retrieve the median of a list of values
    def GetMedian(self, in_list):
        sorted_list = sorted(in_list)
        median = int(round(len(sorted_list) / 2))
        if len(sorted_list) % 2 == 0:
            med_val = float(sorted_list[median - 1]
                            + sorted_list[median]) / 2
        else:
            med_val = sorted_list[median]
        return med_val

    # Method used to retrieve the lower value from a comparison of two fields and write the value to a third field
    def return_lower_value(self, dataset, fieldA, fieldB, fieldC):
        fields = [fieldA, fieldB, fieldC]
        with arcpy.da.UpdateCursor(dataset, fields) as cursor:
            for row in cursor:
                fieldA_val = row[0]
                fieldB_val = row[1]
                # Determine which value is lower between Huff Model and Distance Decay
                if fieldA_val < fieldB_val:
                    row[2] = fieldA_val
                    # arcpy.AddMessage("Comparative analysis result: "+str(fieldA)+" value was lower than "+str(fieldB)+" value; the "+str(fieldA)+" demand share value will be selected.")
                elif fieldB_val < fieldA_val:
                    row[2] = fieldB_val
                    # arcpy.AddMessage("Comparative analysis result: "+str(fieldB)+" value was lower than "+str(fieldA)+" value; the "+str(fieldB)+" demand share value will be selected.")
                elif fieldA_val == fieldB_val:
                    row[2] = fieldA_val
                    # arcpy.AddMessage("Comparative analysis result: "+str(fieldA)+" and "+str(fieldB)+" values were equal and selected.")
                else:
                    arcpy.AddMessage(
                        "ERROR during comparative analysis process. Please contact the GIS developer for assistance.")
                cursor.updateRow(row)

    def field_exists(self, feature_class, field_name):
        try:
            field_list = arcpy.ListFields(feature_class, field_name)
            field_count = len(field_list)
            if field_count == 1:
                return True
            else:
                return False
        except:
            return False

    def validate_analysis_fields(self, feature_class, fields_needed_list):

        """ [SP] Check analysis dataset for pre-existing analysis fields and generate new fields"""

        # Iterate on each of the fields to be generated and remove if it already exists
        for field in fields_needed_list:
            if self.field_exists(feature_class, str(field)):
                arcpy.AddWarning("The input destinations feature class contains a '" + str(field) + "' field.")
                arcpy.AddMessage("Removing existing '" + str(field) + "' field from dataset...")
                arcpy.DeleteField_management(feature_class, str(field))

    def add_home_bg_to_ODTA(self, point_fc, point_id_field, point_id, subgeography_fc, subgeography_id_field,
                            bg_IDs_list):
        """
        Adds the destination point's residing block group to a BGIDs list for trade area generation

        :param point_fc: Point feature class containing the record to check subgeography ID
        :param point_id_field: Field in point feature class designating the point unique ID
        :param point_id: Current ID in iteration
        :param subgeography_fc: Feature class containing the subgeography coverage that the point resides on
        :param subgeography_id_field: Field in subgeography feature class containing the subgeography unique ID value
        :param bg_IDs_list: Python array containing block group ID values used to generate the site's trade area
        """

        """ [SP] Artificial Business Constraint - Add Home BG to Trade Area """
        # Check if the home_bg flag is active

        arcpy.AddMessage("Adding artificial home block group to the Trade Area...")
        # Run logic that determines which block group ID is the home bg for the current site
        home_bg_id = get_subgeography_id_from_point(point_fc, point_id_field, point_id, subgeography_fc,
                                                    subgeography_id_field)
        arcpy.AddMessage("Home Block Group ID found: " + str(home_bg_id))
        # Add the home BG ID to the bg_IDs_list for inclusion in the site's trade area
        bg_IDs_list.append(str(home_bg_id))

        """ HOME BG - END AREA """

    def add_dpt_bg_to_ODTA(self, site_matrix, origin_id_field, demand_share_field, dpt_bg_value, bg_IDs_list):
        """
        Aritificially adds block groups meeting a demand percentage threshold

        :param site_matrix: Origin-Destination matrix for the destination's 100% ODTA
        :param origin_id_field: Field in site matrix designating the unique origin ID
        :param demand_share_field: Field in site_matrix
        :param dpt_bg_value: User-parameter designating the demand percentage contribution threshold for artificial block group inclusion in trade area
        :param bg_IDs_list: Python array containing block group ID values used to generate the site's trade area
        """

        """ [SP] Artificial Business Constraint - Add DPT BG to Trade Area """

        arcpy.AddMessage("Adding artificial demand percentage threshold block groups to the Trade Area...")
        # Iterate on the site matrix with specified fields to determine which fields contribute higher
        # demand than the designated artificial threshold
        fields = [origin_id_field, demand_share_field]
        with arcpy.da.UpdateCursor(site_matrix, fields) as cursor:
            for row in cursor:
                if row[1] >= dpt_bg_value:
                    arcpy.AddMessage("DPT BG " + str(row[0]) + " found (" + str(row[1]) + "). Adding to Trade Area...")
                    bg_IDs_list.append(str(row[0]))
                else:
                    pass

        """ DPT BG - END AREA """

    # Main execution method to calculate Origin-Destination Trade Areas. Invoked by the execute method depending on
    # the combination of input parameters provided to the tool
    def create_ODTAs(self, parameters, dataset, id_field, sj_field, input_name):
        # Assign variable references to user parameters for use in execution
        workFolder = parameters[0].valueAsText  #
        BetaField = parameters[4].value  #
        Beta = parameters[5].valueAsText  #
        DistCutoff = parameters[6].valueAsText  #
        impedanceAttribute = parameters[7].valueAsText  #
        Index = parameters[8].valueAsText  #
        div50 = parameters[9].value  #
        CBE = parameters[10].valueAsText + " Miles"  #
        MDT = parameters[11].value / 100  #
        draw_TAs = parameters[12].value  #
        alt_demand_bgs_flag = parameters[13].value  #
        alt_demand_bgs = parameters[14].valueAsText  #
        alt_demand_bgs_id_field = parameters[15].valueAsText  #
        alt_demand_bgs_demand_field = parameters[16].valueAsText  #
        marketName = parameters[17].valueAsText.replace(" ", "_")  #
        demand_percentage = parameters[18].value / 100  #
        ta_percentage_basis = parameters[19].valueAsText  #
        home_bg_flag = parameters[20].value
        dpt_bg_flag = parameters[21].value
        if dpt_bg_flag == True:
            dpt_bg_value = parameters[22].value / 100
        else:
            dpt_bg_value = None
        pij_prime = parameters[23].value


        # Set variable, impedanceAttributeField, for use during ODCM generation
        impedanceAttributeField = "Total_" + impedanceAttribute

        # Set 'DesktopVersion' variable for use in directory reference paths by invoking the ArcGISVersionChecker function
        # We need to explicitly return the index 2 result since this points to the process folder path needed for this tool
        DesktopVersion = ArcGISVersionChecker()[2]

        # Establish References to the required datasets for ODTA.
        GO_BlockGroups = parameters[26].valueAsText
        GO_CBSAs = parameters[24].valueAsText
        in_NetworkDataset = NetworkDatasetFinder()
        arcpy.AddMessage("ArcMap version: {0}".format(DesktopVersion))
        arcpy.AddMessage("Network Dataset: {0}".format(in_NetworkDataset))

        bg_id_field_name = "ID"
        # Determine if the user provided a value for the alternate source of block group demand data
        if alt_demand_bgs is not None:
            # Set variables for the ID and demand fields for the alternate source of block group demand data
            arcpy.AddMessage(
                "Demand Source Check: The user designated an alternative source of block group demand data...")
            GO_CoverageLogic = alt_demand_bgs
            origins_id_field = alt_demand_bgs_id_field
            origins_demand_field = alt_demand_bgs_demand_field

        """Execute the ODTA Model."""
        # Issue a message to the user informing that the Analysis Process is initiating and will only be executed against the dataset Network dataset.
        arcpy.AddMessage("Executing ODTA Model against " + input_name + " Network...\n")

        if dpt_bg_value:
            arcpy.AddMessage("DEVNOTE: dpt_bg_value = " + str(dpt_bg_value))

        # Creating workspace file geodatabase
        arcpy.AddMessage("Creating Workspace File Geodatabase...")
        GDB = arcpy.CreateFileGDB_management(workFolder, marketName + str("_ODTA")).getOutput(0)
        # Set the variable 'workspace' to reference the variable 'GDB'
        workspace = GDB

        # Establish the workspace
        arcpy.AddMessage("Establishing Workspace...")
        arcpy.env.workspace = workspace
        arcpy.env.overwriteOutput = True

        # Copy the dataset submitted by the user to the workspace
        arcpy.AddMessage("Copying " + input_name + " Features to Workspace...")
        arcpy.CopyFeatures_management(dataset, "input_" + input_name)

        # Overwrite the 'dataset' variable to reference the dataset that was copied to the workspace, rather than the original
        # dataset provided by the user. This prevents the users original dataset from being altered.
        dataset = workspace + "\\" + "input_" + input_name

        """ [SP] Dataset Preliminary Calculations and Preparation Processes"""
        arcpy.AddMessage("\nPreparing " + input_name + " dataset...")

        fields_needed = ["Beta_ODTA",
                         "decayAtIndex_ODTA",
                         "Div50_ODTA",
                         "DemandAlloc_HM_ODTA",
                         "Dij_Beta_ODTA",
                         "Share_ODTA",
                         "E_Share_ODTA",
                         "demandShare_HM_ODTA",
                         "demandShare_preCapped_ODTA",
                         "demandShare_DD_ODTA"
                         "demandAlloc_DD_ODTA",
                         "demandShare_Selected_ODTA",
                         "demandAlloc_MktPcnt_ODTA",
                         "demandAlloc_Selected_ODTA",
                         "origin_total_Pij",
                         "pij_prime",
                         "pij_prime_alloc"
                         ]

        self.validate_analysis_fields(dataset, fields_needed)

        # Determine if the user did not designate the execution to use an inherent 'Beta' field in the input dataset
        if BetaField == False:
            arcpy.AddMessage("\tIngesting user-provided beta of " + str(Beta) + " for analysis...")
            # Create empty 'Beta' field to contain the user-provided Beta value
            if self.field_exists(dataset, "Beta"):
                arcpy.AddMessage("Removing existing 'Beta' field from dataset...")
                arcpy.DeleteField_management(dataset, "Beta")

            arcpy.AddMessage("\tCreating 'Beta' field...")
            arcpy.AddField_management(dataset, "Beta_ODTA", "DOUBLE", 15, 5, "", "Friction of Distance (ODTA)",
                                      "NULLABLE", "REQUIRED")
            # Hydrate 'Beta' field with the user-provided parameter for friction of distance
            arcpy.AddMessage("\tCalculating 'Beta' value from user-provided parameter...")
            arcpy.CalculateField_management(dataset, "Beta_ODTA", float(Beta), "PYTHON")

        """ [SP] Logic to dynamically compute Div50 from input Sj scores """  # Removed per Analyst request to implement static Div50 logic
        # # Create Index field
        # # Create field "(Sj*Index^-beta)"
        # arcpy.AddMessage("\tCreating 'Decay At Index (Sj*Index^-beta)' field...")
        # arcpy.AddField_management(dataset, "decayAtIndex_ODTA", "DOUBLE", 15, 5, "", "Decay at Index (Sj*Index^-beta)", "NULLABLE", "REQUIRED")
        # # Calculate "(Sj*Index^-beta)" field
        # arcpy.AddMessage("\tGathering Decay@Index values from input dataset...")
        # fields = [sj_field, "decayAtIndex"]
        # decayAtIndexList = []
        # with arcpy.da.UpdateCursor(dataset, fields) as cursor:
        #     for row in cursor:
        #         # arcpy.AddMessage("\t\t***DEVNOTE - row[0] (SjField): "+str(row[0]))
        #         row[1] = row[0] * math.pow(float(Index), float(Beta)*-1)
        #         # arcpy.AddMessage("\t\t***DEVNOTE - row[1] (Sj*Dij^-b): "+str(row[1]))
        #         decayAtIndexList.append(row[1])
        #         cursor.updateRow(row)

        # arcpy.AddMessage("\tComputing Div50 (Median of all 'Sj*Index^-beta'(Decay@Index)) values...")
        # # Invoke GetMedian function to find the median value
        # medianDecayAtIndexValue = self.GetMedian(decayAtIndexList)
        # arcpy.AddMessage("\tDiv50 (Median-Sj*Index^-beta) Value Result: "+str(medianDecayAtIndexValue))
        # # Add a field to the copied retail node feature class named 'Div50_ODTA'
        # arcpy.AddField_management(dataset, "Div50_ODTA", "DOUBLE", 15, 5, "", "Div50_ODTA", "NULLABLE", "REQUIRED")
        # # Calculate Field to equal the Div50 variable 'medianDecayAtIndexValue'
        # arcpy.CalculateField_management(dataset, "Div50_ODTA", medianDecayAtIndexValue, "PYTHON")
        """ [SP-END] Logic to dynamically compute Div50 from input Sj scores """

        """ Assign static Div50 value for analysis using user-provided parameter value """
        arcpy.AddMessage("\tUsing parameter-provided Div50 value to calculate 'Div50_ODTA' field...")
        # Add a field to the copied retail node feature class named 'Div50'
        arcpy.AddField_management(dataset, "Div50_ODTA", "DOUBLE", 15, 5, "", "Div50_ODTA", "NULLABLE", "REQUIRED")
        # Calculate Field to equal the Div50 variable 'medianDecayAtIndexValue'
        arcpy.CalculateField_management(dataset, "Div50_ODTA", div50, "PYTHON")

        # Create a Feature Layer from the dataset to facilitate Spatial selections against the dataset.
        arcpy.AddMessage("\tCreating " + input_name + " Sites Feature Layer...")
        arcpy.MakeFeatureLayer_management(dataset, input_name + "_lyr")
        in_Destinations = \
            arcpy.CopyFeatures_management(dataset, str(marketName) + "_output_" + input_name + "_Sites").getOutput(0)

        # Create new field in the destinations dataset to contain the selected demand allocation value
        arcpy.AddField_management(in_Destinations,
                                  "demandAlloc_Selected_ODTA",
                                  "DOUBLE",
                                  15,
                                  5,
                                  "",
                                  "Demand Allocation (ODTA Selected)",
                                  "NULLABLE",
                                  "REQUIRED")
        # Create new field in the destinations dataset to contain the demand allocation as a percent of the total
        # market available demand
        arcpy.AddField_management(in_Destinations,
                                  "demandAlloc_MktPcnt_ODTA",
                                  "DOUBLE",
                                  15,
                                  5,
                                  "",
                                  "Percentage of Available Demand Allocated",
                                  "NULLABLE",
                                  "REQUIRED")

        arcpy.AddMessage(input_name + " dataset preparation complete.\n")

        """ [SP] Analysis Boundary Data Extraction Processes"""
        # Create a Feature Layer of the 'GO_CBSAs' dataset to facilitate Spatial selections against the dataset
        arcpy.AddMessage("Creating CBSAs Feature Layer...")
        arcpy.MakeFeatureLayer_management(GO_CBSAs, "CBSAs_lyr")

        # Select the CBSAs which have a 'dataset Network' site intersecting the given CBSAs boundary.
        arcpy.AddMessage("Selecting CBSAs intersected by " + input_name + " Network sites...")
        arcpy.SelectLayerByLocation_management("CBSAs_lyr", "INTERSECT", dataset, "", "NEW_SELECTION")

        # Export the Selected CBSAs to the user specified Workspace
        arcpy.AddMessage("Exporting selected CBSAs...")
        CBSAs = arcpy.CopyFeatures_management("CBSAs_lyr", "CBSAs").getOutput(0)

        # Dissolve the CBSAs to create our analysis boundary
        arcpy.AddMessage("Dissolving CBSA records and establishing analysis boundary...")
        analysisBoundary = arcpy.Dissolve_management(CBSAs,
                                                     marketName + "_boundary",
                                                     dissolve_field="#",
                                                     statistics_fields="#",
                                                     multi_part="MULTI_PART",
                                                     unsplit_lines="DISSOLVE_LINES").getOutput(0)
        # analysisBoundary = workspace + "\\" + marketName + "_boundary"

        arcpy.AddMessage("Creating analysis boundary Feature Layer")
        arcpy.MakeFeatureLayer_management(analysisBoundary, "analysisBoundaryLyr")

        # Create a Feature Layer from the 'GO_CoverageLogic' dataset to facilitate Spatial selections against the dataset.
        arcpy.AddMessage("Creating Coverage Logic Feature Layer...")
        arcpy.MakeFeatureLayer_management(GO_CoverageLogic, "covLogic_lyr")

        if CBE == "0 Miles":
            # Select all of the features in the 'covLogic_lyr' dataset which intersect the 'analysisBoundary'.
            arcpy.AddMessage("Selecting CovLogic Centroids which intersect the analysis boundary...")
            in_Origins = arcpy.Clip_analysis("covLogic_lyr", analysisBoundary,
                                             str(marketName) + "_DemandCentroids").getOutput(0)
            # # Establish a reference to the 'CovLogic_centroids' dataset as the Origins for the Origin-Destination Cost Matrix
            # in_Origins = workspace + "\\" + str(marketName) + "_DemandCentroids"
            # # arcpy.CopyFeatures_management(orig_Origins, str(marketName) + "_workDemandCentroids")
            # # work_Origins = workspace + "\\" + str(marketName) + "_workDemandCentroids"

            # Create a Feature Layer from the 'GO_bg_polygons' dataset to facilitate Spatial selections against the dataset.
            arcpy.AddMessage("Creating Block Group Polygons Feature Layer...")
            arcpy.AddMessage("Selecting Block Group Polygonal features residing in the analysis boundary...")
            orig_bg_polygons = arcpy.Clip_analysis(GO_BlockGroups, analysisBoundary,
                                                   str(marketName) + "_analysisBGPolygons").getOutput(0)
            # # Establish a reference to the 'bg_polygons_lyr' dataset
            # orig_bg_polygons = workspace + "\\" + str(marketName) + "_analysisBGPolygons"
            arcpy.MakeFeatureLayer_management(orig_bg_polygons, "bg_polygons_lyr")
            arcpy.AddMessage("Boundary data extraction process completed.")

        else:
            # Select all of the features in the 'covLogic_lyr' dataset which are within the distance in miles defined by the
            # 'CBSA Boundary Extension' (CBE) parameter of the given CBSA's boundary.
            arcpy.AddMessage(
                "Selecting Coverage Logic Centroids within " + CBE + " of analysis boundary...")
            arcpy.SelectLayerByLocation_management("covLogic_lyr", "WITHIN_A_DISTANCE", analysisBoundary, CBE,
                                                   "NEW_SELECTION")
            # Export the Selected features to the workspace.
            arcpy.AddMessage("Exporting Selected Coverage Logic Centroids...")
            in_Origins = arcpy.CopyFeatures_management("covLogic_lyr", str(marketName) + "_DemandCentroids").getOutput(
                0)

            # Create a Feature Layer from the 'GO_bg_polygons' dataset to facilitate Spatial selections against the dataset.
            arcpy.AddMessage("Creating Block Group Polygons Feature Layer...")
            arcpy.AddMessage(
                "Selecting Block Group Polygonal features residing in the analysis boundary plus boundary extension value...")
            arcpy.SelectLayerByLocation_management(GO_BlockGroups, "WITHIN_A_DISTANCE", analysisBoundary, CBE,
                                                   "NEW_SELECTION")

            orig_bg_polygons = arcpy.Clip_analysis(GO_BlockGroups, analysisBoundary,
                                                   str(marketName) + "_analysisBGPolygons").getOutput(0)
            # # Establish a reference to the 'bg_polygons_lyr' dataset
            # orig_bg_polygons = workspace + "\\" + str(marketName) + "_analysisBGPolygons"
            arcpy.MakeFeatureLayer_management(orig_bg_polygons, "bg_polygons_lyr")
            arcpy.AddMessage("Boundary data extraction process completed.")

        # Extract the total market demand from the analysis origins dataset
        total_market_demand = 0
        fields = origins_demand_field
        with arcpy.da.SearchCursor(in_Origins, fields) as cursor:
            for row in cursor:
                total_market_demand += row[0]

        arcpy.AddMessage("Total Market demand calculated at " + str(total_market_demand))

        # Establish a reference to the 'WGS_1984_Web_Mercator_Auxillary_Sphere' (WMAS) projection
        # The value '3857' is the WKID or unique identifier for the WMAS projection.
        WMAS = arcpy.SpatialReference(3857)

        """ [SP] Origin-Destination Cost Matrices Processes"""
        arcpy.AddMessage("Initializing Origin-Destination Cost Matrix process...")

        # Establish a reference to the 'CovLogic_centroids' dataset as the Origins for the
        # Origin-Destination Cost Matrix
        arcpy.AddMessage("Acquiring Origins...")
        if arcpy.Exists(in_Origins):
            pass
        else:
            arcpy.AddError("Unable to acquire Origins!")
        # Establish a reference to the dataset as the Destinations for the
        # Origin-Destination Cost Matrix
        arcpy.AddMessage("Acquiring Destinations...")
        if arcpy.Exists(in_Destinations):
            pass
        else:
            arcpy.AddError("Unable to acquire Destinations!")
        # Establish the arguments for the Origin-Destination Cost Matrix as variables to be passed into the
        # tool.
        arcpy.AddMessage("Acquiring Street Network Dataset...")
        if arcpy.Exists(in_NetworkDataset):
            pass
        else:
            arcpy.AddError("Unable to acquire network routing dataset!")
        arcpy.AddMessage("Establishing Network Analyst Layer...")
        outNALayerName = "BG2Sites"
        outLayerFile = outNALayerName + ".lyr"
        arcpy.AddMessage("Establishing Impedance Attribute as '" + impedanceAttribute + "'...")
        arcpy.AddMessage("Establishing Destination Search Distance Cut-Off as '" + DistCutoff + "'...")
        # Create the Composite Origin-Destination Cost Matrix Network Analysis Layer.
        arcpy.AddMessage("Creating Origin-Destination Cost Matrix...")
        outNALayer = arcpy.MakeODCostMatrixLayer_na(in_NetworkDataset, outNALayerName, impedanceAttribute,
                                                    DistCutoff, "", "", "", "", "USE_HIERARCHY", "",
                                                    "NO_LINES")
        # Acquire the result
        arcpy.AddMessage("Acquiring Composite Network Analysis Layer...")
        outNALayer = outNALayer.getOutput(0)
        # Acquire the SubLayers from the Composite Origin-Destination Cost Matrix Network Analysis Layer
        arcpy.AddMessage("Acquiring Composite Network Analysis SubLayers...")
        subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
        # Acquire the Origin's SubLayer
        arcpy.AddMessage("Acquiring Origins SubLayer...")
        originsLayerName = subLayerNames["Origins"]
        # Create a Field Map object to Map the 'CovLogic_Centroid' IDs to the Origins field of the Origin-Destination Cost Matrix
        originsFieldMap = arcpy.na.NAClassFieldMappings(outNALayer, originsLayerName)
        originsFieldMap["Name"].mappedFieldName = origins_id_field
        # Load the Origins into the Composite Network Analysis Layer.
        arcpy.AddMessage("Loading Origins into Composite Network Analysis Layer...")
        arcpy.na.AddLocations(outNALayer, originsLayerName, in_Origins, originsFieldMap)
        # Acquire the Destinations SubLayer
        arcpy.AddMessage("Acquiring Destinations SubLayer...")
        destinationsLayerName = subLayerNames["Destinations"]
        # Create a Field Map object to map the dataset ID to the Destinations field of the Origin-Destination Cost Matrix.
        destinationsFieldMap = arcpy.na.NAClassFieldMappings(outNALayer, destinationsLayerName)
        destinationsFieldMap["Name"].mappedFieldName = str(id_field)
        # Load the Destinations into the Composite Network Analysis Layer.
        arcpy.AddMessage("Loading Destinations into Composite Network Analysis Layer...")
        arcpy.na.AddLocations(outNALayer, destinationsLayerName, in_Destinations, destinationsFieldMap)
        # Solve the Network
        arcpy.AddMessage("Solving Network 'BG2Sites' Origin-Destination Cost Matrix...")
        arcpy.na.Solve(outNALayer)
        # Set the Workspace to C:\Temp
        arcpy.AddMessage("Resetting Workspace to C:\Temp...")
        arcpy.env.workspace = r"C:\Temp"
        # Extract the 'in_memory' result layer and save it as a Layer File in the workspace.
        arcpy.AddMessage("Extracting Result Layer from memory...")
        arcpy.SaveToLayerFile_management(outNALayer, outLayerFile, "RELATIVE")
        # Establish a reference to the Result Layer
        arcpy.AddMessage("Acquiring Result Layer...")
        ResultLayer = arcpy.mapping.Layer(r"C:\Temp\BG2Sites.lyr")
        # Reset the Workspace to the workspace
        arcpy.AddMessage("Resetting Workspace to " + str(workspace) + "...")
        arcpy.env.workspace = workspace
        # Establish a reference to a standard ESRI Map Template
        arcpy.AddMessage("Acquiring ESRI Template MXD...")
        # TempMXD = arcpy.mapping.MapDocument(r"C:\Program Files (x86)\ArcGIS\\" + str(
            # DesktopVersion) + "\\MapTemplates\Traditional Layouts\LetterPortrait.mxd")
        TempMXD = arcpy.mapping.MapDocument(r"C:\Temp\ODTA_TemplateMXD.mxd")
        # Establish a reference to the DataFrame within the ESRI Map Template
        arcpy.AddMessage("Acquiring ESRI Template MXD DataFrame...")
        TempDF = arcpy.mapping.ListDataFrames(TempMXD)[0]
        # Add the 'ResultLayer' to the DataFrame in the 'TempMXD'
        arcpy.AddMessage("Adding Result Layer to ESRI Template MXD...")
        arcpy.mapping.AddLayer(TempDF, ResultLayer)
        # Create a container and dynamically populate it with the layer in the Dataframe named 'Lines'
        LinesLYR = arcpy.mapping.ListLayers(TempMXD, "Lines", TempDF)
        if len(LinesLYR) > 1:
            arcpy.AddError(
                "Multiple OD Cost Matrices populated in Template MXD. Cannot identify correct OD Cost Matrix.")
        elif len(LinesLYR) < 1:
            arcpy.AddError("OD Cost Matrix was not populated in Template MXD. Unable to extract result.")
        else:
            for lyr in LinesLYR:
                # Export the table associated with the 'Lines' layer to a new table in the Workspace
                arcpy.AddMessage("Extracting " + input_name + " Sites Origin-Destination Cost Matrix...")
                arcpy.TableToTable_conversion(lyr, workspace, str(marketName) + "_" + input_name + "_ODCM")
                # Remove the layer from the TempMXD's DataFrame
                arcpy.AddMessage("Removing Result Layer from ESRI Template MXD...")
                arcpy.mapping.RemoveLayer(TempDF, lyr)
                # Delete the 'ResultLayer' file from disk
                arcpy.AddMessage("Deleting Result Layer from disk...")
                arcpy.Delete_management(r"C:\Temp\BG2Sites.lyr")
        # Establish a reference to the Sites Origin-Destination Cost Matrix
        arcpy.AddMessage("Acquiring Sites Origin-Destination Cost Matrix...")
        Sites_ODCM = workspace + "\\" + str(marketName) + "_" + input_name + "_ODCM"
        # Display a message to the user that the Origin-Destination Cost Matrix Complete
        arcpy.AddMessage("Origin-Destination Cost Matrix Process complete.")

        """ [SP] Manipulate Origin-Destination Cost Matrix"""
        # Delete any unnecessary fields ('DestinationID', 'OriginID', 'DestinationRank') from the Sites
        # Origin-Destination Cost Matrix
        arcpy.AddMessage(
            "Deleting fields 'DestinationID' | 'OriginID' | 'DestinationRank' from OD Cost Matrix...")
        arcpy.DeleteField_management(Sites_ODCM, ["DestinationID", "OriginID", "DestinationRank"])
        # Create a new field 'OriginID' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'OriginID'...")
        arcpy.AddField_management(Sites_ODCM, "OriginID", "TEXT", "", "", 15, "Origin ID",
                                  "NULLABLE", "REQUIRED")
        # Calculate the 'OriginID' field in the 'Sites_ODCM' table, populating the field with the Block Group IDs from the
        # 'Name' field in the Table
        arcpy.AddMessage("Calculating 'OriginID' field...")
        arcpy.CalculateField_management(Sites_ODCM, "OriginID", "!Name![:12]", "PYTHON")
        # Create a new field 'DestID' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'DestID'...")
        arcpy.AddField_management(Sites_ODCM, "DestID", "TEXT", "", "", 20, "Destination ID",
                                  "NULLABLE", "REQUIRED")
        # Calculate the 'DestID' field in the 'Sites_ODCM' table, populating the field with the 'Network' sites DID
        arcpy.AddMessage("Calculating 'DestID' field...")
        arcpy.CalculateField_management(Sites_ODCM, "DestID", "!Name![15:]", "PYTHON")
        # Create a new field 'Dij' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'Dij_ODTA'...")
        arcpy.AddField_management(Sites_ODCM, "Dij_ODTA", "DOUBLE", 15, 5, "", "Dij_ODTA", "NULLABLE",
                                  "REQUIRED")
        # Calculate the 'Dij' field in the 'Sites_ODCM' table
        arcpy.AddMessage("Calculating 'Dij_ODTA' field...")
        arcpy.CalculateField_management(Sites_ODCM, "Dij_ODTA", "!" + impedanceAttributeField + "!", "PYTHON")
        # Round the values held in the 'Dij' field in the 'Sites_ODCM' table to the nearest 5 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "Dij_ODTA", "round(!Dij_ODTA!, 5)", "PYTHON")
        # Delete the field 'Total_Miles' from the 'Sites_ODCM' table
        arcpy.AddMessage("Removing field '" + impedanceAttributeField + "'...")
        arcpy.DeleteField_management(Sites_ODCM, impedanceAttributeField)
        # Join the fields 'Beta' and 'Sj' from the 'in_Destinations' table to the 'Sites_ODCM' table
        arcpy.JoinField_management(Sites_ODCM, "DestID", in_Destinations, id_field,
                                   ["Beta_ODTA", sj_field, "Div50_ODTA"])
        # Round the values held in the 'Beta' field in the 'Sites_ODCM' table to the nearest 5 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "Beta_ODTA", "round(!Beta_ODTA!, 5)", "PYTHON")
        # Alter the 'Weight' field to change name to Huff Model referenced 'Sj" value
        arcpy.AlterField_management(Sites_ODCM, sj_field, "Sj_ODTA")
        # Round the values held in the 'Sj' field in the 'Sites_ODCM' table to the nearest 5 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "Sj_ODTA", "round(!Sj_ODTA!, 5)", "PYTHON")
        # Create a new field 'Dij_Beta' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'Dij_Beta_ODTA'...")
        arcpy.AddField_management(Sites_ODCM, "Dij_Beta_ODTA", "DOUBLE", 15, 5, "", "Dij^-B",
                                  "NULLABLE", "REQUIRED")
        # Calculate the 'Dij_Beta' field held in the 'Sites_ODCM' table with the result of the mathematical
        # operation 'Dij^-B'
        arcpy.AddMessage("Calculating 'Dij^-Beta'...")
        arcpy.CalculateField_management(Sites_ODCM, "Dij_Beta_ODTA", "math.pow(!Dij_ODTA!, -!Beta_ODTA!)",
                                        "PYTHON")
        # Round the values held in the 'Dij_B' field in the 'Sites_ODCM' table to the nearest 5 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "Dij_Beta_ODTA", "round(!Dij_Beta_ODTA!, 5)", "PYTHON")
        # Create a new field 'Share' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'Share'...")
        arcpy.AddField_management(Sites_ODCM, "Share_ODTA", "DOUBLE", 15, 5, "", "Share_ODTA", "NULLABLE",
                                  "REQUIRED")
        # Calculate the 'Share' field held in the 'Sites_ODCM' table with the result of the mathematical
        # operation '(Dij^-B)Sj'
        arcpy.AddMessage("Calculating Origin-Destination 'Share'...")
        arcpy.CalculateField_management(Sites_ODCM, "Share_ODTA", "!Dij_Beta_ODTA! * !Sj_ODTA!", "PYTHON")
        # Round the values held in the 'Dij_Beta_Sj' field in the 'Sites_ODCM' table to the nearest 5 significant
        # digits
        arcpy.CalculateField_management(Sites_ODCM, "Share_ODTA", "round(!Share_ODTA!, 5)", "PYTHON")

        """ [SP] Huff Model Denominator Processing Logic"""
        # Summarize the values held in the 'Share' field in the 'Sites_ODCM' table by unique 'OriginID',
        # creating a new table named 'Sites_ODCM_SumStats' in the workspace
        arcpy.AddMessage("Summarizing 'Share' by unique Block Group ID...")
        arcpy.Statistics_analysis(Sites_ODCM, "Sites_ODCM_SumStats", [["Share_ODTA", "SUM"]],
                                  "OriginID")
        # Establish a reference to the 'Sites_ODCM_SumStats' table
        arcpy.AddMessage("Acquiring Result Table...")
        Sites_ODCM_SumStats = workspace + "\\" + "Sites_ODCM" + "_SumStats"
        # Create a new field 'E_Share' in the 'Sites_ODCM_SumStats' table
        arcpy.AddMessage("Creating new field 'E_Share_ODTA'...")
        arcpy.AddField_management \
            (Sites_ODCM_SumStats, "E_Share_ODTA", "DOUBLE", 15, 5, "", "E(Share)_ODTA", "NULLABLE",
             "REQUIRED")
        # Copy the values held in the 'SUM_Share' field to the field 'E_Share' in the 'Sites_ODCM_SumStats' table.
        arcpy.AddMessage("Porting Result Values...")
        arcpy.CalculateField_management(Sites_ODCM_SumStats, "E_Share_ODTA", "!SUM_Share_ODTA!", "PYTHON")
        # Round the values held in the 'E_Share' field in the 'Sites_ODCM_SumStats' table to the nearest
        # 5 significant digits.
        arcpy.CalculateField_management(Sites_ODCM_SumStats, "E_Share_ODTA", "round(!E_Share_ODTA!, 5)",
                                        "PYTHON")
        # Join the field 'E_Share' held in the 'Sites_ODCM_SumStats' table to the 'Sites_ODCM' table
        arcpy.AddMessage("Joining Result to ODCM...")
        arcpy.JoinField_management(Sites_ODCM, "OriginID", Sites_ODCM_SumStats,
                                   "OriginID", "E_Share_ODTA")
        # Delete the 'Sites_ODCM_SumStats' table from Disk
        arcpy.AddMessage("Deleting temporary Summary Statistics table...")
        arcpy.Delete_management(Sites_ODCM_SumStats)
        del Sites_ODCM_SumStats
        # Create a new field 'demandShare_HM' in the 'Sites_ODCM' table
        arcpy.AddMessage("Creating new field 'Share / E(Share)'...")
        arcpy.AddField_management \
            (Sites_ODCM, "demandShare_HM_ODTA", "DOUBLE", 15, 5, "", "Demand Share (Huff Model)", "NULLABLE",
             "REQUIRED")
        # Calculate the 'demandShare_HM' field in the 'Sites_ODCM' table using the mathematical
        # operation '(Dij^-B)Sj / E(Dij^-B)Sj' with the numerator values being held in the field 'Share' and the denominator
        # values being held in the field 'E_Share'
        arcpy.AddMessage("Calculating Share / E_Share...")
        arcpy.CalculateField_management(Sites_ODCM, "demandShare_HM_ODTA", "!Share_ODTA! / !E_Share_ODTA!",
                                        "PYTHON")
        # Round the values held in the 'demandShare_HM' field in the 'Sites_ODCM' table to the
        # nearest 5 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "demandShare_HM_ODTA",
                                        "round(!demandShare_HM_ODTA!, 5)", "PYTHON")

        """[SP] Huff Model Demand Allocation Sequence """
        # Join the fields 'S4', 'S6', 'S7', 'S467', 'WKRS', 'SBB' and 'ING' from the 'covLogic' dataset to the
        # 'Sites_ODCM' table
        arcpy.AddMessage("Acquiring Coverage Logic Population...")
        arcpy.JoinField_management(Sites_ODCM, "OriginID", "covLogic_lyr", origins_id_field, [origins_demand_field])

        # Create a new field to contain Demand Allocation
        arcpy.AddField_management(Sites_ODCM, "demandAlloc_HM_ODTA", "FLOAT", 15, 5, "",
                                  "Demand Allocation (Huff Model)", "NULLABLE", "REQUIRED")
        # Calculate the Total Demand Allocation, multiplying the values held in the 'Share' field by those held in the 'total_bg_d' field
        arcpy.AddMessage("Calculating Total Huff Model Demand Allocation...")
        fields = ["demandShare_HM_ODTA", origins_demand_field, "demandAlloc_HM_ODTA"]
        with arcpy.da.UpdateCursor(Sites_ODCM, fields) as cursor:
            for row in cursor:
                demand_allocation_HM = row[0] * row[1]
                row[2] = demand_allocation_HM
                cursor.updateRow(row)

        # Round the values held in the 'demandAllocation' field in the 'Sites_ODCM' table to the
        # nearest 4 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "demandAlloc_HM_ODTA", "round(!demandAlloc_HM_ODTA!, 4)", "PYTHON")
        # Export the 'Sites_ODCM' table to a Table in the Geodatabase

        """ [SP] Distance Decay Denominator Processing Logic"""
        ############################ START - DISTANCE DECAY DENOMINATOR LOGIC ############################
        # Create the "(Sj*Dij^-b)/Div50" field
        arcpy.AddMessage("Creating 'Demand Share ((Sj*Dij^-b)/Div50)' field...")
        arcpy.AddField_management \
            (Sites_ODCM, "demandShare_preCapped_ODTA", "DOUBLE", 15, 5, "",
             "Demand Share((Sj*Dij^-b)/Div50) (Pre-Capped)", "NULLABLE",
             "REQUIRED")
        arcpy.AddMessage("Calculating '(Sj*Dij^-b)/Div50' field...")
        # Calculate the "(Sj*Dij^-b)/Div50" field
        arcpy.CalculateField_management(Sites_ODCM, "demandShare_preCapped_ODTA", "!Share_ODTA! / !Div50_ODTA!",
                                        "PYTHON")
        arcpy.AddMessage("Creating 'demandShare_Capped' field...")
        # Introduce logic that 'caps' the maximum demand allocation based on the provided Index
        # Create the "(Sj*Dij^-b)/Div50_Capped" field
        arcpy.AddField_management \
            (Sites_ODCM, "demandShare_DD_ODTA", "DOUBLE", 15, 5, "", "Demand Share (Distance Decay)", "NULLABLE",
             "REQUIRED")
        # Calculate "(Sj*Dij^-b)/Div50_Capped" field using an UpdateCursor operation
        arcpy.AddMessage("Calculating 'demandShare_DD_ODTA' field...")
        # Designate the fields needed for the UpdateCursor operation
        fields = ["Dij_ODTA", "demandShare_preCapped_ODTA", "demandShare_DD_ODTA"]
        with arcpy.da.UpdateCursor(Sites_ODCM, fields) as cursor:
            for row in cursor:
                # Determine if the 'Dij' value found by the UpdateCursor is less than the provided Index value
                if float(row[0]) < float(Index):
                    # If the 'Dij' value is less than the Index value, cap the demand share value at 1.
                    # arcpy.AddMessage("Dij is less than the provided Index value. Resetting demand share value to '1'...")
                    row[2] = 1
                    cursor.updateRow(row)
                elif row[1] > 1:
                    # If the 'demandShare_preCapped' value is greater than 1, cap the value at 1 to prevent the demand
                    # share allocated to the Origin-Destination pair from multiplying allocated demand by more than
                    # %100
                    row[2] = 1
                    cursor.updateRow(row)
                else:
                    # If the 'Dij' value is higher than the provided Index, use the inherent value that results from
                    # the '(Sj*Dij^-b)/Div50' calculation
                    # arcpy.AddMessage("Dij is higher than the provided Index. The field will provide the inherent Demand Share '(Sj*Dij^-b)/Div50' value...")
                    row[2] = row[1]
                    cursor.updateRow(row)
        # Round the values held in the 'demandShare_Capped' field in the 'Sites_ODCM' table to the
        # nearest 4 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "demandShare_DD_ODTA", "round(!demandShare_DD_ODTA!, 4)", "PYTHON")
        ############################ END - DISTANCE DECAY DENOMINATOR LOGIC ############################

        ##################### Calculate Demand Allocation via Distance Decay #####################
        # Create a new field to contain Demand Allocation
        arcpy.AddField_management(Sites_ODCM, "demandAlloc_DD_ODTA", "FLOAT", 15, 5, "",
                                  "Demand Allocation (Distance Decay)", "NULLABLE", "REQUIRED")

        arcpy.AddMessage("Calculating Total Distance Decay Demand Allocation...")
        # Calculate the Total Distance Decay Demand Allocation, multiplying the values held in the 'demandShare_DD'
        # field by those held in the 'total_bg_d' field
        fields = [origins_demand_field, "demandShare_DD_ODTA", "demandAlloc_DD_ODTA"]
        with arcpy.da.UpdateCursor(Sites_ODCM, fields) as demandCursor:
            for row in demandCursor:
                # Assign variables to each row list item
                total_bg_d = row[0]
                demandShare = row[1]
                demandAlloc = row[2]
                # Determine if the resulting demand deprecation would yield a negative value
                # (this prevents nonexistent demand from being allocated to the top-ranked item)
                if total_bg_d - (demandShare * total_bg_d) < 0:
                    # If result would be negative, set demand allocation to equal the remaining demand in the contributing origin
                    demandAlloc = total_bg_d
                else:
                    # If the result would be positive, set demand allocation to equal the multiplication
                    # of demandShare and available demand, 'total_bg_d'
                    demandAlloc = demandShare * total_bg_d
                # Set the 'demandAllocation_DD' field to equal the value in
                # the 'demandAlloc' variable
                row[2] = demandAlloc
                # Use the updateRow function of the UpdateCursor
                demandCursor.updateRow(row)

        # Round the values held in the 'demandAllocation_DD' field in the 'Sites_ODCM' table to the
        # nearest 4 significant digits
        arcpy.CalculateField_management(Sites_ODCM, "demandAlloc_DD_ODTA", "round(!demandAlloc_DD_ODTA!, 4)", "PYTHON")

        """ [SP] Comparative Demand Share Processing Logic"""
        # Create new field to contain the selected demand share value
        arcpy.AddField_management(Sites_ODCM, "demandShare_Selected_ODTA", "FLOAT", 15, 5, "",
                                  "Demand Share (Selected)", "NULLABLE", "REQUIRED")
        arcpy.AddMessage("Determining comparative demand share value...")
        # Invoke the 'return_lower_value' method to calculate the lower value between
        # Huff Model and Distance Decay demand share, then write the result into the field 'demandShare_Selected'
        self.return_lower_value(Sites_ODCM, "demandShare_HM_ODTA", "demandShare_DD_ODTA", "demandShare_Selected_ODTA")

        # Create new field to contain the selected demand allocation value
        arcpy.AddField_management(Sites_ODCM, "demandAlloc_Selected_ODTA", "FLOAT", 15, 5, "",
                                  "Demand Allocation (Selected)", "NULLABLE", "REQUIRED")
        arcpy.AddMessage("Determining comparative demand allocation value...")
        self.return_lower_value(Sites_ODCM, "demandAlloc_HM_ODTA", "demandAlloc_DD_ODTA", "demandAlloc_Selected_ODTA")

        pij_field = "demandShare_Selected_ODTA"
        pij_alloc_field = "demandAlloc_Selected_ODTA"

        """ Pij Prime Logic for Reverse ODTA """
        if pij_prime:
            # For each origin, we need to compute the total Pij (sum of all selected share values to all destinations)
            # then use that value as a new denominator to calibrate all origin's Pijs prior to allocating demand
            arcpy.AddMessage("\nPerforming Pij prime calculations...")

            # Set variable references to each field needed
            origin_total_pij_field = "origin_total_Pij"
            pij_prime_field = "demandShare_PijPrime_ODTA"
            pij_prime_alloc_field = "demandAlloc_PijPrime_ODTA"

            # Add needed fields
            arcpy.AddMessage("Adding total Pij field...")
            # Create a field to contain the origin's total Pij value
            arcpy.AddField_management(Sites_ODCM, origin_total_pij_field, "FLOAT", 15, 5, "",
                                      "Total Pij Values for Origin", "NULLABLE", "REQUIRED")
            # Create a field to contain the Pij prime value
            arcpy.AddMessage("Adding Pij prime field...")
            arcpy.AddField_management(Sites_ODCM, pij_prime_field, "FLOAT", 15, 5, "",
                                      "Demand Share (Pij Prime)", "NULLABLE", "REQUIRED")
            # Create a field to contain the Pij Prime allocation value
            arcpy.AddMessage("Adding Pij prime allocation field...")
            arcpy.AddField_management(Sites_ODCM, pij_prime_alloc_field, "FLOAT", 15, 5, "",
                                      "Demand Allocation (Pij Prime)", "NULLABLE", "REQUIRED")

            # Create a set of origins from the ODCM
            arcpy.AddMessage("Calculating origin total Pijs...")
            origins = set([row[0] for row in arcpy.da.SearchCursor(Sites_ODCM, ["OriginID"])])
            # Start iterating on each origin to calculate total Pijs
            for origin_id in origins:
                arcpy.AddMessage("Calculating total Pij for origin '{0}'...".format(str(origin_id)))
                # Set a where clause for the current origin
                where_pij_origins = arcpy.AddFieldDelimiters(Sites_ODCM, "OriginID") + " = '" + str(origin_id) + "'"
                # Start iterating on the table using the where_clause to compute total Pij
                total_origin_pij = 0
                with arcpy.da.SearchCursor(Sites_ODCM,
                                           ["OriginID", pij_field],
                                           where_clause=where_pij_origins) as cursor:
                    for row in cursor:
                        total_origin_pij += row[1]
                arcpy.AddMessage("Total Pij: {0}".format(str(total_origin_pij)))

                arcpy.AddMessage("Writing Total Pij value to origin...")

                with arcpy.da.UpdateCursor(Sites_ODCM,
                                           ["OriginID", origin_total_pij_field],
                                           where_clause=where_pij_origins) as cursor:
                    for row in cursor:
                        row[1] = total_origin_pij
                        cursor.updateRow(row)

                arcpy.AddMessage("Calculating Pij Primes for origin...")

                # Iterate once more on the origin_id using an update cursor to write the total_pijs into the table
                # and calculate Pij prime and Pij prime allocations
                with arcpy.da.UpdateCursor(Sites_ODCM,
                                           ["OriginID",
                                            pij_field,
                                            origin_total_pij_field,
                                            origins_demand_field,
                                            pij_prime_field,
                                            pij_prime_alloc_field],
                                           where_clause=where_pij_origins) as cursor:
                    for row in cursor:
                        pij_prime = float(row[1]) / float(row[2])
                        arcpy.AddMessage("Pij Selected: {0}".format(str(row[1])))
                        arcpy.AddMessage("Total Origin Pij: {0}".format(str(row[2])))
                        arcpy.AddMessage("Pij Prime: {0}".format(str(pij_prime)))
                        pij_prime_alloc = pij_prime * row[3]
                        arcpy.AddMessage("Demand: {0}".format(str(row[3])))
                        arcpy.AddMessage("Pij Prime Alloc: {0}".format(str(pij_prime_alloc)))
                        # Calculate Pij prime
                        row[4] = pij_prime
                        # Calculate the pij prime allocation using Pij prime
                        row[5] = pij_prime_alloc
                        cursor.updateRow(row)

            # Point field variables at pij prime-derived fields
            pij_field = pij_prime_field
            pij_alloc_field = pij_prime_alloc_field

        """ [SP] ODDM Table Export and MDT Logic """
        # Export the 'Sites_ODCM' table to a Table in the Geodatabase
        arcpy.AddMessage("Creating 'Origin-Destination Demand Matrix'...")
        # Assign 'Sites_ODDM' variable to the result of the Table export operation
        Sites_ODDM = arcpy.TableToTable_conversion(Sites_ODCM, workspace,
                                                   str(marketName) + "_" + input_name + "_ODDM").getOutput(0)

        # If the Minimum Demand Threshold parameter was set to a value greater than a value of '0' by the user:
        if MDT > 0:
            arcpy.AddMessage(
                "Creating Minimum Demand Threshold 'Origin-Destination Demand Matrix...")
            if arcpy.Exists("ODDM_MDT_TBV"):
                arcpy.Delete_management("ODDM_MDT_TBV")
            arcpy.MakeTableView_management(Sites_ODDM, "ODDM_MDT_TBV",
                                           '{0} >= '.format(pij_field) + str(MDT))
            Sites_ODDM = arcpy.TableToTable_conversion("ODDM_MDT_TBV", workspace,
                                                       str(marketName) + "_" + input_name + "_ODDM_MDT").getOutput(0)
            # Sites_ODDM = workspace + "\\" + str(marketName) + "_"+input_name+"_ODDM_MDT"
            if arcpy.Exists(Sites_ODDM):
                arcpy.AddMessage("ODDM table verified.")
            # Delete the 'Sites_ODCM' table from the workspace.
            try:
                arcpy.Delete_management(workspace + "\\" + str(marketName) + "_" + input_name + "_ODDM")
            except:
                arcpy.AddError("Failed to delete ODDM.")
        # Otherwise:
        else:
            # Notify the user aned continue with no action
            arcpy.AddMessage(
                "No Minimum Demand Threshold Established. ODTAs will be comprised of all Blockgroups within the Impedance Cutoff Value.")
            pass

        """ [SP] Create the Individual Network Predictive Trade Areas."""
        # Establish a variable for the demand_share field in each trade area, to be used in selection of values if
        # the artificial inclusion of DPT BGs is designated by the user
        demand_share_field = pij_field

        # Determine the results from the input parameter regarding cumulative percentage source
        if ta_percentage_basis == "Demand Share":
            cumulative_basis_field = demand_share_field
            ta_percentage_field = "DemandSharePercentage_ODTA"
            ta_percentage_field_alias = "Percentage based on Demand Share (Selected)"
            cumulative_ta_percentage_field = "CumulativeDemandSharePercentage_ODTA"
            cumulative_ta_percentage_field_alias = "'Cumulative percentage based on Demand Share (Selected)'"

        elif ta_percentage_basis == "Demand Allocation":
            cumulative_basis_field = pij_alloc_field
            ta_percentage_field = "DemandAllocPercentage_ODTA"
            ta_percentage_field_alias = "Percentage based on Demand Allocation (Selected)"
            cumulative_ta_percentage_field = "CumulativeDemandAllocPercentage_ODTA"
            cumulative_ta_percentage_field_alias = "Cumulative percentage based on Demand Allocation (Selected)"

        # Establish a variable for the pre-contribution stack-rank value used for ODTA symbology
        pre_contribution_stackrank_field = "PreContributionStackRank"
        pre_contribution_stackrank_field_alias = "Pre-Contribution Stack Rank"

        # Create a sorted ODDM in order to calculate stack-ranking from demand contribution
        arcpy.AddMessage("Creating copy of Sorted ODDM containing sorted cumulative percentage values...")
        Sorted_ODDM = arcpy.Sort_management(Sites_ODDM, str(marketName) + "_" + input_name + "_sortedODDM",
                                            [[cumulative_basis_field, "DESCENDING"]]).getOutput(0)
        # Add 'Demand Percentage' field to ODTAs_ODDM table
        arcpy.AddField_management(Sorted_ODDM, ta_percentage_field, "FLOAT", 15, 5, "", ta_percentage_field_alias,
                                  "NULLABLE", "REQUIRED")
        # Add 'Cumulative Demand Percentage' field to ODTAs_ODDM table
        arcpy.AddField_management(Sorted_ODDM, cumulative_ta_percentage_field, "FLOAT", 15, 5, "",
                                  cumulative_ta_percentage_field_alias, "NULLABLE", "REQUIRED")
        # Add 'Pre-Contribution Stack Rank' field to ODTAs_ODDM table
        arcpy.AddField_management(Sorted_ODDM, pre_contribution_stackrank_field, "FLOAT", 15, 5, "",
                                  pre_contribution_stackrank_field_alias, "NULLABLE", "REQUIRED")

        # Create a TableView of the 'Sorted_ODDM' table
        arcpy.AddMessage("Creating Table View of Network Sites...")
        # Determine if a residual BG polys table view exists in memory; delete if so
        if arcpy.Exists("TBV"):
            arcpy.AddMessage("Found Residual Table View element in memory. Deleting...")
            arcpy.Delete_management("TBV")
        Sorted_ODDM_TBV = arcpy.MakeTableView_management(Sorted_ODDM, "TBV").getOutput(0)
        arcpy.AddMessage(arcpy.Describe(Sorted_ODDM_TBV).dataType)

        # arcpy.AddMessage("Creating Feature Dataset " + str(marketName) + "_ODTA...")
        # # Create a Feature Dataset with the name of the given market name and the WMAS Spatial Reference System.
        # arcpy.CreateFeatureDataset_management(workspace, str(marketName) + "_ODTA", WMAS)
        #
        # # Set the Workspace to the given ODTAs Feature Dataset so that Trade Areas are saved there
        # arcpy.env.workspace = workspace + "\\" + str(marketName) + "_ODTA"

        # Create a Unique Set of Sites by DestID from the Table View
        arcpy.AddMessage("Creating SiteSet...")
        SiteSet = set([r[0] for r in arcpy.da.SearchCursor(Sorted_ODDM_TBV, ["DestID"])])
        # Iterate though each Site in the SiteSet and perform the following actions:
        for Site in SiteSet:
            TradeArea = arcpy.env.workspace + "\\" + "TradeArea_ID_" + str(Site)
            arcpy.AddMessage("\nChecking to see if Trade Area for ID " + str(Site) + " exists...")
            # Determine if a Trade Area for the current ID in iteration already exists
            if arcpy.Exists(TradeArea):
                # If Trade Area already exists, inform the user and pass
                arcpy.AddMessage("Trade Area for ID " + str(Site) + " already exists. Passing...")
            else:
                # If the Trade Area does not exist
                arcpy.AddMessage("Trade Area for ID " + str(Site) + " not found. Creating...")

                arcpy.AddMessage("Selecting Block Groups associated with ID " + str(Site) + "...")
                where_clause = arcpy.AddFieldDelimiters(Sorted_ODDM_TBV, "DestID") + " = '" + str(Site) + "'"
                site_matrix = arcpy.TableSelect_analysis(Sorted_ODDM_TBV,
                                                         workspace + "\\" + "SiteMatrix_" + str(Site),
                                                         where_clause).getOutput(0)

                # Set a variable, 'cumulative_demand', that will be
                # incremented by each demand allocation value in the
                # site's contributing bg trade area
                cumulative_demand = 0

                # Determine the total cumulative demand allocation
                # and write value to the variable, 'cumulative_demand'
                with arcpy.da.SearchCursor(site_matrix, [cumulative_basis_field]) as cursor:
                    for row in cursor:
                        cumulative_demand += row[0]

                # Check if the cumulative trade area demand results in 0
                if cumulative_demand == 0:
                    arcpy.AddWarning("WARNING: The Cumulative Demand for site " + str(
                        Site) + "'s Trade Area totaled zero. This trade area cannot be produced.\n")
                    # Return control to the beginning of the loop to prevent execution performing a float
                    # point division by zero
                    continue

                arcpy.AddMessage("\tDEVNOTE: cumulative_demand = " + str(cumulative_demand))

                # Determine what the percentage parameter of the total is and write value to a variable, 'pcnt_demand_value'
                pcnt_demand_value = cumulative_demand * demand_percentage
                arcpy.AddMessage("\tDEVNOTE: pcnt_demand_value = " + str(pcnt_demand_value))

                # Set a variable, 'cumulative_demand', that will be
                # incremented by each demand allocation value in the
                # site's contributing bg trade area
                cumulative_demand_pcnt = 0
                # Set an empty variable, 'bg_IDs', to contain an
                # eventual list of the pcnt block group IDs
                bg_IDs_list = []

                """ [SP] Artificial Business Constraint - Add Home BG to Trade Area """
                # Check if the home_bg flag is active
                if home_bg_flag == True:
                    point_fc = dataset
                    point_id_field = id_field
                    point_id = Site
                    subgeography_fc = GO_BlockGroups
                    subgeography_id_field = bg_id_field_name
                    self.add_home_bg_to_ODTA(point_fc, point_id_field, point_id, subgeography_fc,
                                            subgeography_id_field, bg_IDs_list)
                else:
                    pass

                """ [SP] Artificial Business Constraint - Add DPT BG to Trade Area """
                if dpt_bg_flag == True:
                    self.add_dpt_bg_to_ODTA(site_matrix, "OriginID", demand_share_field, dpt_bg_value, bg_IDs_list)
                else:
                    pass

                # Set the fields parameter for the upcoming cursor
                fields = ["OriginID",
                          cumulative_basis_field,
                          ta_percentage_field,
                          cumulative_ta_percentage_field,
                          pre_contribution_stackrank_field]
                # Set variable for stack_rank_contribution_count to use for the pre-contribution calculation
                stackrank_contribution_count = 0

                arcpy.AddMessage("\tDEVNOTE: TBV fields = ")
                arcpy.AddMessage(fields)
                # Determine the demand percentage and cumulative demand percentage values for each contributing BG_ID
                with arcpy.da.UpdateCursor(site_matrix, fields) as cursor:
                    for row in cursor:
                        # Determine the demand percentage
                        row[2] = row[1] / cumulative_demand
                        # Determine the cumulative demand percentage value
                        cumulative_demand_pcnt += row[2]
                        row[3] = cumulative_demand_pcnt
                        row[4] = stackrank_contribution_count
                        stackrank_contribution_count += row[2]

                        """ [SP] Build the ODTA bg_IDs_list """
                        # Determine if the user-designated demand_percentage is under 100 in order to filter
                        # elimination of BGs
                        if demand_percentage < 1:
                            # If the origin demand percent contribution is under the directed threshold...
                            if row[3] <= demand_percentage:
                                bg_IDs_list.append(str(row[0]))
                            else:
                                pass
                        else:
                            bg_IDs_list.append(str(row[0]))

                        # Update the record with the calculated values
                        cursor.updateRow(row)

                arcpy.AddMessage("DEVNOTE: bg_ids_list = " + str(bg_IDs_list))

                if len(bg_IDs_list) == 0:
                    # Determine if the amount of BG IDs that contributed to the trade area resulted in 0
                    with arcpy.da.UpdateCursor(site_matrix, fields) as cursor:
                        check_flag = True
                        while check_flag:
                            for row in cursor:
                                # Determine the ta_percentage_field value in order to see if the TA is composed of one
                                # strong BG contributor to the ODTA
                                if row[2] > demand_percentage:
                                    bg_IDs_list.append(str(row[0]))
                                    check_flag = False

                # If the user designated the "draw ODTAs" parameter as true, extract polygons to make FC ODTAs
                if draw_TAs:
                    # Determine if a residual table view exists in memory; delete if so
                    if arcpy.Exists("BG_layer"):
                        arcpy.AddMessage("Found Residual BG Layer in memory. Deleting...")
                        arcpy.Delete_management("BG_layer")
                    # Create a Feature Layer of the origin Block Groups
                    arcpy.AddMessage("Creating Block Groups Layer...")
                    arcpy.MakeFeatureLayer_management(GO_BlockGroups, "BG_layer")

                    arcpy.AddMessage("Gathering ODTA Block Group IDs...")
                    bg_IDs = tuple(bg_IDs_list)
                    arcpy.AddMessage(bg_IDs)
                    arcpy.AddMessage("Building SQL Query")
                    if len(bg_IDs) == 0:
                        arcpy.AddWarning("Site DID " + str(
                            Site) + " did not return any Block Groups for inclusion in Trade Area. A ODTA will not be created for this site.")
                        continue
                    elif len(bg_IDs) == 1:
                        arcpy.AddMessage("DEVNOTE: len(bg_IDs) equaled 1")
                        for i in bg_IDs:
                            bg_IDs = "('" + i + "')"
                        first = arcpy.AddFieldDelimiters('BG_layer', bg_id_field_name)
                        second = str(bg_IDs)
                        where = """{0} IN {1}""".format(first, second)
                    ##                                arcpy.AddMessage("DEVNOTE: bg_IDs = "+str(bg_IDs))
                    ##                                arcpy.AddMessage("DEVNOTE: where = "+str(where))
                    elif len(bg_IDs) > 1:
                        ##                                arcpy.AddMessage("DEVNOTE: len(bg_IDs) was greater than 1")
                        first = arcpy.AddFieldDelimiters('BG_layer', bg_id_field_name)
                        second = str(bg_IDs)
                        where = """{0} IN {1}""".format(first, second)
                    arcpy.AddMessage("Creating Trade Area for ID " + str(Site) + "...")
                    TradeArea = arcpy.Select_analysis("BG_layer", "TradeArea_ID_" + str(Site), where).getOutput(0)
                    arcpy.AddMessage("Acquiring DID " + str(Site) + "'s Demand Allocations...")
                    site_matrix_tableview = arcpy.MakeTableView_management(site_matrix, "SiteMatrix_" + str(
                        Site) + "_TBV").getOutput(0)
                    arcpy.AddMessage("Joining Demand Allocations for DID " + str(Site) + " to Site's Trade Area...")

                    if pij_prime:
                        ta_joinfield_list = ["DestID",
                                             "NAME",
                                             "Dij_ODTA",
                                             "Beta_ODTA",
                                             "Sj_ODTA",
                                             "Dij_Beta_ODTA",
                                             origins_demand_field,
                                             "Share_ODTA",
                                             "E_Share_ODTA",
                                             "demandShare_HM_ODTA",
                                             "demandAlloc_HM_ODTA",
                                             "Div50_ODTA",
                                             "demandShare_DD_ODTA",
                                             "demandAlloc_DD_ODTA",
                                             pij_field,
                                             pij_alloc_field,
                                             ta_percentage_field,
                                             cumulative_ta_percentage_field,
                                             pre_contribution_stackrank_field]
                    else:
                        ta_joinfield_list = ["DestID",
                                             "NAME",
                                             "Dij_ODTA",
                                             "Beta_ODTA",
                                             "Sj_ODTA",
                                             "Dij_Beta_ODTA",
                                             origins_demand_field,
                                             "Share_ODTA",
                                             "E_Share_ODTA",
                                             "demandShare_HM_ODTA",
                                             "demandAlloc_HM_ODTA",
                                             "Div50_ODTA",
                                             "demandShare_DD_ODTA",
                                             "demandAlloc_DD_ODTA",
                                             "demandShare_Selected_ODTA",
                                             "demandAlloc_Selected_ODTA",
                                             pij_field,
                                             pij_alloc_field,
                                             ta_percentage_field,
                                             cumulative_ta_percentage_field,
                                             pre_contribution_stackrank_field]

                    arcpy.JoinField_management(TradeArea, bg_id_field_name, site_matrix_tableview, "OriginID",
                                               ta_joinfield_list)

                    arcpy.AddMessage("Completed Trade Area for Site DID " + str(Site) + "...")

                ''' [SP] Write the demand allocation value to the output points feature class '''
                # Determine the Trade Area's total demand allocation value
                arcpy.AddMessage("Determining the total allocated demand for site " + str(Site) + "...")
                # Create empty container to hold the cumulative demand allocation value for the trade area
                total_allocated_demand = 0.00
                fields = ['DestID', 'demandAlloc_Selected_ODTA']
                with arcpy.da.SearchCursor(site_matrix, fields) as cursor:
                    for row in cursor:
                        if row[1]:
                            total_allocated_demand += float(row[1])
                        else:
                            pass

                arcpy.AddMessage("Site " + str(Site) + " allocated demand: " + str(total_allocated_demand))
                #Write the result back to the output Destinations feature class
                where_clause = arcpy.AddFieldDelimiters(in_Destinations, id_field) + " = '" + str(Site) + "'"
                fields = [id_field, "demandAlloc_Selected_ODTA", "demandAlloc_MktPcnt_ODTA"]
                with arcpy.da.UpdateCursor(in_Destinations, fields, where_clause) as cursor:
                    for row in cursor:
                        row[1] = float(total_allocated_demand)
                        row[2] = round(((total_allocated_demand / total_market_demand) * 100), 2)
                        arcpy.AddMessage("Site " + str(row[0]) + " demand results:")
                        arcpy.AddMessage("    Total Allocated Demand for Site " + str(Site) + ": " + str(row[1]))
                        arcpy.AddMessage("    Market Demand Available: " + str(total_market_demand))
                        arcpy.AddMessage(
                            "    Market Demand Allocation Percentage for Site " + str(Site) + ": " + str(row[2]))
                        cursor.updateRow(row)

        ''' [SP] Composite Trade Area Dataset Creation Procedures '''
        # Create the Composite Trade Area Dataset
        arcpy.AddMessage("Compiling analysis Trade Areas...")
        if draw_TAs:
            TAList = arcpy.ListFeatureClasses("TradeArea_ID_*", "Polygon")
            arcpy.AddMessage("Creating Composite Trade Area Dataset...")
            CompositeTradeArea = arcpy.CreateFeatureclass_management(str(arcpy.env.workspace),
                                                                     "CompositeODTA_" + input_name + "_" + str(
                                                                         marketName), "Polygon",
                                                                     TAList[0], "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE",
                                                                     TAList[0]).getOutput(0)
        else:
            TAList = arcpy.ListTables("SiteMatrix_*")
            CompositeTradeArea = arcpy.CreateTable_management(str(arcpy.env.workspace),
                                                              "CompositeODTA_" + input_name + "_" + str(marketName),
                                                              TAList[0]).getOutput(0)

        arcpy.AddMessage("Appending individual Trade Areas to Composite Trade Area...")
        arcpy.Append_management(TAList, CompositeTradeArea, "TEST")
        arcpy.AddMessage("Composite Trade Area created.")

        arcpy.AddMessage("ODTA tool execution completed.")

    def execute(self, parameters, messages):
        """ [SP] Determine the combination of user inputs and execute accordingly. """

        ###########################################################################################################
        #                                AOIs ONLY EXECUTION SEQUENCE                                             #
        ###########################################################################################################

        # If the user has left param1 (ProForma Sites) input empty and provided an input for param4 (AOIs):
        if parameters[1].value:
            """ [SP] Execute the ODTA Model against AOIs only."""

            """ [SP] Set up the Workspace"""
            # Instantiate the inputs submitted by the user as variables.
            AOIs = parameters[1].valueAsText
            AOIsIDField = parameters[2].valueAsText
            AOIsSjField = parameters[3].valueAsText

            self.create_ODTAs(parameters, AOIs, AOIsIDField, AOIsSjField, "AOI")
