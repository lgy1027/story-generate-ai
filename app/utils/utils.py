from uuid import uuid4
import os

def get_uuid(remove_hyphen: bool = False) -> str:
    u = str(uuid4())
    if remove_hyphen:
        return u.replace("-", "")
    else:
        return u
    
def get_root_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def resource_dir(sub_dir: str = ""):
    d = os.path.join(get_root_dir(), "resource")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    return d