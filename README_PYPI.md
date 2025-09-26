# ParticleAnalyzer

[![LIVE Application](https://img.shields.io/badge/LIVE-Application%20at%20particleanalyzer.ru-brightgreen)](https://particleanalyzer.ru/)
[![Slow Demo?](https://img.shields.io/badge/Telegram-Try%20Mini%20App-blue)](https://t.me/particleanalyzer_bot)
[![PyPI Version](https://img.shields.io/pypi/v/particleanalyzer?label=PyPI)](https://pypi.org/project/particleanalyzer/)
[![Monthly Downloads](https://static.pepy.tech/badge/particleanalyzer/month)](https://pepy.tech/project/particleanalyzer)


<div align="left">
  <a href="https://sem.rybakov-k.ru/">
    <img src="https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/refs/heads/main/Images/Logo.png" alt="ParticleAnalyzer Logo" width="300"/>
  </a>
</div>

**ParticleAnalyzer** Is A Computer Vision-Based Tool for Automatic Segmentation and Size Analysis of Nanoparticles in Scanning Electron Microscope (SEM) and Transmission Electron Microscope (TEM) Images.

---

## 🎬 Demonstration

<p align="center">
  <strong>Video demonstrations:</strong><br>
  <a href="https://github.com/rybakov-ks/ParticleAnalyzer/blob/main/Images/ParticleAnalyzer.mp4">▶️ Local video (MP4)</a> | 
  <a href="https://youtu.be/qlCuZDjDyqk">▶️ YouTube demonstration</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/Images/example.gif" alt="Example" width="600">
</p>

---

## 🛠 Installation Guide

 ### 1. 📥 Install PyTorch with CUDA support
Make sure your system has an NVIDIA GPU with CUDA. Install [PyTorch](https://pytorch.org/get-started/locally/) using the appropriate CUDA version (e.g., CUDA 11.8):
   ```python
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
If you do not have a CUDA-capable GPU, use the CPU version instead—however, in this case, ParticleAnalyzer will run significantly slower:
   ```python
   pip install torch torchvision torchaudio
   ```
### 🧪 2. Install Detectron2 (Optional)

If you want to enable advanced instance segmentation, install Detectron2:
```python
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
> [!WARNING]
> *There may be problems installing Detectron2. Use the official [documentation](https://detectron2.readthedocs.io/en/latest/tutorials/install.html).*
### 📦 3. Install ParticleAnalyzer
Finally, install ParticleAnalyzer from PyPI:
```python
pip install --upgrade ParticleAnalyzer
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

Launch with LLM support ([OpenRouter](https://openrouter.ai/settings/keys) or [Hugging Face](https://huggingface.co/settings/tokens) API key required):
```python
ParticleAnalyzer run --port 5000 --api-key YOUR_OPENROUTER_API_KEY
```
