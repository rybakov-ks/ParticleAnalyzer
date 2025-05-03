# ParticleAnalyzer

A Computer Vision-based tool for automatic segmentation and size analysis of particles in SEM (Scanning Electron Microscope) images.

[![Try Online](https://img.shields.io/badge/TRY%20ONLINE-Available%20at%20sem.rybakov--k.ru-brightgreen)](https://sem.rybakov-k.ru/)
![Demo](Images/1.png)

## Key Features
- Automated particle segmentation in SEM images
- Comprehensive statistical analysis of particle characteristics
- Interactive visualization of size distributions
- Web-based interface for easy accessibility
- **Dual-unit display**: toggle between pixels and micrometers (µm)
- **Online version** available at [sem.rybakov-k.ru](https://sem.rybakov-k.ru/)

## Analysis Outputs

### Statistical Data Table
![Statistics Table](Images/2.png)\
*Comprehensive metrics including mean, median, min/max, standard deviation values for:*
- Area (px² or µm²)
- Perimeter (px or µm)
- Equivalent diameter (px or µm)
- Eccentricity (unitless)
- Intensity values (grayscale units)

### Size Distribution Visualization
![Distribution Plots](Images/3.png)\
*Normal distribution fitting for all measured parameters showing particle population characteristics*

## Scale Calibration
Micrometer values are calculated by:
1. Identifying the SEM image's scale bar using two marker points
2. Manually specifying the known real-world distance between markers
3. Automatically computing the pixel-to-µm conversion ratio

*Note: For accurate µm measurements, please ensure:*
- The scale bar is clearly visible in your image
- You input the correct reference distance when prompted
- The scale bar was created at the same magnification as your particles

