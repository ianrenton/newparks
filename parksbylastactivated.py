# POTA Parks by Last Activated Date (parksbylastactivated.py)
# By Ian Renton, December 2024
# Queries the Parks on the Air API to get all parks, and produces a KML file where the marker colour is set by the last
# activated date.
# See the README.md file for more details.
# This is Public Domain software, see the LICENCE file

from requests_cache import CachedSession
from datetime import timedelta, datetime
import matplotlib as mpl
import simplekml
import sys
import maidenhead as mh

# Parse command-line arguments
if len(sys.argv) != 2:
    print("The script must be run with a command-line argument for your Maidenhead grid reference.")
    sys.exit()
lat, lon = mh.to_location(sys.argv[1])

# Fetch list of parks
session = CachedSession("parksbylastactivated_cache", expire_after=timedelta(days=1))
parks = session.get(
        "https://api.pota.app/park/grids/" + str(lat - 1.0) + "/" + str(lon - 1.0) + "/" + str(lat + 1.0) + "/" + str(
            lon + 1.0) + "/0").json()["features"]

# For each one, perform another request to determine their most recent activation date
for park in parks:
    print("Looking up " + park["properties"]["reference"] + "...")
    last_activation_data = session.get("https://api.pota.app/park/activations/" + park["properties"]["reference"] + "?count=1")
    # If never activated, mark the last activation as UNIX time zero
    if not last_activation_data.json():
        park["properties"]["last_activation_time"] = 0
    else:
        park["properties"]["last_activation_time"] = datetime.strptime(last_activation_data.json()[0]["qso_date"], "%Y%m%d").timestamp()

# Find the oldest "last activated" date, so we know how to scale the colours
oldest = datetime.now().timestamp()
for park in parks:
    if 0 < park["properties"]["last_activation_time"] < oldest:
        oldest = park["properties"]["last_activation_time"]

# Set up a colour mapping. To provide a good contrast, three years ago is mapped to red, and today to green.
latest = datetime.now().timestamp()
three_years_ago = (datetime.now() - timedelta(days=3*365)).timestamp()
color_map = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=three_years_ago, vmax=latest), cmap=mpl.colormaps.get_cmap("RdYlGn"))

# Create KML object to fill with parks
kml = simplekml.Kml()

# For each park, store its details in the KML, applying the colour to the marker.
# KML hex color format is AABBGGRR
for park in parks:
    color_hex = "ff000000"
    if park["properties"]["last_activation_time"] > 0:
        tmp_color_hex = mpl.colors.rgb2hex(color_map.to_rgba(park["properties"]["last_activation_time"])).replace("#", "", 1)
        color_hex = "ff" + tmp_color_hex[4:6] + tmp_color_hex[2:4] + tmp_color_hex[0:2]

    friendly_activated_time = "Never activated"
    if park["properties"]["last_activation_time"] > 0:
        friendly_activated_time = "Last activated " + datetime.fromtimestamp(park["properties"]["last_activation_time"]).strftime("%d %B %Y")

    pnt = kml.newpoint(name=park["properties"]["reference"],
                 description=park["properties"]["name"] + "<br/>https://pota.app/#/park/" + park["properties"]["reference"] + "<br/>" + friendly_activated_time,
                 coords=[(park["geometry"]["coordinates"][0], park["geometry"]["coordinates"][1])])
    pnt.style.iconstyle.color = color_hex

# Save KML
print("Writing to parksbylastactivated.kml...")
kml.save("parksbylastactivated.kml")
print("Done.")