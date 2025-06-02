# CSS для стилизации интерфейса
css = """
#app-container {
    max-width: 750px; /* Устанавливаем максимальную ширину приложения */
    margin: 0 auto; /* Центрируем контейнер */
}
footer {
    visibility: hidden;
}
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
"""

custom_head = """
<!-- HTML Meta Tags -->
<title>ParticleAnalyzer</title>
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
"""
