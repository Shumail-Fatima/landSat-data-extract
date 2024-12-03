import ee
ee.Authenticate()
ee.Initialize(project='ee-shumailarshadubit')
import geemap
import pandas as pd
import matplotlib.pyplot as plt
import os
import webbrowser

class CoordinateLandsat:
    def __init__(self, project_id="ee-shumailarshadubit"):
        ee.Initialize(project=project_id)
        self.maps = geemap.Map()

    def get_target_coordinates(self):
        target_lat = float(input("give Target Latitude = "))
        target_lon = float(input("give Target Longitude = "))
        self.latitude = target_lat
        self.longitude = target_lon
        self.target_point = ee.Geometry.Point(self.longitude, self.latitude)

    def load_landsat_info(self):
        self.collection = ee.ImageCollection("LANDSAT/LC08/C02/T1")

    def find_most_recent_landsat_image(self):
        start_date = str(input("Enter your Starting date for data capture (YYYY-MM-DD): "))
        end_date = str(input("Enter your Ending date for data capture (YYYY-MM-DD): "))

        # Define WRS2 geometry based on target coordinates (adjust size as needed)
        self.wrs2_geometry = ee.Geometry.Polygon([[
            [self.longitude - 0.1677, self.latitude - 0.2617],
            [self.longitude - 0.1677, self.latitude + 0.2264],
            [self.longitude + 0.3323, self.latitude + 0.2264],
            [self.longitude + 0.3323, self.latitude - 0.2617],
        ]])

        filtered_collection = self.collection.filterBounds(self.wrs2_geometry) \
            .filterDate(start_date, end_date) \
            .filterMetadata("CLOUD_COVER", "less_than", 10)

        self.most_recent_landsat = filtered_collection.sort("system:time_start", False).first()

    def get_landsat_metadata(self):
        landsat_props = geemap.image_props(self.most_recent_landsat)

        lst = ["Sensor ID", "Spacecraft ID", "Station ID", "Target WRS path",
               "Target WRS row", "WRS path", "WRS row",
               "Image date", "Cloud Cover", "Cloud Cover Land",
               "Image Quality OLI", "Image Quality TIRS"]

        prp_lst = ["SENSOR_ID", "SPACECRAFT_ID", "STATION_ID",
                   "TARGET_WRS_PATH", "TARGET_WRS_ROW", "WRS_PATH", "WRS_ROW",
                   "IMAGE_DATE", "CLOUD_COVER", "CLOUD_COVER_LAND",
                   "IMAGE_QUALITY_OLI", "IMAGE_QUALITY_TIRS"]

        self.prop_dict = {}
        #self.prop_dict["Location name"] = input("Enter location name: ")
        #self.prop_dict["Location name"] = self.loc
        self.prop_dict["Latitude"] = self.latitude
        self.prop_dict["Longitude"] = self.longitude

        for i in range(len(lst)):
            self.prop_dict[lst[i]] = landsat_props.get(prp_lst[i]).getInfo()

        for key, value in self.prop_dict.items():
            print(f"{key}: {value}")

    def download_metadata_to_csv(self):
        get_csv = str(input("Do you want to download the metadata (yes/no)? "))
        if get_csv.lower() == "yes":
            # Use pandas' to_csv method with index=False for cleaner output
            (pd.DataFrame.from_dict(data=self.prop_dict, orient='index').to_csv('dict_file.csv', header=False))
        else:
            print("Thank you!")

    def create_display_map(self):
        self.maps.centerObject(self.target_point, zoom=10)  # Center the map on the target point

        rgbVis = {'bands':["B4","B3","B2"], min:0, max:0.3}

        # Add the image to the map
        self.maps.addLayer(self.most_recent_landsat, rgbVis, 'Most Recent Landsat Image')

        self.maps.addLayer(self.wrs2_geometry, {'color': 'red', 'opacity': 0.5}, 'Landsat Scene Extent')

        self.maps.addLayer(self.target_point, {'color': 'blue'}, 'Target Point')

        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        html_file = os.path.join(download_dir, "my_map.html")
        self.maps.to_html(filename=html_file, title="My Map", width="100%", height="880px")
        webbrowser.open(html_file)

        # Display the map
        #self.maps.centerObject(self.target_point, zoom=10)  # Center the map on the target point

    def get_landsat_stats(self):
        landsat_stats = geemap.image_stats(self.most_recent_landsat, scale=90)
        self.stats_dict = landsat_stats.getInfo()
        #print(self.stats_dict)

    def plot_spectral_signature(self):
        # Extract mean values from stats_dict
        #mean_values = [self.stats_dict["mean"][band] for band in range(1, 9)]  # Assuming 8 bands

        def display_inner_keys(nested_dict, outer_key):
            for key, value in nested_dict.items():
                if key == outer_key and isinstance(value, dict):
                    for inner_key in value.keys():
                        lst_keys.append(inner_key)
                elif isinstance(value, dict):
                    display_inner_keys(value, outer_key)  # Recursively process nested dictionaries

        def display_inner_values(nested_dict, outer_key):
            for key, value in nested_dict.items():
                if key == outer_key and isinstance(value, dict):
                    for inner_value in value.values():
                        lst_vals.append(inner_value)
                elif isinstance(value, dict):
                    display_inner_values(value, outer_key)  # Recursively process nested dictionaries


        lst_keys = []
        display_inner_keys(self.stats_dict, "mean")

        lst_vals = []
        display_inner_values(self.stats_dict, "mean")

        res = dict(zip(lst_keys, lst_vals))

        plt.plot(res.values())
        plt.title('Spectral Signature')
        plt.xlabel('Band Number')
        plt.ylabel('Pixel Value')
        plt.grid(True)  # Add grid for better readability
        plt.show()

    def run(self):
        try:
            self.get_target_coordinates()
            self.load_landsat_info()
            self.find_most_recent_landsat_image()
            self.get_landsat_metadata()
            self.download_metadata_to_csv()
            self.create_display_map()
            self.get_landsat_stats()
            self.plot_spectral_signature()
        except Exception as e:
            print(f"An error occurred: {e}")

# Create an instance of the LandsatDownloader class and run it
#downloader = CoordinateLandsat()
#downloader.run()