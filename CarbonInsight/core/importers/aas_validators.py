import logging
from io import BytesIO, TextIOWrapper

from aas_test_engines.file import *
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)
def validate_aas_aasx(file:BytesIO, silent:bool=False) -> bool:
    result = check_aasx_file(BytesIO(file.getvalue()))  # I KNOW THIS IS A TYPING ISSUE, BUT USING TEXTIO CRASHES THE CHECKER
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS AASX file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()

def validate_aas_json(file:BytesIO, silent:bool=False) -> bool:
    text_io = TextIOWrapper(BytesIO(file.getvalue()))
    result = check_json_file(text_io)
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS JSON file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()

def validate_aas_xml(file:BytesIO, silent:bool=False) -> bool:
    text_io = TextIOWrapper(BytesIO(file.getvalue()))
    result = check_xml_file(text_io)
    if not silent and not result.ok():
        raise ValidationError({"file":f"AAS XML file is not valid: \n"+'\n'.join(get_error_critical_messages(result))})
    return result.ok()