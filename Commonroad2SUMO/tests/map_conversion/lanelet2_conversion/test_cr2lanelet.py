
import os
import unittest
from crdesigner.map_conversion.lanelet2.cr2lanelet import CR2LaneletConverter
from commonroad.scenario.lanelet import Lanelet, StopLine, LineMarking
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.scenario.traffic_sign import * 
from pyproj import Proj

# creating a testing vertices and a testing scenario from a test file (xml)
right_vertices = np.array([[0, 0], [1, 0], [2, 0]])
left_vertices = np.array([[0, 1], [1, 1], [2, 1]])
center_vertices = np.array([[0, .5], [1, .5], [2, .5]])
lanelet = Lanelet(left_vertices, center_vertices, right_vertices, 100)

left_vertices2 = np.array([[0, 0], [1, 0], [2, 0]])
right_vertices2 = np.array([[0, -1], [1, -1], [2, -1]])
center_vertices2 = np.array([[0, -0.5], [1, -0.5], [2, -0.5]])
lanelet2 = Lanelet(left_vertices2, center_vertices2, right_vertices2, 105)
lanelet2._adj_left = 100


# loading a file for a scenario
commonroad_reader = CommonRoadFileReader(
            f"{os.path.dirname(os.path.realpath(__file__))}/../test_maps/lanelet2/merging_lanelets_utm.xml"
        )

# creating a scenario with the .open() function
scenario, _ = commonroad_reader.open()


