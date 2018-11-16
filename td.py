from flask import Flask, request, send_file, render_template
import matplotlib.pyplot as plt
from sklearn.cluster import *
from staticmap import *
import overpy
import time

## SETUP
app = Flask(__name__)
api = overpy.Overpass()
m = StaticMap(400, 400, 10, 10)


def get_nodes(bbox: list) -> list:
    return api.query("[out:json][timeout:25];(node({0}, {1}, {2}, {3}););out;".format(*bbox)).nodes


def kmeans(x: list, y: list) -> list:
    X = list(zip(x, y))
    kmeans = KMeans(n_clusters=5, random_state=0)
    return kmeans.fit_predict(X)


def calculate_cluster_density(cluster: list) -> float:
    x = [float(node.lat) for node in cluster]
    y = [float(node.lon) for node in cluster]

    print(x, y)

def run(bbox: list) -> None:

    ## GET NODES
    nodes = get_nodes(bbox)

    ## FILTER NODES BY TYPE
    nodes = [node for node in nodes if "amenity" in node.tags]

    ## FORMAT NODES TO LIST OF (x, y) POSITIONS
    data = kmeans([node.lat for node in nodes], [node.lon for node in nodes])

    ## COMBINE NODE AND CLUSTER NUMBER
    clustered_nodes = list(zip(nodes, data))

    ## PLOT
    plt.scatter(x = [node[0].lat for node in clustered_nodes],
                y = [node[0].lon for node in clustered_nodes],
                c = [node[1] for node in clustered_nodes])


bbox = [55.6489237434721,12.505874633789062,55.71811887501279,12.641658782958984]
run(bbox)
plt.show()
#print(calculate_cluster_density([node[0] for node in run(bbox) if node[1] == 1]))
@app.route('/cluster')
def get_clusters_from_bbox():

    bbox = request.args.get('bbox').split(',') or [55.67771296159718, 12.580944299697876, 55.67879428149783, 12.583065927028654]
    bbox = [float(pos) for pos in bbox]

    print(bbox)
    run(bbox)

    plt.savefig("./test.png")
    plt.clf()

    time.sleep(1)
    return send_file("./test.png")
