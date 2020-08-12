import subprocess
import ast


def chunker(seq, size):
    """Split a list into equal segments (maybe except the last one)."""
    return list(seq[pos : pos + size] for pos in range(0, len(seq), size))


def genes_to_points(genes):
    return chunker(genes, 2)


def call(genes):
    """Put in a list of coordinates that will be converted to list of points
    and be sent to kernel.py. Finally return a dict of results."""

    points = genes_to_points(genes)
    output = subprocess.check_output(
        "abaqus cae script=kernel.py -- %s" % (points),
        shell=True,
        universal_newlines=True,
    )
    return ast.literal_eval(output)


item = [
    111.87132947467546,
    154.84234007460947,
    151.22783189690762,
    151.94710336686853,
    153.63132721020142,
    132.90801960616707,
    105.90063325502885,
    83.65029884013845,
    123.7738980535961,
    43.95716766771994,
    318.7427215955475,
    26.616519367623177,
    331.5687735490922,
    11.728892217460007,
    64.24634419016516,
    10.896031033564434,
    65.69086030517032,
    26.982343069431955,
    110.00149598853362,
    28.820551914191583,
    77.41055801595185,
    61.023071799296346,
    121.25260316369966,
    132.13412555335466,
]
call(item)
