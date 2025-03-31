import requests
import json
import geopandas as gpd

def run_overpass_query():
    """
    Fetch nature reserves from OpenStreetMap using Overpass API.
    """
    query = """
    [out:json][timeout:180];
    way["leisure"="nature_reserve"]
    (-35.0, -25.0, 40.0, 55.0);  # Corrected bounding box for Africa
    >;
    out geom;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})

    if response.status_code == 200:
        data = response.json()
        geojson = convert_to_geojson(data)

        filename = "nature_reserves.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=4)

        print(f"GeoJSON saved as {filename}")
    else:
        print(f"Error: {response.status_code}", response.text)

def convert_to_geojson(data):
    """
    Convert Overpass API response data to GeoJSON format.
    """
    geojson = {"type": "FeatureCollection", "features": []}

    for element in data.get("elements", []):
        feature = {"type": "Feature", "properties": {}, "geometry": None}
        
        # Include only OSM tags
        feature["properties"].update(element.get("tags", {}))
        feature["properties"]["id"] = element.get("id", "")

        if "geometry" in element:
            coords = [[node["lon"], node["lat"]] for node in element["geometry"]]
            
            if element["type"] == "way" and coords[0] == coords[-1]:  # Closed polygon
                feature["geometry"] = {"type": "Polygon", "coordinates": [coords]}
            else:
                continue  # Skip non-polygonal ways
        
        if feature["geometry"]:
            geojson["features"].append(feature)

    return geojson

def clip_parks():
    """
    Load the generated GeoJSON file and clip it using the Africa boundary shapefile.
    """
    africa_boundary = gpd.read_file(r"C:\Users\yashk\Downloads\africannationalparks\Africa_Adm0_Country\Africa_Adm0_Country.shp")
    national_parks = gpd.read_file("nature_reserves.geojson")

    # Ensure CRS match
    africa_boundary = africa_boundary.to_crs(national_parks.crs)

    clipped_parks = gpd.clip(national_parks, africa_boundary)
    clipped_parks.to_file(r"C:\Users\yashk\Downloads\africanationalparks\clipped_parks2.geojson", driver="GeoJSON")

    print("Clipped parks saved as GeoJSON.")

if __name__ == "__main__":
    run_overpass_query()  # Fetch and save nature reserves
    clip_parks()  # Clip the parks using the Africa boundary
