# Flake8: noqa
"""This is kernel file that uses abaqus kernel for modeling and analyse jobs.
You should not modify this.
"""
# from __future__ import print_function
# Abaqus related modules
from abaqus import *
from abaqusConstants import *
import part
import sketch
import material
import section
import assembly
import step
import load
import job
import mesh
import odbAccess

# Standard modules
import visualization
import os
import sys
import ast
import random

# Other modules
from sub.inputprocess import *


def _print_(string):
    """Print a string to command prompt if running scrip within abaqus cae.
    Return nothing
    """
    print >>sys.__stdout__, string
    # print(string, file=sys.__stdout__)


def remove_unnecessary_files(file_name):
    """Delete unused files. Return nothing"""
    for type in UNUSED_FILES:
        if os.path.isfile(file_name + type):
            try:
                os.remove(file_name + type)
            except Exception:
                pass


# def coordinates_to_points(coordinates):
#     """Merge coordinates list to points list. Rerurn 2-dim array"""
#     points = []
#     for index in range(0, len(coordinates), 2):
#         x_coordinate = coordinates[index]
#         y_coordinate = coordinates[index + 1]
#         points.append([x_coordinate, y_coordinate])
#     return points


def finite_element_analysis(points, print_photo=PHOTO_MODE):
    model_name = "Model" + "_" + str(random.random())[2:]

    # Create a models
    my_model = mdb.Model(name=model_name)

    # Create a part
    rules_dict = create_rules()
    my_sketch = my_model.ConstrainedSketch(name="Profile", sheetSize=300.0)
    # Create lines by 2 points
    for index in rules_dict["Lines"]:
        my_sketch.Line(
            point1=points[index[0] - 1], point2=points[index[1] - 1]
        )
    # Create arcs by 3 points
    for index in rules_dict["Arcs"]:
        my_sketch.Arc3Points(
            point1=points[index[0] - 1],
            point2=points[index[2] - 1],
            point3=points[index[1] - 1],
        )
    # Create 3D part by extrusion
    my_part = my_model.Part(
        name="FootPart", dimensionality=THREE_D, type=DEFORMABLE_BODY
    )
    my_part.BaseSolidExtrude(sketch=my_sketch, depth=DEPTH)

    # Create a material
    my_material = my_model.Material(name="POM")
    my_material.Elastic(table=((YOUNGS_MODULUS, POISSONS_RATIO),))

    # Create section
    my_model.HomogeneousSolidSection(
        name="FootSection", material="POM", thickness=1.0
    )
    my_part.SectionAssignment(
        region=(my_part.cells,), sectionName="FootSection"
    )

    # Create an instance
    my_assembly = my_model.rootAssembly
    my_instance = my_assembly.Instance(
        name="FootInstance", part=my_part, dependent=OFF
    )

    # Create a step
    my_step = my_model.StaticStep(
        name="LoadStep",
        previous="Initial",
        timePeriod=1.0,
        initialInc=0.1,
        description="Weight of patient",
    )
    my_step.setValues(initialInc=1.0)
    # Create field output request and set one frame only
    my_field_request = my_model.fieldOutputRequests["F-Output-1"]
    my_field_request.setValues(variables=(OUTPUT_VARIABLE,))
    del my_model.historyOutputRequests["H-Output-1"]

    # Fix face and apply load
    fixed_face_center = (
        (points[6][0] + points[7][0]) / 2,
        (points[6][1] + points[7][1]) / 2,
        DEPTH / 2,
    )
    loaded_face_center = (
        (points[0][0] + points[1][0]) / 2,
        (points[0][1] + points[1][1]) / 2,
        DEPTH / 2,
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
        region=((loaded_face, SIDE1),),
        magnitude=LOAD_MAGNITUDE,
    )

    # Mesh the instance
    my_element_type = mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD)
    my_assembly.setElementType(
        regions=(my_instance.cells,), elemTypes=(my_element_type,)
    )
    my_assembly.seedPartInstance(
        regions=(my_instance,), size=ELEMENT_SEED_SIZE
    )
    my_assembly.generateMesh(regions=(my_instance,))

    # Create and submit job
    job_name = model_name
    my_job = mdb.Job(
        name=job_name, model=model_name, description="Foot design"
    )
    my_job.submit()
    my_job.waitForCompletion()

    # Read the ESEDEN result
    my_odb = odbAccess.openOdb(path=job_name + ".odb")
    my_last_frame = my_odb.steps["LoadStep"].frames[-1]
    total_energy_density = my_last_frame.fieldOutputs["ESEDEN"]
    elements_data = []
    for index in total_energy_density.values:
        elements_data.append(index.data)

    if print_photo:
        # View the result (not working with noGUI)
        my_odb = visualization.openOdb(path=job_name + ".odb")
        my_viewport = session.viewports["Viewport: 1"]
        my_viewport.setValues(displayedObject=my_odb)
        my_viewport.view.fitView()
        my_viewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
        my_viewport.odbDisplay.setPrimaryVariable(
            variableLabel="ESEDEN", outputPosition=WHOLE_ELEMENT
        )
        my_viewport.odbDisplay.commonOptions.setValues(renderStyle=FILLED)

        # Export image
        my_viewport.view.pan(xFraction=0.1)
        session.defaultViewportAnnotationOptions.setValues(
            title=OFF, state=OFF, triad=OFF
        )
        session.printOptions.setValues(
            rendition=COLOR, vpDecorations=OFF, vpBackground=OFF
        )
        session.printToFile(
            fileName=job_name, format=PNG, canvasObjects=(my_viewport,)
        )

    # Close output database and delete the model
    my_odb.close()
    del my_model

    # Delete unnecessary files
    remove_unnecessary_files(job_name)

    return {"objective": max(elements_data)}


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
