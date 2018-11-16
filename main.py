import matplotlib.pyplot as plt
import overpy
from sklearn.cluster import KMeans
from collections import Counter
from staticmap import *

from flask import Flask, send_file
app = Flask(__name__)



api = overpy.Overpass()
m = StaticMap(400, 400, 10, 10)
bbox = [55.67771296159718,12.580944299697876,55.67879428149783,12.583065927028654]

type_table = {"entertainment":("nightclub", "theater"),
              "shopping": (),
              "food / drinks": ("bar", "cafe", "resturant", "nightclub")}

blacklist = ["atm", "toilets", "drinking_water"]


def gen_query(bbox, amenity_filter=None):

    if amenity_filter is None:
        """ Return all nodes in area"""

        return api.query("[out:json][timeout:25];(node({0}, {1}, {2}, {3}););out;".format(*bbox)).nodes

    else:
        """ Return all nodes that fit the amenity filter"""

        return api.query("[out:json][timeout:25];({0});out;".format(
            ''.join(["""node["amenity"="{0}"]({1}, {2}, {3}, {4});""".format(
                amenity, *bbox) for amenity in amenity_filter]))).nodes


class Area:

    def __init__(self, bbox: list):
        self.bbox = bbox  # TODO replace BBOX with polygon list

    def get_nodes(self):
        return gen_query(self.bbox)

    @staticmethod
    def sort_node_types(nodes: list) -> list:
        """

        :param nodes: takes a list of overpass.api node types
        :return: a list of nodes with their type as a tuple   (node, nodetype)
        """
        sorted_nodes = []

        for node in nodes:

            if "amenity" in node.tags:
                sorted_nodes.append((node, "amenity"))
                continue

            if "shop" in node.tags:
                sorted_nodes.append((node, "shop"))

                continue

            if "office" in node.tags:
                sorted_nodes.append((node, "office"))

        return sorted_nodes

    @staticmethod
    def count_nodes_in_types(sorted_nodes: list) -> dict:
        """

        :param sorted_nodes: Takes the output of sort_node_types() as input
        :return: e.g. {"amenities": 432, "shops": 113}
        """

        return dict(Counter([node[1] for node in sorted_nodes]))

    def districtize(self, nodes: list) -> object:
        """

        :param nodes: Takes a list over overpass.api node types
        :return: a list of District objects
        """
        districts = {}

        ## FORMAT DATA

        type_sorted_nodes = self.sort_node_types(nodes)
        types = set([node[1] for node in type_sorted_nodes])

        for node_type in types:

            nodes_with_type = [node for node in type_sorted_nodes if node[1] == node_type]

            X = [[node[0].lon, node[0].lat] for node in nodes_with_type]
            kmeans = KMeans(n_clusters=3, random_state=0).fit_predict(X)

            x = [node[0] for node in X]
            y = [node[1] for node in X]

            tmp_c_map = {0: (255, 255, 0),
                         1: (255, 0, 255),
                         2: (0, 255, 255)}


            for i, j in enumerate(x):
                marker = CircleMarker((float(j), float(y[i])), color=tmp_c_map[kmeans[i]], width=5)
                m.add_marker(marker)
            break
        image = m.render(zoom=18)
        return image

    @staticmethod
    def visualize_nodes(X: list, y: list, c: list) -> None:
        """

        :param nodes: takes a list of tuples (node, nodetype)
        :return: No return type
        """




        #plt.scatter(X, y, c=c)
        image = m.render(zoom=15)
        image.show()
        #plt.show()



class District:

    def __init__(self, poly: list, type: str, nodes: list):
        self.poly = poly
        self.type = type
        self.nodes = nodes

import io

def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')



"""

for tp in ["amenity", "office", "shop", "residential"]:
    nodes = [node for node in t if node[1] == tp]
    data = [[node[0].lat, node[0].lon] for node in nodes]
    if len(data) == 0:
        continue



    kmn = list(zip([node[0].id for node in nodes], kmeans))
    print(Counter(kmn, key=lambda x: x[1]))

    #for enum, node in enumerate(nodes):
    #    plt.annotate(node[1], xy=data[enum])
    plt.scatter([x[0] for x in data], [x[1] for x in data], c=kmeans)

    #plt.show()
    input()
#area.visualize_nodes(t)"""