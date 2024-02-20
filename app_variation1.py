import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
from folium.plugins import Geocoder
import osmnx as ox
import networkx as nx

# Variables to store the selected markers
source_marker = None
destination_marker = None

# Function to calculate the shortest path and display it on the map
def calculate_shortest_path():
    try:
        lat1 = float(entry_lat1.text())
        lon1 = float(entry_lon1.text())
        lat2 = float(entry_lat2.text())
        lon2 = float(entry_lon2.text())

        # Find the nearest nodes in the network
        source_node = ox.distance.nearest_nodes(G, lon1, lat1)
        target_node = ox.distance.nearest_nodes(G, lon2, lat2)

        # Calculate shortest path
        shortest_path = nx.shortest_path(G, source_node, target_node, weight="length")

        # Highlight shortest path on map
        path_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
        folium.PolyLine(locations=path_coordinates, color='red', weight=5).add_to(mymap)

        # Update the map display
        map_widget.setHtml(mymap.get_root().render())

    except Exception as e:
        print("Error:", e)

# Specify the city or location
place_name = "Fullerton, California, USA"

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

# Create a widget to display the map
map_widget = QWebEngineView()
map_widget.setHtml(mymap.get_root().render())
layout.addWidget(map_widget)

# Create input boxes for source and destination latitude and longitude
lbl_lat1 = QLabel("Source Latitude:")
layout.addWidget(lbl_lat1)
entry_lat1 = QLineEdit()
layout.addWidget(entry_lat1)

lbl_lon1 = QLabel("Source Longitude:")
layout.addWidget(lbl_lon1)
entry_lon1 = QLineEdit()
layout.addWidget(entry_lon1)

lbl_lat2 = QLabel("Destination Latitude:")
layout.addWidget(lbl_lat2)
entry_lat2 = QLineEdit()
layout.addWidget(entry_lat2)

lbl_lon2 = QLabel("Destination Longitude:")
layout.addWidget(lbl_lon2)
entry_lon2 = QLineEdit()
layout.addWidget(entry_lon2)

# Button to calculate shortest path
btn_run = QPushButton("Get Shortest Path")
btn_run.clicked.connect(calculate_shortest_path)
layout.addWidget(btn_run)

# Create a widget to hold the layout
widget = QWidget()
widget.setLayout(layout)
window.setCentralWidget(widget)

# Display the main application window
window.show()

# Run the application
sys.exit(app.exec_())

