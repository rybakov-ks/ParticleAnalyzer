## 📑 Table of Contents

1. 🔎 [ParticleAnalyzer](#particleanalyzer)
2. ✨ [Key Features](#-key-features)
3. 📥 [Installation Guide](#-installation-guide)
4. 🛠 [Segmentation Optimization Guide](#-segmentation-optimization-guide)
5. 📊 [Analysis Outputs](#-analysis-outputs)
6. ⚙️ [Advanced Settings](#-advanced-settings)
7. 📏 [Scale Calibration](#-scale-calibration)
8. 📧 [Contributors](#-contributors)

## ParticleAnalyzer
[![Try Online](https://img.shields.io/badge/TRY%20ONLINE-Available%20at%20sem.rybakov--k.ru-brightgreen)](https://sem.rybakov-k.ru/)
[![Download from PyPI](https://img.shields.io/pypi/v/particleanalyzer?label=Download%20from%20PyPI)](https://pypi.org/project/particleanalyzer/)
[![Downloads per month](https://static.pepy.tech/badge/particleanalyzer/month)](https://pepy.tech/project/particleanalyzer)

A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images.
<p align="center">
  <strong>Video demonstrations:</strong><br>
  <a href="Images/ParticleAnalyzer.mp4">Local video (MP4)</a> | 
  <a href="https://youtu.be/qlCuZDjDyqk">YouTube demonstration</a>
</p>

<div align="center">
  <img src="Images/example.gif" alt="Example">
</div>

*If you encounter any errors while using Particle Analyzer, please open an issue in the GitHub repository or contact me at rybakov-ks@ya.ru for support.
If the model cannot segment your images correctly, please send them to rybakov-ks@ya.ru . Your images will be used to retrain the model's.*
## ✨ Key Features
- Automated particle segmentation in SEM images
- SAHI mode enables accurate detection of small particles in high-resolution images via a sliding window method
- Comprehensive statistical analysis of particle characteristics
- Interactive visualization of size distributions
- Dual unit support — switch between pixels and micrometers (µm)
- Supports multiple AI models: YOLOv11, YOLOv12, and Detectron2
- Advanced configuration options for fine-tuning detection accuracy
- AI Interpretation of SEM Data
- Multi-language interface: Russian, Simplified Chinese, Traditional Chinese, English (ru, zh-CN, zh-TW, en)
- Try it online: [sem.rybakov-k.ru](https://sem.rybakov-k.ru/)

## 🛠 Installation Guide

 ### 1. 📥 Install PyTorch with CUDA support
Make sure your system has an NVIDIA GPU with CUDA. Install [PyTorch](https://pytorch.org/get-started/locally/) using the appropriate CUDA version (e.g., CUDA 11.8):
   ```python
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
If you do not have a CUDA-capable GPU, use the CPU version instead:
   ```python
   pip install torch torchvision torchaudio
   ```
### 🧪 2. Install Detectron2 (Optional)

If you want to enable advanced instance segmentation, install Detectron2:
```python
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
⚠️ *There may be problems installing Detectron2. Use the official [documentation](https://detectron2.readthedocs.io/en/latest/tutorials/install.html).*
### 📦 3. Install ParticleAnalyzer
Finally, install ParticleAnalyzer from PyPI:
```python
pip install ParticleAnalyzer
```
✅ Now you're ready to run the application:
```python
ParticleAnalyzer run
```
Open in browser: http://127.0.0.1:8000 

You can specify the port if necessary:
```python
ParticleAnalyzer run --port 5000
```

Launch with LLM support ([OpenRouter](https://openrouter.ai/settings/keys) API key required):
```python
ParticleAnalyzer run --port 5000 --api-key YOUR_OPENROUTER_API_KEY
```

## 🛠 Segmentation Optimization Guide
🔧 Core Parameters:
   - Model Selection
   - Detection Confidence Threshold (0-1)
     - Increase (e.g., 0.7→0.85) to reduce false positives
     - Decrease (e.g., 0.5→0.3) to detect faint particles
   - IoU Threshold (0-1)
     - Increase (e.g., 0.5→0.7) to eliminate duplicate detections
     - Decrease for dense particle fields
   - Enable SAHI Processing (split-analyze-merge)

🧩 SAHI Configuration (for large images):
   - Slice Size: Start with 400×400
   - Overlap Ratio: 0.2-0.3 (prevents edge artifacts)\
*SAHI mode helps detect small objects in high-resolution images by using a sliding window approach*

🔄 Model Selection:
<div align="center">
   
| Model       | Best For                   | Speed     | Recommended Use Case               |
|-------------|----------------------------|-----------|------------------------------------|
| **YOLOv11** | General use (balanced)      | ⚡⚡⚡ Fast | Quick analysis of standard samples |
| **YOLOv12** | High precision detection    | ⚡⚡ Medium | Critical measurements              |
| **Cascade_X152** | Challenging morphology   | ⚡ Slow    | Irregular/overlapping particles    |

</div>

## 📊 Analysis Outputs

### Statistical Data Table
<div align="center">
  <img src="Images/2.png" alt="Statistics Table">
</div>

*Comprehensive metrics including mean, median, min/max, standard deviation values for:*
<div align="center">
  <img src="Images/8.png" alt="Statistics Table">
</div>

- Area (px² or µm²)
- Perimeter (px or µm)
- Equivalent diameter (px or µm)
- Feret diameters and angles (px or µm and °)
- Eccentricity (unitless)
- Intensity values (grayscale units)

**AI Interpretation of SEM Data**
<div align="center">
  <img src="Images/9.png" alt="Statistics Table">
</div>

### Size Distribution Visualization
<div align="center">
  <img src="Images/3.png" alt="Distribution Plots">
</div>

*Normal distribution fitting for all measured parameters showing particle population characteristics*

## Advanced Settings Panel
<div align="center">
  <img src="Images/4.png" alt="Settings Menu">
</div>

*Configuration options include:*
- **Model Selection**: YOLOv11, YOLOv12, Detectron2
- **SAHI Mode**: Enable/disable sliced inference for large images
<div align="center">
  <img src="Images/6.gif" alt="SAHI Mode">
</div>

- **Detection Threshold**: Confidence level (0-1)
- **IOU Threshold**: Overlap threshold for NMS (0-1)
- **Max Detections**: Maximum number of particles to detect
- **Scaling Mode**: Pixel/µm unit selection
- **Image Resolution**: Output resolution control
- **Result Rounding**: Decimal places for metrics
- **Single Particle Mode**: Detailed individual analysis
- **Histogram Bins**: Number of intervals for distribution plots

## 📐 Scale Calibration
<div align="center">
  <img src="Images/5.png" alt="Scale Calibration">
</div>

Micrometer values are calculated by:
1. Identifying the SEM image's scale bar using two marker points
2. Manually specifying the known real-world distance between markers
3. Automatically computing the pixel-to-µm conversion ratio
<div align="center">
  <img src="Images/7.png" alt="Real Scale">
</div>

*Note: For accurate µm measurements, please ensure:*
- The scale bar is clearly visible in your image
- Enter the correct scale
- The scale bar was created at the same magnification as your particles

## 📧 Contributors
Rybakov Kirill (Saratov State University): rybakov-ks@ya.ru
