#!/bin/bash

pyuic5 -o ui/main_window_ui.py ui/geo_load.ui; 
pyuic5 -o ui/about_window_ui.py ui/about_window.ui; 
pyuic5 -o ui/ndf_spectra_fit_ui.py ui/ndf_spectra_fit.ui; 
pyuic5 -o ui/reactions_ui.py ui/reactions.ui; 
pyuic5 -o ui/NDF_run_ui.py ui/NDF_run.ui;
pyuic5 -o ui/ndf_more_options_ui.py ui/ndf_more_options.ui;

# Replace paths in the generated Python files
sed -i 's|ui/../logos/|logos/|g' ui/main_window_ui.py
sed -i 's|ui/../logos/|logos/|g' ui/about_window_ui.py
sed -i 's|ui/../logos/|logos/|g' ui/ndf_spectra_fit_ui.py
sed -i 's|ui/../logos/|logos/|g' ui/reactions_ui.py
sed -i 's|ui/../logos/|logos/|g' ui/NDF_run_ui.py
sed -i 's|ui/../logos/|logos/|g' ui/ndf_more_options_ui.py

python3 iba_studio.py

