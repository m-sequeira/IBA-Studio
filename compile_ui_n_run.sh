#!/bin/bash

pyuic5 -o main_window_ui.py ui/geo_load.ui; 
pyuic5 -o about_window_ui.py ui/about_window.ui; 
pyuic5 -o ndf_spectra_fit_ui.py ui/ndf_spectra_fit.ui; 
pyuic5 -o reactions_ui.py ui/reactions.ui; 
pyuic5 -o NDF_run_ui.py ui/NDF_run.ui;
pyuic5 -o ndf_more_options_ui.py ui/ndf_more_options.ui;
python3 NDF_gui.py