class TestCR2LaneletConverter(unittest.TestCase):

    def test_init(self):
        # test the initialization values without opening the scenario
        cr1 = CR2LaneletConverter()
        self.assertEqual(cr1.id_count, -1)
        self.assertIsNone(cr1.first_nodes) 
        self.assertIsNone(cr1.last_nodes) 
        self.assertIsNone(cr1.left_ways) 
        self.assertIsNone(cr1.right_ways)
        self.assertIsNone(cr1.lanelet_network)
        self.assertIsNone(cr1.origin_utm)
        self.assertEqual(cr1.proj, Proj("+proj=utm +zone=32 +ellps=WGS84"))  # default proj
    
    def test_init_with_scenario(self):
        # test the initialization with the custom proj scenario
        custom_proj_scen = "+proj=utm +zone=59 south"
        cr1 = CR2LaneletConverter(custom_proj_scen)  # object referred to as "self" in the source code
        self.assertEqual(cr1.proj, Proj(custom_proj_scen))

    def test_id_count(self):
        # test assigning id
        cr1 = CR2LaneletConverter()
        self.assertEqual(cr1.id_count, -1)
        self.assertEqual(cr1.id_count, -2)
        self.assertEqual(cr1.id_count, -3)
        cr2 = CR2LaneletConverter()
        self.assertEqual(cr2.id_count, -1)
        self.assertEqual(cr2.id_count, -2)
        self.assertEqual(cr2.id_count, -3)
    
    def test_call(self):
        # checking if the lanelet networks are the same
        cr1 = CR2LaneletConverter()

        # check if the dicts are empty
        self.assertFalse(cr1.first_nodes)
        self.assertFalse(cr1.last_nodes)
        self.assertFalse(cr1.left_ways)
        self.assertFalse(cr1.right_ways)
        
        cr1(scenario)
        self.assertEqual(scenario.lanelet_network, cr1.lanelet_network)  # check the lanelet network of the scenario
        self.assertEqual(cr1.origin_utm, cr1.proj(scenario.location.gps_longitude, scenario.location.gps_latitude))

    def test_convert_lanelet(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)

        # calculating the number of way relations before and after the function
        len_of_way_relations_before = len(cr1.osm.way_relations)
        cr1._convert_lanelet(lanelet)
        len_of_way_relations_after = len(cr1.osm.way_relations)
        
        # save the id variable as the count rises at every call
        idCount = cr1.id_count + 1 
        last_way_relation = list(cr1.osm.way_relations)[-1]

        # testing if the function has added a way relation to the osm
        self.assertEqual(len_of_way_relations_after, len_of_way_relations_before+1)

        # testing the right id of the left way
        self.assertEqual(cr1.osm.way_relations[last_way_relation].left_way, str(idCount+2))

        # testing the right id of the right way
        self.assertEqual(cr1.osm.way_relations[last_way_relation].right_way, str(idCount+1))

        # testing the right id of the created way relation
        self.assertEqual(cr1.osm.way_relations[last_way_relation].id_, str(idCount))

        # testing the right entry in the dict
        self.assertEqual(cr1.osm.way_relations[last_way_relation].tag_dict, {'type': 'lanelet'})

    def test_create_nodes(self):
        cr = CR2LaneletConverter()
        cr(scenario)

        tup = cr._create_nodes(lanelet, None, None)
        left_nodes = list(cr.osm.nodes)[-6:-3]  # getting the last created leftNodes
        right_nodes = list(cr.osm.nodes)[-3:]  # getting the last created right nodes

        # tup[0] is the list of the created left nodes from our function "create_nodes"
        self.assertEqual(left_nodes, tup[0])

        # tup[1] is the list of the created right nodes from our function "create_nodes"
        self.assertEqual(right_nodes, tup[1])

    def test_get_first_and_last_nodes_from_way(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)
        cr1._convert_lanelet(lanelet)
      
        # getting the created ways from our lanelet
        last_left_way = list(cr1.osm.ways)[-2]
        last_right_way = list(cr1.osm.ways)[-1]

        # getting the first and the last nodes in a tuple
        leftNodeTuple = cr1._get_first_and_last_nodes_from_way(last_left_way, True)
        rightNodeTuple = cr1._get_first_and_last_nodes_from_way(last_right_way, True)

        # testing if the first node in the corresponding way is the same as the first node in the tuple
        self.assertEqual(cr1.osm.ways[last_left_way].nodes[0], leftNodeTuple[0])

        # testing if the first node in the corresponding way is the same as the last node in the tuple
        self.assertEqual(cr1.osm.ways[last_left_way].nodes[-1], leftNodeTuple[1])

        # testing if the first node in the corresponding way is the same as the first node in the tuple
        self.assertEqual(cr1.osm.ways[last_right_way].nodes[0], rightNodeTuple[0])

        # testing if the first node in the corresponding way is the same as the last node in the tuple
        self.assertEqual(cr1.osm.ways[last_right_way].nodes[-1], rightNodeTuple[1])

    def test_create_nodes_from_vertices(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)
        left_nodes = cr1._create_nodes_from_vertices(list(left_vertices))
        right_nodes = cr1._create_nodes_from_vertices(list(right_vertices))
        self.assertEqual(len(right_nodes), 3)  # test the size of the right node array
        self.assertEqual(len(left_nodes), 3)  # test the size of the left node array

        # as I have some problems with the inverse of "proj" function, I have created testLonRight and testLatRight
        # variables with the coordinates of the first right node (0,0) and the last left node (2,1)
        testLonRight, testLatRight = cr1.proj(cr1.origin_utm[0]+0, cr1.origin_utm[1]+0, inverse=True)
        self.assertEqual(str(testLonRight), cr1.osm.nodes[right_nodes[0]].lon)  # test the lon coordinates of the node
        self.assertEqual(str(testLatRight), cr1.osm.nodes[right_nodes[0]].lat)  # test the lat coordinate of the node
        testLonLeft, testLatLeft = cr1.proj(cr1.origin_utm[0]+2, cr1.origin_utm[1]+1, inverse=True)
        self.assertEqual(str(testLonLeft), cr1.osm.nodes[left_nodes[2]].lon)  # test the lon coordinate of the node
        self.assertEqual(str(testLatLeft), cr1.osm.nodes[left_nodes[2]].lat)  # test the lat coordinate of the node
        
    def test_get_potential_left_way(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)

        # As I can not seem to insert my custom lanelets directly into the scenario,
        # a new testing lanelet is created and will be compared to a lanelet already in the scenario
        # As the both sides (left and right) are being tested, both vertices of the existing lanelet
        # have been created, and will be assigned to the new lanelet depending on the testing needs
        test_right = cr1.lanelet_network.lanelets[11].right_vertices 
        test_left = cr1.lanelet_network.lanelets[11].left_vertices 

        # testing the same direction, left side, meaning that the right vertices is equal to the opposing left

        # right_vertices of the new Lanelet are the same as left_vertices of the lanelet (id 11) that is already in
        # the scenario.
        laneletTest = Lanelet(test_right, center_vertices, right_vertices, lanelet_id=150)
        laneletTest._adj_left = 12  # assigning our lanelet[11] as the adjacent left to our test lanelet.

        # if the direction is the same, then the left way should be equal to the right one of some other lanelet
        laneletTest.adj_left_same_direction = True
        self.assertEqual(cr1._get_potential_left_way(laneletTest), cr1.right_ways.get(laneletTest.adj_left))

        # testing the different direction, left side, meaning that the left vertices are equal,
        # but reversed (hence the [::-1])
        laneletTest = Lanelet(test_left[::-1], center_vertices, right_vertices, lanelet_id=150)
        laneletTest._adj_left = 12  # assigning our lanelet[11] as the adjacent left to our test lanelet.
        laneletTest.adj_left_same_direction = False 
        self.assertEqual(cr1._get_potential_left_way(laneletTest), cr1.left_ways.get(laneletTest.adj_left))

    def test_get_potential_right_way(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)

        # same logic as in the previous testing, just for the right side, same direction
        test_right = cr1.lanelet_network.lanelets[11].right_vertices 
        test_left = cr1.lanelet_network.lanelets[11].left_vertices

        # new Lanelet has the same right_vertices as left_vertices of the lanelet (id 11) that is already in the
        # scenario.
        laneletTest = Lanelet(left_vertices, center_vertices, test_left, lanelet_id=150)

        # assigning our lanelet[11] (it has id 12) as the adjacent left to our test lanelet.
        laneletTest._adj_right = 12
        laneletTest.adj_right_same_direction = True 
        self.assertEqual(cr1._get_potential_right_way(laneletTest), cr1.left_ways.get(laneletTest.adj_right))

        # right side, different direction

        # new Lanelet has the same right_vertices as left_vertices of the lanelet (id 11) that is already in the
        # scenario.
        laneletTest = Lanelet(left_vertices, center_vertices, test_right[::-1], lanelet_id=150)

        # assigning our lanelet[11] (it has id 12) as the adjacent left to our test lanelet.
        laneletTest._adj_right = 12
        laneletTest.adj_right_same_direction = False
        self.assertEqual(cr1._get_potential_right_way(laneletTest), cr1.right_ways.get(laneletTest.adj_right))
    
    def test_get_shared_first_nodes_from_other_lanelets(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)
        # creating a lanelet that will have the same first nodes as some random lanelet already in the scenario
        lv = np.array([[-134.8145, 22.3995], [-135, 23]])  # same beginning of the node, end does not matter
        rv = np.array([[-134.791, 25.5844], [-135, 26]])  # same beginning of the node, end does not matter
        cv = np.array([[0, 0], [0, 0]])  # does not matter
        laneletTest = Lanelet(lv, rv, cv, 100)

        # adding the lanelet which coordinates have been used in vertices as the predecessor
        laneletTest.predecessor = [2]

        # calling the function
        nodes = cr1._get_shared_first_nodes_from_other_lanelets(laneletTest)

        # if the function works accordingly, the value of the "nodes" variable
        # should be equal to the value of the cr1.last_nodes at the same index of our lanelet 2.
        self.assertEqual(nodes, cr1.last_nodes[2])
        cr1.lanelet_network.remove_lanelet(laneletTest)

    def test_get_shared_last_nodes_from_other_lanelets(self):
        cr1 = CR2LaneletConverter()
        cr1(scenario)
        # creating a lanelet that will have the same first nodes as some random lanelet already in the scenario
        lv = np.array([[-79, 15], [-80.9075, 16.1302]])  # same beginning of the node, end does not matter
        rv = np.array([[-79, 18], [-80.3486, 19.5818]])  # same beginning of the node, end does not matter
        cv = np.array([[0, 0], [0, 0]])  # does not matter
        laneletTest = Lanelet(lv, rv, cv, 100)

        # adding the lanelet which coordinates have been used in vertices as the predecessor
        laneletTest.successor = [2]
        
        # calling the function
        nodes = cr1._get_shared_last_nodes_from_other_lanelets(laneletTest)

        # if the function works accordingly, the value of the "nodes" variable should be
        # equal to the value of the cr1.first_nodes at the same index of our lanelet 2.
        self.assertEqual(nodes, cr1.first_nodes[2])

    def test__convert_traffic_sign(self):
        # function takes a traffic sign and maps it as a way

        cr1 = CR2LaneletConverter()
        cr1(scenario)

        # traffic sign element list with one traffic sign
        tse = TrafficSignElement(TrafficSignIDGermany.STOP)
        list_tse = list()
        list_tse.append(tse)

        # position at the beginning of global lanelet
        position = np.array([0, 0])

        # creating the sign, referenced to global lanelet
        sign = TrafficSign(1, list_tse, {100}, position)

        # before converting a sign
        ways_before = len(cr1.osm.ways)
        cr1._convert_traffic_sign(sign)
        ways_after = len(cr1.osm.ways)
        # there should be 1 more way in the osm
        self.assertEqual(ways_before+1, ways_after)

        # check the attributes of our way, do they match the sign

        # get the id of our way, as it is the last one in the osm way list
        id_converted_sign = list(cr1.osm.ways)[-1]

        # get the way from the id
        sign_as_way = cr1.osm.ways[id_converted_sign]

        # extract the nodes
        n1_id, n2_id = sign_as_way.nodes
        n1 = cr1.osm.nodes[n1_id]
        n2 = cr1.osm.nodes[n2_id]

        # compare the node coordinates
        # transform the coordinates of the sign, should get the same coordinates as ones of the newly created way
        sign_n1_lon, sign_n1_lat = cr1.proj(cr1.origin_utm[0] + sign.position[0],
                                            cr1.origin_utm[1] + sign.position[1], inverse=True)
        
        self.assertEqual(str(sign_n1_lon), n1.lon)
        self.assertEqual(str(sign_n1_lat), n1.lat)
        
        # as stated in the original function, second node is created to match the L2 format
        sign_n2_lon, sign_n2_lat = cr1.proj(cr1.origin_utm[0] + sign.position[1]+0.25,
                                            cr1.origin_utm[1] + sign.position[1]+0.25, inverse=True)
        self.assertEqual(str(sign_n2_lon), n2.lon)
        self.assertEqual(str(sign_n2_lat), n2.lat)

        # check the type of way

        type = sign_as_way.tag_dict["type"]
        self.assertEqual(type, "traffic_sign")
    
    def test__add_rightOfWayRelation(self):
        """
        """
        # working with the local scenario as it reflects the entire file if I change it globally
        commonroad_reader = CommonRoadFileReader(
            f"{os.path.dirname(os.path.realpath(__file__))}/../test_maps/lanelet2/merging_lanelets_utm.xml"
        )
        scenario, _ = commonroad_reader.open()
        cr1 = CR2LaneletConverter()
        cr1(scenario)

        count_before = 0
        for way_rel_id in cr1.osm.regulatory_elements:
            way_rel = cr1.osm.find_right_of_way_by_id(way_rel_id)
            if way_rel.tag_dict["subtype"] == "right_of_way":
                for signs in way_rel.refers:
                    count_before += 1
        
        # create a sign, so it could be added to the right_of_way_relation
        tse = TrafficSignElement(TrafficSignIDGermany.RIGHT_OF_WAY)
        list_tse = list()
        list_tse.append(tse)
        # position at the beginning of global lanelet
        position = np.array([0, 0])
        # creating the sign, referenced to a random lanelet with id 1
        sign = TrafficSign(1, list_tse, {1}, position)

        # add sign to lanelet_traffic_sign, then convert it
        cr1.lanelet_network.lanelets[0].traffic_signs.add(1)
        cr1.lanelet_network._traffic_signs.update({1: sign})
        
        # create a stop line and append it to our lanelet
        cr1.lanelet_network.lanelets[0].stop_line = StopLine(np.array([0, 0]), np.array([1, 1]),
                                                             line_marking=LineMarking.DASHED, traffic_sign_ref={1})
        stop_lines_before = 0
        for w in cr1.osm.ways:
            if len(cr1.osm.ways[w].tag_dict.keys()) > 0:
                if cr1.osm.ways[w].tag_dict["type"] == "stop_line":
                    stop_lines_before += 1

        # convert the sign so that it maps to our osm file
        cr1._convert_traffic_sign(sign)

        # call the function, which should add a right_of_way regulatory element to the osm file
        cr1._add_right_of_way_relation()
        
        count_after = 0
        for way_rel_id in cr1.osm.regulatory_elements:
            way_rel = cr1.osm.find_right_of_way_by_id(way_rel_id)
            if way_rel.tag_dict["subtype"] == "right_of_way":
                for wayid in way_rel.refers:
                    # check if we have mapped correctly
                    way = cr1.osm.ways[wayid]
                    n1_id, n2_id = way.nodes
                    n1 = cr1.osm.nodes[n1_id]
                    n2 = cr1.osm.nodes[n2_id]
                    sign_n1_lon, sign_n1_lat = cr1.proj(cr1.origin_utm[0] + sign.position[0],
                                                        cr1.origin_utm[1] + sign.position[1], inverse=True)
                    self.assertEqual(str(sign_n1_lon), n1.lon)
                    self.assertEqual(str(sign_n1_lat), n1.lat)
                    sign_n2_lon, sign_n2_lat = cr1.proj(cr1.origin_utm[0] + sign.position[1]+0.25,
                                                        cr1.origin_utm[1] + sign.position[1]+0.25, inverse=True)
                    self.assertEqual(str(sign_n2_lon), n2.lon)
                    self.assertEqual(str(sign_n2_lat), n2.lat)
                    count_after += 1
        
        # check if we have added the sign to the way relation
        self.assertEqual(count_before+1, count_after)

        stop_lines_after = 0
        for w in cr1.osm.ways:
            if len(cr1.osm.ways[w].tag_dict.keys()) > 0:
                if cr1.osm.ways[w].tag_dict["type"] == "stop_line":
                    stop_lines_after += 1
        self.assertEqual(stop_lines_before+1, stop_lines_after)

    def test__convert_traffic_light(self):
        # working with the local scenario as it reflects the entire file if I change it globally
        commonroad_reader = CommonRoadFileReader(
            f"{os.path.dirname(os.path.realpath(__file__))}/../test_maps/lanelet2/merging_lanelets_utm.xml"
        )
        scenario, _ = commonroad_reader.open()
        cr1 = CR2LaneletConverter()
        cr1(scenario)

        # create a custom CR format traffic light
        traffic_cycle_element_list = list()
        traffic_cycle_element_list.append(TrafficLightCycleElement(TrafficLightState.RED, 1))
        traffic_light = TrafficLight(1, traffic_cycle_element_list, np.array([0, 0]))
        
        nodes_before = len(cr1.osm.nodes)
        ways_before = len(cr1.osm.ways)

        # call the function to convert it to the osm format
        # the osm should add 3 nodes for its position, along with creating a way, similar to traffic sign
        cr1._convert_traffic_light(traffic_light)

        nodes_after = len(cr1.osm.nodes)
        ways_after = len(cr1.osm.ways)
        
        self.assertEqual(nodes_before+3, nodes_after)
        self.assertEqual(ways_before+1, ways_after)
        
        # check if properties of the way are as they should be:

        # check if the position of new nodes corresponds to the CR format
        # (for now the position of the traffic light is diagonal)
        x1, y1 = cr1.proj(cr1.origin_utm[0] + traffic_light.position[0],
                          cr1.origin_utm[1] + traffic_light.position[1], inverse=True)
        # for now, the traffic light gets position with this formula (a diagonal line)
        x2, y2 = cr1.proj(cr1.origin_utm[0] + traffic_light.position[0]+0.1,
                          cr1.origin_utm[1] + traffic_light.position[1]+0.1, inverse=True)
        x3, y3 = cr1.proj(cr1.origin_utm[0] + traffic_light.position[0]-0.1,
                          cr1.origin_utm[1] + traffic_light.position[1]-0.1, inverse=True)

        n3_id = list(cr1.osm.nodes)[-1]
        n2_id = list(cr1.osm.nodes)[-2]
        n1_id = list(cr1.osm.nodes)[-3]

        n1 = cr1.osm.nodes[n1_id]
        n2 = cr1.osm.nodes[n2_id]
        n3 = cr1.osm.nodes[n3_id]

        self.assertEqual(str(x1), n1.lon)
        self.assertEqual(str(y1), n1.lat)
        self.assertEqual(str(x2), n2.lon)
        self.assertEqual(str(y2), n2.lat)
        self.assertEqual(str(x3), n3.lon)
        self.assertEqual(str(y3), n3.lat)

        # check if the mapped nodes correspond to the newly created ones
        last_created_way_id = list(cr1.osm.ways)[-1]
        last_created_way = cr1.osm.ways[last_created_way_id]

        self.assertEqual(n1_id, last_created_way.nodes[0])
        self.assertEqual(n2_id, last_created_way.nodes[1])
        self.assertEqual(n3_id, last_created_way.nodes[2])

        # check if the type is traffic light

        type = last_created_way.tag_dict["type"]
        self.assertEqual("traffic_light", type)

