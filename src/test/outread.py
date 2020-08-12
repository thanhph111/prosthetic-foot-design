from abaqus import *
from abaqusConstants import *
import odbAccess


OUTPUT_DATABASE = "Model-0-069.odb"


def _print_(string):
    """Print a string to command prompt if running scrip within abaqus cae.
    Return nothing
    """
    print >>sys.__stdout__, string  # noqa: F633


my_odb = odbAccess.openOdb(path=OUTPUT_DATABASE)
my_last_frame = my_odb.steps["LoadStep"].frames[-1]
total_energy_density = my_last_frame.fieldOutputs["ESEDEN"]
elements_data = []
for index in total_energy_density.values:
    elements_data.append(index.data)
_print_(max(elements_data))
