from setuptools import setup, find_packages
import os


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="ParticleAnalyzer",
    version="1.3.2",
    packages=find_packages(exclude=["tests*"]),
    package_data={
        "particleanalyzer": [
            "assets/**/*",
            "core/*",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ParticleAnalyzer=particleanalyzer.cli:main",
        ],
    },
    install_requires=[
        "gradio==5.47.0",
        "gradio-rangeslider",
        "matplotlib",
        "opencv-python",
        "opencv-python-headless",
        "Pillow",
        "plotly",
        "sahi",
        "scipy",
        "tqdm",
        "ultralytics",
        "huggingface_hub",
        "openai",
        "Requests",
        "numpy",
        "pandas",
        "supervision",
    ],
    python_requires=">=3.10",
    author="Kirill Rybakov",
    author_email="rybakov-ks@ya.ru",
    description="ParticleAnalyzer is a computer vision tool for automatic particle segmentation and size analysis in Scanning Electron Microscope (SEM) images.",
    long_description=read_file("README_PYPI.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/rybakov-ks/ParticleAnalyzer",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "SEM",
        "TEM",
        "microscopy",
        "image-analysis",
        "particle-analysis",
        "materials-science",
        "nanoparticles",
        "computer-vision",
        "opencv",
        "python",
        "scientific-computing",
        "microstructure",
        "particle-size",
        "image-processing",
        "detectron2",
        "YOLO",
        "deep-learning",
        "microscope-images",
        "material-characterization",
        "automated-measurements",
        "research-tools",
        "onnxruntime",
    ],
    project_urls={
        "Bug Reports": "https://github.com/rybakov-ks/ParticleAnalyzer/issues",
        "Source": "https://github.com/rybakov-ks/ParticleAnalyzer",
    },
)
