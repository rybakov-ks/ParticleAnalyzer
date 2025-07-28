from particleanalyzer.version import __version__

about_ru = f"""
<div style="max-width:800px;margin:0 auto 1px auto;padding:1px;font-family:var(--font)">
    <!-- Header with badges -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div style="display:flex;gap:10px">
            <a href="https://pypi.org/project/particleanalyzer/" target="_blank">
                <img src="https://img.shields.io/pypi/v/particleanalyzer?label=PyPI&color=blue&logo=pypi" alt="PyPI" style="height:24px">
            </a>
            <a href="https://pepy.tech/project/particleanalyzer" target="_blank">
                <img src="https://static.pepy.tech/badge/particleanalyzer/month?color=green&logo=python" alt="Downloads" style="height:24px">
            </a>
        </div>
        <div style="display:flex;gap:10px">
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/stargazers" target="_blank">
                <img src="https://img.shields.io/github/stars/rybakov-ks/ParticleAnalyzer?logo=github" alt="Stars" style="height:24px">
            </a>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/blob/main/LICENSE" target="_blank">
                <img src="https://img.shields.io/github/license/rybakov-ks/ParticleAnalyzer?color=orange" alt="License" style="height:24px">
            </a>
        </div>
    </div>

    <!-- Main content with logo -->
    <div style="
        background:var(--block-background-fill);
        padding:20px;
        border-radius:8px;
        margin-bottom:20px;
        border-left:4px solid #4a6bdf;
        border-top:1px solid var(--border-color-primary);
        border-right:1px solid var(--border-color-primary);
        border-bottom:1px solid var(--border-color-primary);
        box-shadow:var(--block-shadow)
    ">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
            <svg width="250" height="55" viewBox="0 0 250 55" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                <image x="2" y="0" width="46" height="46" preserveAspectRatio="xMidYMid meet"
                       xlink:href="https://svgsilh.com/svg/305079-2196f3.svg"/>
                <g font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" text-rendering="optimizeLegibility">
                    <text x="55" y="25" font-size="22" font-weight="600" letter-spacing="-0.3">
                        <tspan fill="#3b82f6">ParticleAnalyzer</tspan>
                    </text>
                    <text x="56" y="40" font-size="11" fill="#64748b" font-weight="500">
                        SEM Image Analysis Tool
                    </text>
                </g>
                <line x1="49" y1="0" x2="49" y2="50" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="3,2"/>
            </svg>
        </div>
        <p style="font-size:16px;line-height:1.6;margin-bottom:0;color:var(--text-color)">
            Инструмент для  <strong style="color:var(--block-label-text-color)">автоматической сегментации</strong>
            частиц на SEM-изображениях, измерения их размерных характеристик, проведения статистического анализа
            и экспорта полученных данных.          
        </p>
    </div>

    <!-- Video Demo Block -->
    <div style="background:var(--block-background-fill);padding:20px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow);text-align:center">
        <h3 style="margin-top:0;color:var(--header-text-color);font-weight:600">🎥 Видео-демонстрация работы</h3>
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin-top:15px;border-radius:6px">
            <iframe src="https://rutube.ru/play/embed/1f879a0e65c95168704ba53b94f9109a" 
                    style="position:absolute;top:0;left:0;width:100%;height:100%;border:none" 
                    frameborder="0" 
                    allow="cross-origin-isolated; accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        <p style="font-size:14px;color:var(--text-color-secondary);margin-top:10px">
            Посмотрите, как работает ParticleAnalyzer на реальных примерах
        </p>
    </div>

    <!-- Support block -->
    <div style="background:var(--block-background-fill);padding:15px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow)">
        <h3 style="margin-top:0;color:#e65100;font-weight:600">🛠 Техническая поддержка</h3>
        <div style="font-size:15px;line-height:1.5;color:var(--text-color)">
            <div style="margin-bottom:8px">При возникновении проблем:</div>
            <ul style="margin-top:8px;margin-bottom:12px;padding-left:20px;color:var(--text-color)">
                <li>Приложите проблемное изображение</li>
                <li>Приложите скриншот ошибки</li>
                <li>Опишите ожидаемый результат</li>
                <li>Укажите версию программы</li>
            </ul>
            <strong>Контакт:</strong> 
            <a href="mailto:rybakov-ks@ya.ru" style="color:var(--link-text-color);text-decoration:none">rybakov-ks@ya.ru</a>
        </div>
    </div>

    <!-- Footer -->
    <div style="display:flex;justify-content:space-between;align-items:center;padding-top:15px;border-top:1px solid var(--border-color-primary);font-size:14px;color:var(--text-color)">
        <div>
            <strong>Исходный код:</strong>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer" target="_blank" 
               style="color:var(--link-text-color);text-decoration:none;margin-left:8px">
               github.com/rybakov-ks/ParticleAnalyzer
            </a>
        </div>
        <div style="color:var(--body-text-color-subdued)">Версия v{__version__} | © 2025</div>
    </div>
</div>
"""

