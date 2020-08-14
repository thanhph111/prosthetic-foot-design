"""This is kernel file that uses abaqus kernel for modeling and analyse jobs.
You should not modify this.
"""

# Import new print function from python 3
from __future__ import print_function

# Abaqus related modules
import abaqus as ABQ
import abaqusConstants as ABC

import part  # noqa: F401
import sketch  # noqa: F401
import material  # noqa: F401
import section  # noqa: F401
import assembly  # noqa: F401
import step  # noqa: F401
import load  # noqa: F401
import job  # noqa: F401
import mesh  # noqa: F401
import odbAccess

# Standard modules
import visualization
import os
import sys
import ast
import random

# Other modules
from sub.inputprocess import RULES as RULES
from sub.inputprocess import CONSTANTS as CONS

# Convert list of unicode string to tuple of bare string
OUTPUT_VARIABLE_TUPLE = tuple(
    index.encode("ascii", "ignore") for index in CONS["OUTPUT_VARIABLE"]
)


def _print_(string):
    """Print a string to command prompt if running scrip within abaqus cae.
    Return nothing
    """
    print(string, file=sys.__stdout__)


def remove_unnecessary_files(file_name):
    """Delete unused files. Return nothing"""
    for type in CONS["UNUSED_FILES"]:
        if os.path.isfile(file_name + type):
            try:
                os.remove(file_name + type)
            except Exception:
                pass


