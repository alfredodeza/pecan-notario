__version__ = "0.1"

__version__ = '0.0.1'

#from notario import validate
from notario.exceptions import Invalid

from pecan_notario.decorator import validate

__all__ = ['validate', 'Invalid']
