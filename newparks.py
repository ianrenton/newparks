# POTA Unactivated Park Finder (aka newparks.py)
# By Ian Renton, November 2024
# Queries the Parks on the Air API to find all parks that have never been activated, and produces a KML file.
# See the README.md file for more details.
# This is Public Domain software, see the LICENCE file

import sys
from requests_cache import CachedSession
from datetime import timedelta
import simplekml

# Setup cache and KML
session = CachedSession("newparks_cache", expire_after=timedelta(days=1))
kml = simplekml.Kml()

# Fetch list of programs
programs = session.get("https://api.pota.app/programs").json()
valid_prefixes = {program["programPrefix"]: program for program in programs}

# Check command-line arguments
args = sys.argv[1:]

# Option to list all valid prefixes
if args and args[0] == "--list":
    print("Valid program prefixes:")
    for prefix in sorted(valid_prefixes.keys()):
        print(f"  {prefix}")
    sys.exit(0)

# Function to add unactivated parks for a prefix
def add_unactivated_parks(prefix):
    parks = session.get(f"https://api.pota.app/program/parks/{prefix}").json()
    print(f"Found {len(parks)} parks in {prefix}")
    for park in parks:
        if park["activations"] == 0:
            kml.newpoint(name=f'{park["reference"]} {park["name"]}',
                         description=f'https://pota.app/#/park/{park["reference"]}',
                         coords=[(park["longitude"], park["latitude"])])

# If a specific prefix is provided
if args:
    prefix = args[0].upper()
    if prefix not in valid_prefixes:
        print(f"Invalid programPrefix '{prefix}'. Use --list to see valid options.")
        sys.exit(1)
    print(f"Fetching parks for program prefix: {prefix}")
    add_unactivated_parks(prefix)
    filename = f"newparks-{prefix}.kml"
else:
    print("No prefix provided. Fetching parks for all programs...")
    for prefix in valid_prefixes:
        add_unactivated_parks(prefix)
    filename = "newparks.kml"

# Save KML file
print(f"Writing to {filename}...")
kml.save(filename)
print("Done.")
