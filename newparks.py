# POTA Unactivated Park Finder (aka newparks.py)
# By Ian Renton, November 2024
# Queries the Parks on the Air API to find all parks that have never been activated, and produces a KML file.
# See the README.md file for more details.
# This is Public Domain software, see the LICENCE file

from requests_cache import CachedSession
from datetime import timedelta
import simplekml

# Create KML object to fill with unactivated parks
kml = simplekml.Kml()

# Fetch list of programs
session = CachedSession("newparks_cache", expire_after=timedelta(days=1))
programs = session.get("https://api.pota.app/programs").json()
print("Found " + str(len(programs)) + " POTA programs")

# For each program, fetch a list of parks
for program in programs:
    prefix = program["programPrefix"]
    parks = session.get("https://api.pota.app/program/parks/" + prefix).json()
    print("Found " + str(len(parks)) + " parks in " + prefix)

    # For each park, if it's not activated, store its details in the KML
    for park in parks:
        if park["activations"] == 0:
            kml.newpoint(name=park["reference"] + " " + park["name"],
                         description="https://pota.app/#/park/" + park["reference"],
                         coords=[(park["longitude"], park["latitude"])])

# Save KML
print("Writing to newparks.kml...")
kml.save("newparks.kml")
print("Done.")