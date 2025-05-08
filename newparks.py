# POTA Unactivated Park Finder (aka newparks.py)
# By Ian Renton, November 2024
# Queries the Parks on the Air API to find all parks that have never been activated, and produces a KML file.
# See the README.md file for more details.
# This is Public Domain software, see the LICENCE file

import sys
from requests_cache import CachedSession
from datetime import timedelta
import simplekml

# Ensure user provided a prefix
if len(sys.argv) != 2:
    print("Usage: python newparks.py <programPrefix>")
    sys.exit(1)

input_prefix = sys.argv[1].upper()

# Create KML object to fill with unactivated parks
kml = simplekml.Kml()

# Fetch list of programs
session = CachedSession("newparks_cache", expire_after=timedelta(days=1))
programs = session.get("https://api.pota.app/programs").json()

# Validate the input prefix
valid_prefixes = {program["programPrefix"]: program for program in programs}
if input_prefix not in valid_prefixes:
    print(f"Invalid programPrefix '{input_prefix}'. Valid options are: {', '.join(valid_prefixes.keys())}")
    sys.exit(1)

print(f"Fetching parks for program prefix: {input_prefix}")

# Fetch parks for the specified prefix
parks = session.get(f"https://api.pota.app/program/parks/{input_prefix}").json()
print(f"Found {len(parks)} parks in {input_prefix}")

# Add unactivated parks to KML
for park in parks:
    if park["activations"] == 0:
        kml.newpoint(name=f'{park["reference"]} {park["name"]}',
                     description=f'https://pota.app/#/park/{park["reference"]}',
                     coords=[(park["longitude"], park["latitude"])])

# Save KML
filename = f"newparks-{input_prefix}.kml"
print(f"Writing to {filename}...")
kml.save(filename)
print("Done.")
