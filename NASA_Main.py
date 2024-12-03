import OOP_NASA_place_Display
import OOP_NASA_coordinate_Display

print("Get Satellit Surface Reflectance Data")
option = str(input("Location Name or Location Coordinates = "))
if option == "location name":
    downloader = OOP_NASA_place_Display.LocationLandsat()
    downloader.run()
else:
    downloader = OOP_NASA_coordinate_Display.CoordinateLandsat()
    downloader.run()

print("thank you for using")