def finite_element_analysis(
    points, is_planar=CONS["PLANAR_MODE"], print_photo=CONS["PHOTO_MODE"]
):
    model_name = "Model" + "_" + str(random.random())[2:]

    # Create a models
    my_model = ABQ.mdb.Model(name=model_name)

    # Create a part
    my_sketch = my_model.ConstrainedSketch(name="Profile", sheetSize=300.0)
    # Create lines by 2 points
    for index in RULES["Lines"]:
        my_sketch.Line(
            point1=points[index[0] - 1], point2=points[index[1] - 1]
        )
    # Create arcs by 3 points
    for index in RULES["Arcs"]:
        my_sketch.Arc3Points(
            point1=points[index[0] - 1],
            point2=points[index[2] - 1],
            point3=points[index[1] - 1],
        )
    # Create part
    if is_planar:
        my_part = my_model.Part(
            name="FootPart",
            dimensionality=ABC.TWO_D_PLANAR,
            type=ABC.DEFORMABLE_BODY,
        )
        my_part.BaseShell(sketch=my_sketch)
    else:
        my_part = my_model.Part(
            name="FootPart",
            dimensionality=ABC.THREE_D,
            type=ABC.DEFORMABLE_BODY,
        )
        my_part.BaseSolidExtrude(sketch=my_sketch, depth=CONS["DEPTH"])

    # Create a material
    my_material = my_model.Material(name="POM")
    my_material.Elastic(
        table=((CONS["YOUNGS_MODULUS"], CONS["POISSONS_RATIO"]),)
    )

    # Create section
    if is_planar:
        my_model.HomogeneousSolidSection(
            name="FootSection", material="POM", thickness=None
        )
        my_part.SectionAssignment(
            region=(my_part.faces,), sectionName="FootSection"
        )
    else:
        my_model.HomogeneousSolidSection(
            name="FootSection", material="POM", thickness=1.0
        )
        my_part.SectionAssignment(
            region=(my_part.cells,), sectionName="FootSection"
        )

    # Create an instance
    my_assembly = my_model.rootAssembly
    my_instance = my_assembly.Instance(
        name="FootInstance", part=my_part, dependent=ABC.OFF
    )

    # Create a step
    my_model.StaticStep(
        name="LoadStep",
        previous="Initial",
        timePeriod=1.0,
        initialInc=0.1,
        description="Weight of patient",
    )

    # Create track point
    vertices = my_instance.vertices
    track_point = vertices.findAt((tuple(points[1] + [0]),))
    my_assembly.Set(vertices=track_point, name="TrackPoint")

    # Create field output request and set one frame only
    my_field_request = my_model.fieldOutputRequests["F-Output-1"]
    my_field_request.setValues(variables=OUTPUT_VARIABLE_TUPLE)

    my_history_request = my_model.historyOutputRequests["H-Output-1"]
    my_history_request.setValues(
        variables=("U1", "U2", "U3", "UR1", "UR2", "UR3"),
        region=my_assembly.sets["TrackPoint"],
    )

    if is_planar:
        # Fix face and apply load
        fixed_edge_center = (
            (points[6][0] + points[7][0]) / 2,
            (points[6][1] + points[7][1]) / 2,
            0,
        )
        loaded_edge_center = (
            (points[0][0] + points[1][0]) / 2,
            (points[0][1] + points[1][1]) / 2,
            0,
        )
        # Fix face
        fixed_edge = my_instance.edges.findAt((fixed_edge_center,))
        my_model.EncastreBC(
            name="Fixed", createStepName="LoadStep", region=(fixed_edge,)
        )
        # Apply load
        loaded_edge = my_instance.edges.findAt((loaded_edge_center,))
        my_model.Pressure(
            name="Loaded",
            createStepName="LoadStep",
            region=((loaded_edge, ABC.SIDE1),),
            magnitude=CONS["LOAD_MAGNITUDE"],
        )
    else:
        # Fix face and apply load
        fixed_face_center = (
            (points[6][0] + points[7][0]) / 2,
            (points[6][1] + points[7][1]) / 2,
            CONS["DEPTH"] / 2,
        )
        loaded_face_center = (
            (points[0][0] + points[1][0]) / 2,
            (points[0][1] + points[1][1]) / 2,
            CONS["DEPTH"] / 2,
        )
        # Fix face
        fixed_face = my_instance.faces.findAt((fixed_face_center,))
        my_model.EncastreBC(
            name="Fixed", createStepName="LoadStep", region=(fixed_face,)
        )
        # Apply load
        loaded_face = my_instance.faces.findAt((loaded_face_center,))
        my_model.Pressure(
            name="Loaded",
            createStepName="LoadStep",
            region=((loaded_face, ABC.SIDE1),),
            magnitude=CONS["LOAD_MAGNITUDE"],
        )

    # Mesh the instance
    my_assembly.seedPartInstance(
        regions=(my_instance,), size=CONS["ELEMENT_SEED_SIZE"]
    )
    my_assembly.generateMesh(regions=(my_instance,))

    # Create and submit job
    job_name = model_name
    my_job = ABQ.mdb.Job(
        name=job_name, model=model_name, description="Foot design"
    )
    my_job.submit()
    my_job.waitForCompletion()

    # Read the field output
    my_odb = odbAccess.openOdb(path=job_name + ".odb")
    last_step = my_odb.steps["LoadStep"]
    last_frame = last_step.frames[-1]
    field_outputs = last_frame.fieldOutputs["S"]
    field_output = max(
        [getattr(value, "mises") for value in field_outputs.values]
    )

    # Read the history output
    history_region_name = last_step.historyRegions.keys()[0]
    history_region = last_step.historyRegions[history_region_name]
    history_output = [
        value.data[-1][-1]
        for value in history_region.historyOutputs.values()[:2]
    ]

    if is_planar:
        # Get the area
        objective = my_part.getArea(faces=my_part.faces)
    else:
        objective = my_part.getVolume(cells=my_part.cells)

    # Print result photo, just for Mises
    if print_photo:
        # View the result (not working with noGUI)
        my_odb = visualization.openOdb(path=job_name + ".odb")
        my_viewport = ABQ.session.viewports["Viewport: 1"]
        my_viewport.setValues(displayedObject=my_odb)
        my_viewport.view.fitView()
        my_viewport.odbDisplay.display.setValues(plotState=ABC.CONTOURS_ON_DEF)
        my_viewport.odbDisplay.setPrimaryVariable(
            variableLabel="S",
            outputPosition=ABC.INTEGRATION_POINT,
            refinement=(ABC.INVARIANT, "Mises"),
        )
        my_viewport.odbDisplay.commonOptions.setValues(renderStyle=ABC.FILLED)

        # Export image
        my_viewport.view.pan(xFraction=0.1)
        ABQ.session.defaultViewportAnnotationOptions.setValues(
            title=ABC.OFF, state=ABC.OFF, triad=ABC.OFF
        )
        ABQ.session.printOptions.setValues(
            rendition=ABC.COLOR, vpDecorations=ABC.OFF, vpBackground=ABC.OFF
        )
        ABQ.session.printToFile(
            fileName=job_name, format=ABC.PNG, canvasObjects=(my_viewport,)
        )

    # Close output database and delete the model
    my_odb.close()
    del my_model

    # Delete unnecessary files
    remove_unnecessary_files(job_name)

    return {
        "objective": objective,
        "field_output": field_output,
        "history_output": history_output,
    }


if __name__ == "__main__":
    system_arguments = sys.argv[8:]
    if system_arguments:
        try:
            points = ast.literal_eval("".join(system_arguments))
        except SyntaxError:
            points = ast.literal_eval(",".join(system_arguments))
    else:
        points = [
            [114.40712390296207, 154.4548506587745],
            [155.83216298727956, 153.69293386572238],
            [158.73231133486775, 131.575630521931],
            [100.39661174612677, 97.96224914262834],
            [133.59506590428762, 34.38834774229362],
            [317.4845802401193, 28.45614216554591],
            [323.72203751729865, 11.091371502325634],
            [58.67622185352986, 10.24172336521795],
            [68.69993077132263, 29.048814235453474],
            [108.70961349716724, 32.43813789262146],
            [83.1338504234908, 71.65940041608457],
            [116.8888742298014, 135.3959448675419],
        ]

    _print_(finite_element_analysis(points))
