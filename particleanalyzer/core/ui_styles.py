from particleanalyzer.core.tour import tour

# CSS для стилизации интерфейса
css = """
#app-container {
    max-width: 750px;
    margin: 0 auto;
}
footer { display: none !important; }
#author-note {
    text-align: right;
    font-size: 14px;
}
#dataframe-table {
    width: 100%;
    table-layout: auto;
}
#dataframe-table th, #dataframe-table td {
    white-space: nowrap;
}
#dataframe-table2 {
    width: 100%;
    table-layout: auto;
}
#dataframe-table2 th, #dataframe-table2 td {
    white-space: nowrap;
}
#gr-head {
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
}
#gr-head > div {
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
}
.btn-group {
    gap: 20px !important;
}
.custom-cancel-btn {
    background: #5E936C !important;
}
.custom-cancel-btn:hover {
    background: #3E5F44 !important;
}
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #3b71ca;
}

input:checked + .slider:before {
  transform: translateX(26px);
}
"""

custom_head = (
    """
<!-- HTML Meta Tags -->
<title>ParticleAnalyzer — SEM Image Analysis Tool</title>
<meta name="description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images.">

<!-- Facebook Meta Tags -->
<meta property="og:url" content="https://sem.rybakov-k.ru/">
<meta property="og:type" content="website">
<meta property="og:title" content="ParticleAnalyzer">
<meta property="og:description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images.">
<meta property="og:image" content="https://rybakov-k.ru/images/ex.png">

<!-- Twitter Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:creator" content="@rybakov_ks">
<meta name="twitter:title" content="ParticleAnalyzer">
<meta name="twitter:description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images.">
<meta name="twitter:image" content="https://rybakov-k.ru/images/ex.png">
<meta property="twitter:domain" content="sem.rybakov-k.ru">
<meta property="twitter:url" content="https://sem.rybakov-k.ru/">

<!-- Meta Tags Generated via https://www.opengraph.xyz/ -->

<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/intro.js@7.0.1/minified/introjs.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/intro.js@7.0.1/minified/intro.min.js"></script>
"""
    + tour
    + """
<style>
.custom-introjs-tooltip {
  min-width: 300px;
  max-width: 400px;
  border-radius: 8px;
  color: #000000 !important;
}

.custom-introjs-tooltip * {
  color: #000000 !important;
}

.introjs-progress {
  background-color: #e0e0e0;
  height: 4px;
}

.introjs-progressbar {
  background-color: #4CAF50;
}

.custom-introjs-tooltip .introjs-tooltip-title {
  color: #000000 !important;
}

.custom-introjs-tooltip .introjs-tooltiptext {
  color: #000000 !important;
}

.custom-introjs-tooltip .introjs-button {
  color: #000000 !important;
}
</style>
"""
)
