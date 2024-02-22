import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
from folium.plugins import Geocoder
import osmnx as ox
import networkx as nx

# Define a list of cities in California
cities = [
    "Aliso Viejo", "Anaheim", "Brea", "Buena Park", "Costa Mesa", "Cypress", "Dana Point",
    "Fountain Valley", "Fullerton", "Garden Grove", "Huntington Beach", "Irvine", "La Habra",
    "La Palma", "Laguna Beach", "Laguna Hills", "Laguna Niguel", "Laguna Woods", "Lake Forest",
    "Los Alamitos", "Mission Viejo", "Newport Beach", "Orange", "Placentia", "Rancho Santa Margarita",
    "San Clemente", "San Juan Capistrano", "Santa Ana", "Seal Beach", "Stanton", "Tustin",
    "Villa Park", "Westminster", "Yorba Linda"
]

# Function to block a road
def block_road():
    try:
        global G, blocked_nodes
        source_name = cities_combo.currentText()
        destination_name = cities_combo2.currentText()

        if source_name == destination_name:
            print("Source and destination cities cannot be the same.")
            return

        source_location = ox.geocode(source_name + ", California, USA")
        destination_location = ox.geocode(destination_name + ", California, USA")

        # Find the nearest nodes in the network
        source_node = ox.nearest_nodes(G, source_location[1], source_location[0])
        target_node = ox.nearest_nodes(G, destination_location[1], destination_location[0])

        print(f"Source node: {source_node}, Target node: {target_node}")

        # Calculate the shortest path
        shortest_path = nx.shortest_path(G, source_node, target_node, weight="length")

        # Remove a node or multiple nodes from the shortest path
        if len(shortest_path) > 2:
            # Remove the middle node(s)
            remove_node = shortest_path[len(shortest_path) // 2]
            blocked_nodes.append(remove_node)
            print(f"Node {remove_node} removed from the shortest path.")

        # Highlight shortest path on map
        path_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
        folium.PolyLine(locations=path_coordinates, color='red', weight=3).add_to(mymap)

        # Update the map display
        map_widget.setHtml(mymap.get_root().render())

        print("Blocked path between {} and {}, finding alternate path...".format(source_name, destination_name))

    except Exception as e:
        print("Error blocking road:", e)

# Function to calculate the shortest path
def calculate_shortest_path():
    try:
        global G, blocked_nodes
        source_name = cities_combo.currentText()
        destination_name = cities_combo2.currentText()

        source_location = ox.geocode(source_name + ", California, USA")
        destination_location = ox.geocode(destination_name + ", California, USA")

        # Find the nearest nodes in the network
        source_node = ox.nearest_nodes(G, source_location[1], source_location[0])
        target_node = ox.nearest_nodes(G, destination_location[1], destination_location[0])

        # Create a custom weight function
        def custom_weight(u, v, d):
            edge_data = d[next(iter(d))]  # Get the first (and only) edge data dictionary
            if u in blocked_nodes or v in blocked_nodes:
                return edge_data['length'] * 1000  # Penalize blocked nodes
            else:
                return edge_data['length']

        shortest_path = nx.shortest_path(G, source_node, target_node, weight=custom_weight)

        # Highlight shortest path on map
        path_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
        folium.PolyLine(locations=path_coordinates, color='blue', weight=5).add_to(mymap)

        # Update the map display
        map_widget.setHtml(mymap.get_root().render())

    except Exception as e:
        import traceback
        print("Error calculating path:", traceback.print_exc())

# Function to refresh the map
def refresh_map():
    global mymap, blocked_nodes
    mymap = folium.Map(location=map_center, zoom_start=12)
    Geocoder().add_to(mymap)
    blocked_nodes = []  # Reset blocked roads
    map_widget.setHtml(mymap.get_root().render())

# Initialize the map and GUI
place_name = "Orange County, California, USA"
G = ox.graph_from_place(place_name, network_type="drive")
map_center = ox.geocode(place_name)
mymap = folium.Map(location=map_center, zoom_start=12)
Geocoder().add_to(mymap)

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Orange County - Shortest Path Finder")

layout = QVBoxLayout()

cities_combo_label = QLabel("Select source city:")
layout.addWidget(cities_combo_label)
cities_combo = QComboBox()
cities_combo.addItems(cities)
layout.addWidget(cities_combo)

cities_combo2_label = QLabel("Select destination city:")
layout.addWidget(cities_combo2_label)
cities_combo2 = QComboBox()
cities_combo2.addItems(cities)
layout.addWidget(cities_combo2)

btn_run = QPushButton("Get Shortest Path")
btn_run.clicked.connect(lambda: calculate_shortest_path())
layout.addWidget(btn_run)

# Add a set to keep track of blocked roads
blocked_nodes = []

# Create a button to block the road
btn_block_road = QPushButton("Block Road")
btn_block_road.clicked.connect(block_road)
layout.addWidget(btn_block_road)

btn_refresh = QPushButton("Refresh")
btn_refresh.clicked.connect(refresh_map)
layout.addWidget(btn_refresh)

map_widget = QWebEngineView()
map_widget.setHtml(mymap.get_root().render())
layout.addWidget(map_widget)

widget = QWidget()
widget.setLayout(layout)
window.setCentralWidget(widget)

window.show()
sys.exit(app.exec_())
