import os

from commonroad.scenario.scenario import Tag
from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile
from commonroad.planning.planning_problem import PlanningProblemSet

from crdesigner.map_conversion.opendrive.opendrive_parser.parser import parse_opendrive
from crdesigner.map_conversion.opendrive.opendrive_conversion.network import Network

from crdesigner.map_conversion.map_conversion_interface import opendrive_to_commonroad
from crdesigner.configurations.get_configs import get_configs

input_path = "C:/Users/Napoleon the Beast/Documents/TianZheng/commonroad-scenario-designer/ScenarioBasic.xodr"  # replace empty string

# load configuration
config = get_configs()

# ----------------------------------------------- Option 1: General API ------------------------------------------------
# load OpenDRIVE file, parse it, and convert it to a CommonRoad scenario

scenario = opendrive_to_commonroad(input_path)

# store converted file as CommonRoad scenario
writer = CommonRoadFileWriter(
    scenario=scenario,
    planning_problem_set=PlanningProblemSet(),
    author=config.file_header.author,
    affiliation=config.file_header.affiliation,
    source=config.file_header.source,
    tags={Tag.URBAN},
)
writer.write_to_file(os.path.dirname(os.path.realpath(__file__)) + "/" + "ZAM_OpenDRIVETest-1_1-T1.xml",
                     OverwriteExistingFile.ALWAYS)


# --------------------------------------- Option 2: OpenDRIVE conversion APIs ------------------------------------------
# OpenDRIVE parser to load file
opendrive = parse_opendrive(input_path)

# create OpenDRIVE intermediate network object from configuration
road_network = Network(config.opendrive)

# convert OpenDRIVE file
road_network.load_opendrive(opendrive)

# export to CommonRoad scenario
scenario = road_network.export_commonroad_scenario()

# store converted file as CommonRoad scenario
writer = CommonRoadFileWriter(
    scenario=scenario,
    planning_problem_set=PlanningProblemSet(),
    author=config.file_header.author,
    affiliation=config.file_header.affiliation,
    source=config.file_header.source,
    tags={Tag.URBAN},
)
writer.write_to_file(os.path.dirname(os.path.realpath(__file__)) + "/" + "ZAM_OpenDRIVETest-1_1-T2.xml",
                     OverwriteExistingFile.ALWAYS)
