
# Import necessary libraries  
import requests  # For making HTTP requests to the API  
import json      # For handling JSON data format  

def run_overpass_query():  
    # Define the Overpass API query  
    query = """  
    [out:json][timeout:180];  # Set output format to JSON and timeout to 180 seconds  
    way["leisure"="nature_reserve"](-36.17335693522159,-19.509008284679254,38.47939467327645,52.03396046532075);  # Query for nature reserves within a bounding box  
    (._;>;);  # Get all nodes associated with the ways  
    out geom;  # Output the geometry of the features  
    """  

    # Define the Overpass API URL   
    url = "https://overpass-api.de/api/interpreter"  
    # Send the GET request to the API with the defined query  
    response = requests.get(url, params={"data": query})  

    # Check if the request was successful (status code 200)  
    if response.status_code == 200:  
        # Parse the JSON response from the API  
        data = response.json()  
        # Convert the raw data to GeoJSON format  
        geojson = convert_to_geojson(data)  
        # Define the filename for saving the GeoJSON data  
        filename = "nature_reserves.geojson"  
        # Open the file in write mode to save the GeoJSON  
        with open(filename, "w") as f:  
            # Write the GeoJSON data to the file  
            json.dump(geojson, f, indent=4)  
        # Print success message  
        print(f"GeoJSON saved as {filename}")  
    else:  
        # Print error message if the request failed  
        print(f"Error: {response.status_code}", response.text)  

def convert_to_geojson(data):  
    # Initialize GeoJSON structure  
    geojson = {  
        "type": "FeatureCollection",  
        "features": []  
    }  
    
    # List of required properties that we want to initialize  
    required_properties = [  
        "Year of Visitor-Counting", "PH", "Soil Type", "Cash Crop", "Rainfall Average", "Temperature Average",   
        "Biome type", "Endangered species Fauna", "Endangered species flora", "Wetlands", "Highest peak",   
        "Water table", "Greenhouse index", "CO2 emissions index", "ISO1", "ISO2", "ISO3", "ISO4", "ISO5",   
        "OSM1", "OSM2", "OSM3", "OSM4567"  
    ]  

    # Loop through each element in the response data  
    for element in data.get("elements", []):  
        # Initialize a feature for GeoJSON  
        feature = {  
            "type": "Feature",  
            "properties": {prop: " " for prop in required_properties},  # Initialize properties with empty string  
            "geometry": None  # Start with no geometry  
        }  
        
        # Update properties with existing OpenStreetMap tags  
        feature["properties"].update({key: f'"{value}"' for key, value in element.get("tags", {}).items()})  
        feature["properties"]["id"] = f'"{element.get("id", "")}"'  # Add the unique ID of the feature  
        
        # Check if the element has geometry  
        if "geometry" in element:  
            # Extract longitude and latitude for each node in the geometry  
            coords = [[node["lon"], node["lat"]] for node in element["geometry"]]  

            # Check if it’s a closed way (first and last coordinates are the same) to consider it a Polygon  
            if element["type"] == "way" and coords[0] == coords[-1]:  
                # Assign the geometry as a Polygon  
                feature["geometry"] = {"type": "Polygon", "coordinates": [coords]}  
            else:  
                continue  # Skip if it's not a polygon  

        # If geometry is valid, add the feature to GeoJSON  
        if feature["geometry"]:  
            geojson["features"].append(feature)  

    # Return the constructed GeoJSON  
    return geojson  

# Run the query if the script is executed directly  
if __name__ == "__main__":  
    run_overpass_query()