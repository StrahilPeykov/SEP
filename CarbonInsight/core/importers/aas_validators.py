import logging
from io import BytesIO, TextIOWrapper

from aas_test_engines.file import *
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

def get_error_critical_messages(result: AasTestResult) -> list[str]:
    """
    Recursively extracts all ERROR and CRITICAL messages from an AasTestResult.

    Args:
        result: The top-level result from the AAS test engine.

    Returns:
        A flat list of all error and critical messages.
    """
    errors = []
    if result.level == Level.CRITICAL:
        errors.append(result.message)
    elif result.level == Level.ERROR:
        errors.append(result.message)
    for sub_result in result.sub_results:
        errors.extend(get_error_critical_messages(sub_result))
    return errors

def validate_aas_aasx(file:BytesIO, silent:bool=False) -> bool:
    """
    Validates an AASX file.

    Args:
        file: The AASX file content as a byte stream.
        silent: If True, suppresses ValidationError and returns a boolean.

    Returns:
        True if the file is valid, False otherwise.

    Raises:
        ValidationError: If the file is invalid and silent is False.
    """

    result = check_aasx_file(BytesIO(file.getvalue()))  # I KNOW THIS IS A TYPING ISSUE, BUT USING TEXTIO CRASHES THE CHECKER
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS AASX file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()

def validate_aas_json(file:BytesIO, silent:bool=False) -> bool:
    """
    Validates an AAS JSON file.

    Args:
        file: The AAS JSON file content as a byte stream.
        silent: If True, suppresses ValidationError and returns a boolean.

    Returns:
        True if the file is valid, False otherwise.

    Raises:
        ValidationError: If the file is invalid and silent is False.
    """

    text_io = TextIOWrapper(BytesIO(file.getvalue()))
    result = check_json_file(text_io)
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS JSON file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()

def validate_aas_xml(file:BytesIO, silent:bool=False) -> bool:
    """
    Validates an AAS XML file.

    Args:
        file: The AAS XML file content as a byte stream.
        silent: If True, suppresses ValidationError and returns a boolean.

    Returns:
        True if the file is valid, False otherwise.

    Raises:
        ValidationError: If the file is invalid and silent is False.
    """

    text_io = TextIOWrapper(BytesIO(file.getvalue()))
    result = check_xml_file(text_io)
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS XML file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()