import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
import alphashape
import csv

input_file = 'data/batch-geocoder-output-filtered-formatted-with-walkbikescore-over-thresholds.csv'
output_file = 'data/polygon-of-streets-with-walkandbike-score-over-thresholds.csv'
alpha_value = 130

def write_coords_to_file(filename, coords):
    with open(filename, 'w') as f:
        f.write("{},{}\n".format('lat','long'))
        for coord in coords:
            f.write("{},{}\n".format(coord[0], coord[1]))

def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)
    
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

def get_biggest_part(multipolygon):
    # Get the area of all mutipolygon parts
    areas = [i.area for i in multipolygon]

    # Get the area of the largest part
    max_area = areas.index(max(areas))    

    # Return the index of the largest area
    return multipolygon[max_area]

points = []

with open(input_file, 'r') as in_csv, open(output_file, 'w', newline='') as out_csv:
    reader = csv.reader(in_csv)    
    _ = next(reader)
    
    for row in reader:
        lat = float(row[5])
        lng = float(row[6])

        points.append([lat, lng])

points = np.array(points)

fig, ax = plt.subplots()
ax.scatter(*zip(*points))

alpha_shape = alphashape.alphashape(points, alpha_value)

if isinstance(alpha_shape, MultiPolygon):
    alpha_shape = get_biggest_part(alpha_shape.geoms)

print(alpha_shape)
write_coords_to_file(output_file, alpha_shape.exterior.coords)

plot_polygon(ax, alpha_shape, facecolor='lightblue', edgecolor='red', alpha=0.4)
plt.show()