about_en = f"""
<div style="max-width:800px;margin:0 auto 1px auto;padding:1px;font-family:var(--font)">
    <!-- Header with badges -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div style="display:flex;gap:10px">
            <a href="https://pypi.org/project/particleanalyzer/" target="_blank">
                <img src="https://img.shields.io/pypi/v/particleanalyzer?label=PyPI&color=blue&logo=pypi" alt="PyPI" style="height:24px">
            </a>
            <a href="https://pepy.tech/project/particleanalyzer" target="_blank">
                <img src="https://static.pepy.tech/badge/particleanalyzer/month?color=green&logo=python" alt="Downloads" style="height:24px">
            </a>
        </div>
        <div style="display:flex;gap:10px">
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/stargazers" target="_blank">
                <img src="https://img.shields.io/github/stars/rybakov-ks/ParticleAnalyzer?logo=github" alt="Stars" style="height:24px">
            </a>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/blob/main/LICENSE" target="_blank">
                <img src="https://img.shields.io/github/license/rybakov-ks/ParticleAnalyzer?color=orange" alt="License" style="height:24px">
            </a>
        </div>
    </div>

    <!-- Main content with logo -->
    <div style="
        background:var(--block-background-fill);
        padding:20px;
        border-radius:8px;
        margin-bottom:20px;
        border-left:4px solid #4a6bdf;
        border-top:1px solid var(--border-color-primary);
        border-right:1px solid var(--border-color-primary);
        border-bottom:1px solid var(--border-color-primary);
        box-shadow:var(--block-shadow)
    ">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
            <svg width="250" height="55" viewBox="0 0 250 55" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                <image x="2" y="0" width="46" height="46" preserveAspectRatio="xMidYMid meet"
                       xlink:href="https://svgsilh.com/svg/305079-2196f3.svg"/>
                <g font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" text-rendering="optimizeLegibility">
                    <text x="55" y="25" font-size="22" font-weight="600" letter-spacing="-0.3">
                        <tspan fill="#3b82f6">ParticleAnalyzer</tspan>
                    </text>
                    <text x="56" y="40" font-size="11" fill="#64748b" font-weight="500">
                        SEM Image Analysis Tool
                    </text>
                </g>
                <line x1="49" y1="0" x2="49" y2="50" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="3,2"/>
            </svg>
        </div>
        <p style="font-size:16px;line-height:1.6;margin-bottom:0;color:var(--text-color)">
            A tool for analyzing <strong style="color:var(--block-label-text-color)">particle size characteristics</strong> 
            in SEM images with automatic segmentation, statistical analysis, 
            and result export capabilities.
        </p>
    </div>

    <!-- Video Demo Block -->
    <div style="background:var(--block-background-fill);padding:20px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow);text-align:center">
        <h3 style="margin-top:0;color:var(--header-text-color);font-weight:600">🎥 Video Demonstration</h3>
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin-top:15px;border-radius:6px">
            <iframe src="https://www.youtube.com/embed/qlCuZDjDyqk" 
                    style="position:absolute;top:0;left:0;width:100%;height:100%;border:none" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        <p style="font-size:14px;color:var(--text-color-secondary);margin-top:10px">
            See how ParticleAnalyzer works with real examples
        </p>
    </div>

    <!-- Support block -->
    <div style="background:var(--block-background-fill);padding:15px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow)">
        <h3 style="margin-top:0;color:#e65100;font-weight:600">🛠 Technical Support</h3>
        <div style="font-size:15px;line-height:1.5;color:var(--text-color)">
            <div style="margin-bottom:8px">If you encounter any issues:</div>
            <ul style="margin-top:8px;margin-bottom:12px;padding-left:20px;color:var(--text-color)">
                <li>Attach the problematic image</li>
                <li>Include a screenshot of the error</li>
                <li>Describe the expected result</li>
                <li>Specify the program version</li>
            </ul>
            <strong>Contact:</strong> 
            <a href="mailto:rybakov-ks@ya.ru" style="color:var(--link-text-color);text-decoration:none">rybakov-ks@ya.ru</a>
        </div>
    </div>

    <!-- Footer -->
    <div style="display:flex;justify-content:space-between;align-items:center;padding-top:15px;border-top:1px solid var(--border-color-primary);font-size:14px;color:var(--text-color)">
        <div>
            <strong>Source code:</strong>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer" target="_blank" 
               style="color:var(--link-text-color);text-decoration:none;margin-left:8px">
               github.com/rybakov-ks/ParticleAnalyzer
            </a>
        </div>
        <div style="color:var(--body-text-color-subdued)">Version v{__version__} | © 2025</div>
    </div>
</div>
"""

