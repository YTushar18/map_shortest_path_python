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

# Variables to store the selected cities
source_city = None
destination_city = None

# Function to calculate the shortest path and display it on the map
def calculate_shortest_path():
    try:
        source_name = cities_combo.currentText()
        destination_name = cities_combo2.currentText()

        source_location = ox.geocode(source_name + ", California, USA")
        destination_location = ox.geocode(destination_name + ", California, USA")

        print(source_location, destination_location)

        # Find the nearest nodes in the network
        # source_node = ox.distance.nearest_nodes(G, source_location[1], source_location[0])
        # target_node = ox.distance.nearest_nodes(G, destination_location[1], destination_location[0])
        # # Find the nearest nodes in the network
        source_node = ox.nearest_nodes(G, source_location[1], source_location[0])
        target_node = ox.nearest_nodes(G, destination_location[1], destination_location[0])

        # Calculate shortest path
        shortest_path = nx.shortest_path(G, source_node, target_node, weight="length")

        # Highlight shortest path on map
        path_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
        folium.PolyLine(locations=path_coordinates, color='red', weight=5).add_to(mymap)

        # Update the map display
        map_widget.setHtml(mymap.get_root().render())

    except Exception as e:
        print("Error:", e)

# Function to clear all paths and refresh the map
def refresh_map():
    global mymap
    mymap = folium.Map(location=map_center, zoom_start=12)
    Geocoder().add_to(mymap)
    map_widget.setHtml(mymap.get_root().render())

# Specify the city or location
place_name = "Orange County, California, USA"

# Download the street network for the specified location
G = ox.graph_from_place(place_name, network_type="drive")

# Create an interactive map centered around the city
map_center = ox.geocode(place_name)
mymap = folium.Map(location=map_center, zoom_start=12)
Geocoder().add_to(mymap)
# Add LatLngPopup feature to allow manual entry of latitude and longitude
mymap.add_child(folium.features.LatLngPopup())

# Create the main application window
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Shortest Path Finder")

# Create a layout for the map
layout = QVBoxLayout()

# Create dropdowns for source and destination cities
cities_combo = QComboBox()
cities_combo.addItems(cities)
layout.addWidget(cities_combo)

cities_combo2 = QComboBox()
cities_combo2.addItems(cities)
layout.addWidget(cities_combo2)

# Button to calculate shortest path
btn_run = QPushButton("Get Shortest Path")
btn_run.clicked.connect(calculate_shortest_path)
layout.addWidget(btn_run)

# Button to refresh map and clear paths
btn_refresh = QPushButton("Refresh")
btn_refresh.clicked.connect(refresh_map)
layout.addWidget(btn_refresh)

# Create a widget to display the map
map_widget = QWebEngineView()
map_widget.setHtml(mymap.get_root().render())
layout.addWidget(map_widget)

# Create a widget to hold the layout
widget = QWidget()
widget.setLayout(layout)
window.setCentralWidget(widget)

# Display the main application window
window.show()

# Run the application
sys.exit(app.exec_())
