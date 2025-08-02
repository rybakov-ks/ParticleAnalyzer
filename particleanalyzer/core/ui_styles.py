from particleanalyzer.core.tour import tour

# CSS для стилизации интерфейса
css = """
/* ==========================================================================
   🌗 ПЕРЕМЕННЫЕ ТЕМЫ
   ========================================================================== */
:root {
  --primary: #3b82f6;
  --primary-dark: #2563eb;
  --text: #1e293b;
  --text-light: #64748b;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --border: #e2e8f0;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark {
  --primary: #60a5fa;
  --primary-dark: #3b82f6;
  --text: #f1f5f9;
  --text-light: #94a3b8;
  --bg: #0f172a;
  --card-bg: #1e293b;
  --border: #334155;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
}

/* ==========================================================================
   🧱 ОСНОВНАЯ СЕТКА
   ========================================================================== */
.gradio-container {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%) !important;
  font-family: 'Inter', system-ui, sans-serif !important;
  transition: all 0.3s ease !important;
}

.dark .gradio-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}

.gradio-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 50%, rgba(123, 179, 255, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 80% 70%, rgba(255, 153, 102, 0.15) 0%, transparent 40%);
  animation: gradientShift 15s ease infinite alternate;
  z-index: 0;
}

.dark .gradio-container::before {
  background: radial-gradient(circle at 20% 50%, rgba(56, 132, 255, 0.1) 0%, transparent 40%),
              radial-gradient(circle at 80% 70%, rgba(255, 107, 107, 0.1) 0%, transparent 40%);
}

#app-container {
  max-width: 790px;
  margin: 0 auto;
}

/* ==========================================================================
   🧩 ХЕДЕР
   ========================================================================== */
#gr-head {
  background: var(--card-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 0 !important;
  margin-top: 0 !important;
  box-shadow: var(--shadow) !important;
}

/* ==========================================================================
   📑 ТАБЫ И КОНТЕНТ
   ========================================================================== */
.tabs {
  background: var(--card-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 16px !important;
  margin-top: 0 !important;
  box-shadow: var(--shadow) !important;
}

.tabitem {
  padding: 0 16px !important;
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== Контейнер вкладок результатов ===== */
#tabs_result {
  margin-top: 0 !important;
  background: var(--card-bg) !important;
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-md) !important;
  overflow: hidden !important;
}

/* ===== Навигация по вкладкам ===== */
#tabs_result .tab-nav {
  background: var(--card-bg) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 16px !important;
}

#tabs_result .tab-button {
  padding: 12px 24px !important;
  font-weight: 500 !important;
  color: var(--text-light) !important;
  border: none !important;
  background: transparent !important;
  transition: all 0.3s ease !important;
}

#tabs_result .tab-button.selected {
  color: var(--primary) !important;
  position: relative;
}

#tabs_result .tab-button.selected::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
}

#tabs_result .tabitem {
  padding: 0 !important;
  animation: fadeIn 0.4s ease-out;
}

/* ==========================================================================
   🧾 ТАБЛИЦЫ
   ========================================================================== */
#dataframe-table,
#dataframe-table2 {
  width: 100%;
  table-layout: auto;
  border-radius: 8px !important;
}

#dataframe-table th, #dataframe-table td,
#dataframe-table2 th, #dataframe-table2 td {
  white-space: nowrap;
}

/* ==========================================================================
   🖼 ИЗОБРАЖЕНИЯ
   ========================================================================== */
#in-image-paint,
#in-image,
#output-image {
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
  background: var(--card-bg) !important;
  padding: 8px !important;
  object-fit: contain;
  width: 100%;
  transition: all 0.4s ease;
}

#analyze {
  background-color: var(--card-bg) !important;
  border-radius: 16px !important;
  padding: 16px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
  transition: all 0.3s ease;
}

/* ==========================================================================
   🌘 ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ
   ========================================================================== */
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
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 24px;
}

.slider:before {
  content: "";
  position: absolute;
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #3b71ca;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

/* ==========================================================================
   🎛 КАСТОМНЫЕ КНОПКИ
   ========================================================================== */
.custom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  width: 180px;
  height: 40px;
  border: none;
  border-radius: 50px !important;
  font-weight: 600;
  font-family: 'Segoe UI', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  color: white;
}

/* Иконка внутри кнопки */
.custom-btn img {
  width: 24px;
  height: 24px;
  margin-right: 12px;
  object-fit: contain;
}

/* Стили по типам кнопок */
.btn-analyze {
  background: linear-gradient(135deg, #7386d5 0%, #a0b1f5 100%);
  margin-left: auto;
}

.btn-clear {
  background: linear-gradient(135deg, #f68084 0%, #fda085 100%);
  margin-right: auto;
}

.btn-ai-run {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  margin-left: auto;
  width: 200px;
}

.btn-ai-cancel {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa3a3 100%);
  margin-right: auto;
  width: 200px;
}

.btn-yes {
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
  margin-left: auto;
}

.btn-no {
  background: linear-gradient(135deg, #F44336 0%, #FF5252 100%); 
  margin-right: auto;
}

/* Ripple эффект */
.custom-btn::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  width: 5px; height: 5px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 100%;
  opacity: 0;
  transform: scale(1) translate(-50%);
  transform-origin: 50% 50%;
}

.custom-btn:focus:not(:active)::after {
  animation: ripple 0.6s ease-out;
}

/* Наведение и активное состояние */
.custom-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.custom-btn:active {
  transform: translateY(1px);
}

/* ==========================================================================
   АДАПТИВНЫЕ СТИЛИ ДЛЯ МОБИЛЬНЫХ УСТРОЙСТВ
   ========================================================================== */
@media (max-width: 400px) {
  .custom-btn {
    width: 100%; /* Занимает всю доступную ширину */
    max-width: 280px; /* Но не более 280px */
    height: 48px; /* Увеличиваем высоту */
    font-size: 15px; /* Увеличиваем размер текста */
    padding: 0 20px; /* Больше внутренних отступов */
  }

  .custom-btn img {
    width: 26px; /* Увеличиваем иконки */
    height: 26px;
    margin-right: 10px;
  }

  /* Контейнер для кнопок */
  #button-row {
    flex-direction: column;
    align-items: center;
    gap: 12px; /* Увеличиваем расстояние между кнопками */
  }
}

/* Анимация ripple-эффекта */
@keyframes ripple {
  0% {
    transform: scale(0) translate(-50%);
    opacity: 1;
  }
  100% {
    transform: scale(20) translate(-50%);
    opacity: 0;
  }
}

/* ==========================================================================
   🌀 АНИМАЦИИ
   ========================================================================== */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes ripple {
  0%   { transform: scale(0); opacity: 0.7; }
  100% { transform: scale(20); opacity: 0; }
}

@keyframes gradientShift {
  0%   { background-position: 20% 50%, 80% 70%; }
  100% { background-position: 30% 60%, 70% 80%; }
}

/* ==========================================================================
   🧹 ДРУГОЕ
   ========================================================================== */
footer {
  display: none !important;
}

#button-row, #example-row {
    margin-top: -10px; /* расстояние между строками */
}
#button-row {
  display: flex;
  gap: 0px; /* расстояние между колонками */
}

/* Для мобильных устройств */
@media (max-width: 400px) {
    .logo-image {
        width: 30px !important; /* Фиксированная ширина для иконки */
        height: 40px !important;
        object-fit: cover;
        object-position: left center; /* Обрезаем справа, оставляя иконку слева */
    }
    
    /* Дополнительно можно скрыть текст в кнопке Помощь */
    @media (max-width: 480px) {
        button[onclick="startIntro()"] span {
            display: none;
        }
        button[onclick="startIntro()"] {
            padding: 7px !important;
            width: 40px !important;
            justify-content: center !important;
        }
    }
}
"""

