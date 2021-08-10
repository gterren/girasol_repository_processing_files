# Girasol Repository Processing Files

This repository contains the files needed to process the data in the Girasol Machine and upload it to the Girasol Dataset repository in DRYAD: https://doi.org/10.5061/dryad.zcrjdfn9m.

For more information about the Girasol Machine and the Girasol Dataset see article https://www.sciencedirect.com/science/article/pii/S2352340921001980.

## Workflow

If there was not errors during the adquisition of the infrared images, these are saved in the repository directory with the date /yyyy_mm_dd as name in a folder called /ir_camera using file copy_infrared_files.py.

If there was not errors during the adquisition of the fisheye visible light images, these are saved in the repository directory with the date /yyyy_mm_dd as name in a folder called /vi_camera using file copy_visible_files.py.

The sun_position.csv that contains elevation and azimuth angle of the solar tracker updated every seconds are interpolated to the sampling interval of the pyranometer in pyranometer.csv copy_csv_files.py.

The weather features in weather_station.csv are interpolated to the resolution pyranometer samples in pyranometer.csv, and save in a folder called /weather_station in the repository directory with the date /yyyy_mm_dd using copy_weather_station_files.py.

The file remove_images.py removes begging and ending infrared and visible image that have not pyranometer a sample.

## Pickle Files

The repository files are updated and transformed to python readable single pickle files that contain all the data of a day. The file to perform this action is pickle_files.py.
