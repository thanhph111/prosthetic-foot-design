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
        "abaqus cae noGUI=sub/kernel.py -- %s" % (points),
        shell=True,
        universal_newlines=True,
    )
    return ast.literal_eval(output)


items = [
    [
        114.63107020229356,
        155.10267783233923,
        157.09506749123182,
        153.7058893565211,
        162.1430041090124,
        131.76490124852504,
        121.89182385099676,
        99.52622992289716,
        139.81117638950445,
        46.46699875209077,
        324.31990604815996,
        25.141656256834708,
        320.0225980667446,
        14.22609723323744,
        57.99170825014508,
        10.959535340663123,
        57.50608699549253,
        25.90945520202186,
        102.7918196300105,
        27.382873990461697,
        80.30868221882133,
        61.94692710686138,
        107.81422996813805,
        138.27944771382076,
    ]
]

for item in items:
    print(call(item))