custom_head = (
    """
<!-- HTML Meta Tags -->
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
<title>ParticleAnalyzer — SEM Image Analysis Tool</title>
<meta name="description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images." />

<!-- Facebook Meta Tags -->
<meta property="og:url" content="https://sem.rybakov-k.ru/" />
<meta property="og:type" content="website" />
<meta property="og:title" content="ParticleAnalyzer" />
<meta property="og:description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images." />
<meta property="og:image" content="https://rybakov-k.ru/assets/icon/logo_og.png" />

<!-- Twitter Meta Tags -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:creator" content="@rybakov_ks" />
<meta name="twitter:title" content="ParticleAnalyzer" />
<meta name="twitter:description" content="A Computer Vision Tool for Automatic Particle Segmentation and Size Analysis in Scanning Electron Microscope (SEM) Images." />
<meta name="twitter:image" content="https://rybakov-k.ru/assets/icon/logo_og.png" />
<meta property="twitter:domain" content="sem.rybakov-k.ru" />
<meta property="twitter:url" content="https://sem.rybakov-k.ru/" />
<!-- Meta Tags Generated via https://www.opengraph.xyz/ -->

<!-- Favicon -->
<link rel="icon" href="https://rybakov-k.ru/assets/icon/favicon.svg" type="image/x-icon" />

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