about_zh_cn = f"""
<div style="max-width:800px;margin:0 auto 1px auto;padding:1px;font-family:var(--font)">
    <!-- 徽标头部 -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div style="display:flex;gap:10px">
            <a href="https://pypi.org/project/particleanalyzer/" target="_blank">
                <img src="https://img.shields.io/pypi/v/particleanalyzer?label=PyPI&color=blue&logo=pypi" alt="PyPI" style="height:24px">
            </a>
            <a href="https://pepy.tech/project/particleanalyzer" target="_blank">
                <img src="https://static.pepy.tech/badge/particleanalyzer/month?color=green&logo=python" alt="下载量" style="height:24px">
            </a>
        </div>
        <div style="display:flex;gap:10px">
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/stargazers" target="_blank">
                <img src="https://img.shields.io/github/stars/rybakov-ks/ParticleAnalyzer?logo=github" alt="星标" style="height:24px">
            </a>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/blob/main/LICENSE" target="_blank">
                <img src="https://img.shields.io/github/license/rybakov-ks/ParticleAnalyzer?color=orange" alt="许可证" style="height:24px">
            </a>
        </div>
    </div>

    <!-- 主要内容 -->
    <div style="
        background:var(--block-background-fill);
        padding:20px;
        border-radius:8px;
        margin-bottom:20px;
        border-left:4px solid #4a6bdf;
        border-top:1px solid var(--border-color-primary);
        border-right:1px solid var(--border-color-primary);
        border-bottom:1px solid var(--border-color-primary);
        box-shadow:var(--block-shadow)
    ">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
            <svg width="250" height="55" viewBox="0 0 250 55" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                <image x="2" y="0" width="46" height="46" preserveAspectRatio="xMidYMid meet"
                       xlink:href="https://svgsilh.com/svg/305079-2196f3.svg"/>
                <g font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" text-rendering="optimizeLegibility">
                    <text x="55" y="25" font-size="22" font-weight="600" letter-spacing="-0.3">
                        <tspan fill="#3b82f6">ParticleAnalyzer</tspan>
                    </text>
                    <text x="56" y="40" font-size="11" fill="#64748b" font-weight="500">
                        SEM Image Analysis Tool
                    </text>
                </g>
                <line x1="49" y1="0" x2="49" y2="50" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="3,2"/>
            </svg>
        </div>
        <p style="font-size:16px;line-height:1.6;margin-bottom:0;color:var(--text-color)">
            一款用于分析<strong style="color:var(--block-label-text-color)">颗粒尺寸特征</strong>的工具，
            支持SEM图像的自动分割、统计分析以及结果导出功能。
        </p>
    </div>

    <!-- 视频演示 -->
    <div style="background:var(--block-background-fill);padding:20px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow);text-align:center">
        <h3 style="margin-top:0;color:var(--header-text-color);font-weight:600">🎥 视频演示</h3>
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin-top:15px;border-radius:6px">
            <iframe src="https://www.youtube.com/embed/qlCuZDjDyqk" 
                    style="position:absolute;top:0;left:0;width:100%;height:100%;border:none" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        <p style="font-size:14px;color:var(--text-color-secondary);margin-top:10px">
            观看颗粒分析器在实际案例中的应用
        </p>
    </div>

    <!-- 技术支持 -->
    <div style="background:var(--block-background-fill);padding:15px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow)">
        <h3 style="margin-top:0;color:#e65100;font-weight:600">🛠 技术支持</h3>
        <div style="font-size:15px;line-height:1.5;color:var(--text-color)">
            <div style="margin-bottom:8px">如遇问题请提供：</div>
            <ul style="margin-top:8px;margin-bottom:12px;padding-left:20px;color:var(--text-color)">
                <li>问题图像文件</li>
                <li>错误截图</li>
                <li>预期结果描述</li>
                <li>软件版本信息</li>
            </ul>
            <strong>联系方式：</strong> 
            <a href="mailto:rybakov-ks@ya.ru" style="color:var(--link-text-color);text-decoration:none">rybakov-ks@ya.ru</a>
        </div>
    </div>

    <!-- 页脚 -->
    <div style="display:flex;justify-content:space-between;align-items:center;padding-top:15px;border-top:1px solid var(--border-color-primary);font-size:14px;color:var(--text-color)">
        <div>
            <strong>源代码：</strong>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer" target="_blank" 
               style="color:var(--link-text-color);text-decoration:none;margin-left:8px">
               github.com/rybakov-ks/ParticleAnalyzer
            </a>
        </div>
        <div style="color:var(--body-text-color-subdued)">版本 v{__version__} | © 2025 版权所有</div>
    </div>
</div>
"""

