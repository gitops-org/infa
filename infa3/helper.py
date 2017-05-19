"""
This module contains generic functions for handling communication with
Informatica programs and process their output.
"""


def cmd_prepare(params, opts_args, opts_flags):
    """
    Prepare the command line parameters to be passed to an external
    program.

    The passed parameters may either require additional arguments, or serve
    as plain flags and should be handled appropriately.

    Args:
        params (str): parameters supplied
        opts_args (list[str]): list of command line options that require 
            additional arguments
        opts_flags (list[str]): list of command line options without 
            additional arguments (regular flags)

    Returns:
        List
    """
    command = []
    for key, value in params.items():
        if key in opts_args:
            command.extend(['-' + key, value])
        elif key in opts_flags and value == True:
            command.extend(['-' + key])
        elif key not in opts_args + opts_flags:
            raise Exception("unsupported option: %s" % key)
    return command


def cmd_execute(command):
    """
    Execute an external command and return its output as a list where 
    each list element corresponds to one STDOUT line returned by the 
    command.

    Args:
        command (list): OS command call formatted for the subprocess'
            Popen

    Returns:
        List
    """
    import subprocess  # import only on demand, as it is slow on cygwin
    command_output = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    return str(command_output[0]).strip("b'").split('\\r\\n')


def cmd_status(command, command_output):
    """
    Check if the command has been successfully executed.

    A command is considered be executed successfully if the output 
    stream contains a string 'completed successfully'.

    Args:
        command (list): executed command
        command_output(list): output of that command

    Returns:
        None
    """
    if not any('completed successfully' in line for line in command_output):
        print("\n".join(command_output))
        raise Exception("failed to execute: %s" % " ".join(command))


def format_output(command_output, field_separator):
    """
    Cleanse the external commands STDOUT stream and format it 
    to an API-friendly list.

    Args:
        command_output(list): array of lines returned by the called
            program
        field_separator(str): caracted that delimits a field in the 
            returned output

    Returns:
        List
    """
    ignore_lines = (
        'Informatica',
        'Copyright',
        'All Rights Reserved',
        'This Software is protected',
        'Invoked at',
        'Completed at',
        'completed successfully'
    )

    result = []
    for item in command_output:
        if item and not any(s in item for s in ignore_lines):
            if field_separator in item:
                result.append(item.strip().split(field_separator))
            else:
                result.append(item.strip())

    return result


def create_import_control_xml(xml_output, src_folder, src_repo, tgt_folder, tgt_repo, dtd):
    """
    Creates a control xml file for the objectimport command.
    For now the strategy is simply to replace all objects.
    Raises an exception if the file cannot be created.

    Args:
        src_folder(str): name of the source folder
        src_repo(str): name of the source repository
        tgt_folder(str): name of the target folder
        tgt_repo(str): name of the target repository

    Returns:
        Nothing
    """
    template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE IMPORTPARAMS SYSTEM "{dtd}">
<IMPORTPARAMS CHECKIN_AFTER_IMPORT="NO">
<FOLDERMAP SOURCEFOLDERNAME="{src_folder}" SOURCEREPOSITORYNAME="{src_repo}" TARGETFOLDERNAME="{tgt_folder}" TARGETREPOSITORYNAME="{tgt_repo}"/>
<RESOLVECONFLICT>
<TYPEOBJECT OBJECTTYPENAME = "ALL" RESOLUTION="REPLACE"/>
</RESOLVECONFLICT>
</IMPORTPARAMS>""".format(src_folder=src_folder, src_repo=src_repo, tgt_folder=tgt_folder, tgt_repo=tgt_repo, dtd=dtd)
    with open(xml_output, 'w') as f:
        f.write(template)