# test regulatory element left
    def test__add_regulatoryElementForTrafficLights(self):
        # working with the local scenario as it reflects the entire file if I change it globally
        commonroad_reader = CommonRoadFileReader(
            f"{os.path.dirname(os.path.realpath(__file__))}/../test_maps/lanelet2/merging_lanelets_utm.xml"
        )
        scenario, _ = commonroad_reader.open()
        cr1 = CR2LaneletConverter()
        cr1(scenario)
        
        # create a custom CR format traffic light
        traffic_cycle_element_list = list()
        traffic_cycle_element_list.append(TrafficLightCycleElement(TrafficLightState.RED, 1))
        traffic_light = TrafficLight(1, traffic_cycle_element_list, np.array([0, 0]))

        # assign it to a lanelet
        cr1.lanelet_network.lanelets[0].traffic_lights.add(1)

        # assign it to the lanelet network
        cr1.lanelet_network._traffic_lights.update({1: traffic_light})

        # count the number of traffic lights before the function
        count_before = 0
        for way_rel_id in cr1.osm.regulatory_elements:
            way_rel = cr1.osm.find_right_of_way_by_id(way_rel_id)
            if way_rel.tag_dict["subtype"] == "traffic_light":
                count_before += 1
        
        cr1._convert_traffic_light(traffic_light)
        cr1._add_regulatory_element_for_traffic_lights()

        # count the number of traffic lights after the function
        count_after = 0
        for way_rel_id in cr1.osm.regulatory_elements:
            way_rel = cr1.osm.find_right_of_way_by_id(way_rel_id)
            if way_rel.tag_dict["subtype"] == "traffic_light":
                count_after += 1

        # there should be one more
        self.assertEqual(count_before+1, count_after)

        # check if the traffic light has mapped correctly
        for re in cr1.osm.regulatory_elements:
            # it should refer to the newly created traffic light id
            for tl in cr1.osm.ways:
                if len(cr1.osm.ways[tl].tag_dict.keys()) != 0:
                    tl_id = str(tl)
        
                    self.assertEqual(cr1.osm.regulatory_elements[re].refers[0], tl_id)


if __name__ == '__main__':
    unittest.main()