about_zh_tw = f"""
<div style="max-width:800px;margin:0 auto 1px auto;padding:1px;font-family:var(--font)">
    <!-- 標題與徽章 -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div style="display:flex;gap:10px">
            <a href="https://pypi.org/project/particleanalyzer/" target="_blank">
                <img src="https://img.shields.io/pypi/v/particleanalyzer?label=PyPI&color=blue&logo=pypi" alt="PyPI" style="height:24px">
            </a>
            <a href="https://pepy.tech/project/particleanalyzer" target="_blank">
                <img src="https://static.pepy.tech/badge/particleanalyzer/month?color=green&logo=python" alt="下載量" style="height:24px">
            </a>
        </div>
        <div style="display:flex;gap:10px">
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/stargazers" target="_blank">
                <img src="https://img.shields.io/github/stars/rybakov-ks/ParticleAnalyzer?logo=github" alt="星標" style="height:24px">
            </a>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer/blob/main/LICENSE" target="_blank">
                <img src="https://img.shields.io/github/license/rybakov-ks/ParticleAnalyzer?color=orange" alt="授權" style="height:24px">
            </a>
        </div>
    </div>

    <!-- 主要內容 -->
    <div style="
        background:var(--block-background-fill);
        padding:20px;
        border-radius:8px;
        margin-bottom:20px;
        border-left:4px solid #4a6bdf;
        border-top:1px solid var(--border-color-primary);
        border-right:1px solid var(--border-color-primary);
        border-bottom:1px solid var(--border-color-primary);
        box-shadow:var(--block-shadow)
    ">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
            <svg width="250" height="55" viewBox="0 0 250 55" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                <image x="2" y="0" width="46" height="46" preserveAspectRatio="xMidYMid meet"
                       xlink:href="https://svgsilh.com/svg/305079-2196f3.svg"/>
                <g font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" text-rendering="optimizeLegibility">
                    <text x="55" y="25" font-size="22" font-weight="600" letter-spacing="-0.3">
                        <tspan fill="#3b82f6">ParticleAnalyzer</tspan>
                    </text>
                    <text x="56" y="40" font-size="11" fill="#64748b" font-weight="500">
                        SEM Image Analysis Tool
                    </text>
                </g>
                <line x1="49" y1="0" x2="49" y2="50" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="3,2"/>
            </svg>
        </div>
        <p style="font-size:16px;line-height:1.6;margin-bottom:0;color:var(--text-color)">
            用於分析<strong style="color:var(--block-label-text-color)">粒子尺寸特徵</strong>的工具，
            具備SEM影像自動分割、統計分析及結果導出功能。
        </p>
    </div>

    <!-- 影片示範 -->
    <div style="background:var(--block-background-fill);padding:20px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow);text-align:center">
        <h3 style="margin-top:0;color:var(--header-text-color);font-weight:600">🎥 影片示範</h3>
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin-top:15px;border-radius:6px">
            <iframe src="https://www.youtube.com/embed/qlCuZDjDyqk" 
                    style="position:absolute;top:0;left:0;width:100%;height:100%;border:none" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        <p style="font-size:14px;color:var(--text-color-secondary);margin-top:10px">
            觀看粒子分析器的實際操作範例
        </p>
    </div>

    <!-- 技術支援 -->
    <div style="background:var(--block-background-fill);padding:15px;border-radius:8px;margin-bottom:20px;border:1px solid var(--border-color-primary);box-shadow:var(--block-shadow)">
        <h3 style="margin-top:0;color:#e65100;font-weight:600">🛠 技術支援</h3>
        <div style="font-size:15px;line-height:1.5;color:var(--text-color)">
            <div style="margin-bottom:8px">若遇到問題請提供：</div>
            <ul style="margin-top:8px;margin-bottom:12px;padding-left:20px;color:var(--text-color)">
                <li>有問題的影像檔案</li>
                <li>錯誤截圖</li>
                <li>預期結果說明</li>
                <li>程式版本資訊</li>
            </ul>
            <strong>聯絡方式：</strong> 
            <a href="mailto:rybakov-ks@ya.ru" style="color:var(--link-text-color);text-decoration:none">rybakov-ks@ya.ru</a>
        </div>
    </div>

    <!-- 頁尾 -->
    <div style="display:flex;justify-content:space-between;align-items:center;padding-top:15px;border-top:1px solid var(--border-color-primary);font-size:14px;color:var(--text-color)">
        <div>
            <strong>原始碼：</strong>
            <a href="https://github.com/rybakov-ks/ParticleAnalyzer" target="_blank" 
               style="color:var(--link-text-color);text-decoration:none;margin-left:8px">
               github.com/rybakov-ks/ParticleAnalyzer
            </a>
        </div>
        <div style="color:var(--body-text-color-subdued)">版本 v{__version__} | © 2025 版權所有</div>
    </div>
</div>
"""
