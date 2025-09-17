"""
HTML/JS intro tour script for ParticleAnalyzer UI.
The string is injected into the Gradio page to initialize Intro.js steps.
"""

__all__ = ["tour"]

tour: str = """
<script>
  function getBrowserLanguage() {
    return navigator.language || navigator.userLanguage || 'en';
  }
  document.currentLang = getBrowserLanguage();

  function startIntro(lang = document.currentLang) {
    // Словарь переводов
    const translations = {
      'ru': {
        notificationText: 'Перейдите на вкладку <strong>"Анализ"</strong>.',
        notificationText2: 'Загрузите изображение для начала работы.',
        welcomeText: "Привет! Сейчас мы покажем, как работать с ParticleAnalyzer.",
        scaleSelectorText: "Здесь выберите, в каких единицах работать: пиксели, микроны или нанометры.",
        paintUploaderText: "Загрузите изображение СЭМ, затем с помощью инструмента 'Кисть' отметьте две точки для определения границ шкалы. При необходимости воспользуйтесь 'Ластиком' для корректировки и функцией 'Масштаб' для более точного позиционирования.",
        normalUploaderText: "Загрузите сюда ваше изображение СЭМ.",
        scaleInputText: "Укажите здесь длину шкалы, которая указана на вашем изображении.",
        examplesText: "В этом разделе можно выбрать один из предложенных примеров изображений — после выбора образец автоматически загрузится для анализа. Это позволяет быстро начать работу с типовыми данными и оценить настройки модели.",
        processButtonText: "Когда всё будет готово, нажмите эту кнопку для анализа.",
        outputImageText: "Визуализация результатов сегментации появится в этом окне. Дополнительные данные (таблицы, графики и файлы) будут доступны ниже.",
        cancelButtonText: "Прервать текущий анализ → нажмите эту кнопку, если нужно остановить обработку.",
        clearButtonText: "Очистить все поля → удалит текущие данные и подготовит форму для нового анализа.",
        tabsText: "Для повышения качества сегментации рекомендуется индивидуальная настройка параметров под конкретные особенности изображения. Перейдите в раздел <b>Настройки</b>, чтобы продолжить демонстрацию и оптимизировать процесс анализа для вашего случая.",
        modelSettingText: "В данном разделе настраиваются параметры модели для детекции частиц. Доступны три архитектуры: YOLOv11, YOLOv12 и Cascade_x152 - каждая может демонстрировать различную эффективность в зависимости от характеристик анализируемых частиц и условий съемки. Чувствительность обнаружения регулируется параметром точности: снижение значения позволяет выявлять больше частиц, включая мелкие и слабовыраженные, тогда как увеличение помогает минимизировать ложные срабатывания. Порог перекрытия (IoU) определяет степень допустимого перекрытия частиц при детекции: значения 0.1-0.3 оптимальны для плотных скоплений, тогда как диапазон 0.5-0.7 лучше подходит для предотвращения ошибочного разделения слипшихся объектов. Для достижения оптимальных результатов рекомендуется экспериментально подбирать параметры под конкретные особенности анализируемых изображений.",
        sahiSettingText: "Для анализа больших изображений (свыше 2000 пикселей) с мелкими или слипшимися частицами рекомендуется включить режим SAHI (Slicing Aided Hyper Inference). Оптимальные параметры включают размер сегментов 200-400 пикселей и перекрытие 10-20% - такие настройки обеспечивают баланс между точностью детекции и производительностью. Уменьшение размера сегментов повышает детализацию анализа, но увеличивает время обработки, в то время как регулировка процента перекрытия помогает улучшить обнаружение частиц в областях стыков сегментов, особенно при неоднородном распределении объектов. Эти параметры особенно важны при работе со сложными изображениями, где требуется высокая точность сегментации.",
        solutionSegmentText: "В данном разделе можно настроить разрешение: увеличение этого параметра повышает точность анализа, однако приводит к более длительной обработке.",
        numberDetectionsText: "Ограничение количества частиц: уменьшите, если система тормозит, увеличьте для редких частиц на больших площадях. Сначала попробуйте 1000, затем корректируйте.",
        binsFeretText: "В этом разделе можно настроить количество бинов гистограммы для анализа распределения частиц — оптимальное значение составляет 10-20 бинов, так как оно обеспечивает четкие и хорошо различимые пики.",
        visualizationSettings: "В данном разделе можно задать параметры визуализации контура и заливки сегментированных частиц. Также здесь доступны опция отображения диаметров Ферета, которые показывают ориентацию частиц непосредственно на результатах сегментации, и опция отображения масштабной шкалы в пикселях.",
        modelParamsText: "Отлично! Теперь настройте параметры модели.",
        buttons: {
          next: 'Далее',
          prev: 'Назад',
          done: 'Закрыть'
        }
      },
      'en': {
        notificationText: 'Go to the <strong>Analysis</strong> tab.',
        notificationText2: 'Upload an image to get started.',
        welcomeText: "Hello! We'll now show you how to work with ParticleAnalyzer.",
        scaleSelectorText: "Here you can select the units to work with: pixels, microns, or nanometers.",
        paintUploaderText: "Upload your SEM image, then use the 'Brush' tool to mark two points to define the scale boundaries. If needed, use the 'Eraser' for corrections and the 'Zoom' function for more precise positioning.",
        normalUploaderText: "Upload your SEM image here.",
        scaleInputText: "Enter here the scale length that is indicated on your image.",
        examplesText: "In this section, you can select one of the provided example images - after selection, the sample will be automatically loaded for analysis. This allows you to quickly start working with typical data and evaluate model settings.",
        processButtonText: "When everything is ready, click this button to start the analysis.",
        outputImageText: "The visualization of segmentation results will appear in this window. Additional data (tables, charts, and files) will be available below.",
        cancelButtonText: "To interrupt the current analysis → click this button if you need to stop processing.",
        clearButtonText: "Clear all fields → removes current data and prepares the form for a new analysis.",
        tabsText: "For improved segmentation quality, individual parameter tuning is recommended based on specific image characteristics. Go to the <b>Settings</b> section to continue the demonstration and optimize the analysis process for your case.",
        modelSettingText: "This section configures the particle detection model parameters. Three architectures are available: YOLOv11, YOLOv12, and Cascade_x152 - each may demonstrate different effectiveness depending on the characteristics of the analyzed particles and imaging conditions. Detection sensitivity is adjusted via the precision parameter: lowering the value allows detecting more particles, including small and faint ones, while increasing it helps minimize false positives. The overlap threshold (IoU) determines the acceptable degree of particle overlap during detection: values of 0.1-0.3 are optimal for dense clusters, while the 0.5-0.7 range is better suited for preventing erroneous separation of overlapping objects. For optimal results, experimental parameter tuning is recommended based on specific image characteristics.",
        sahiSettingText: "For analyzing large images (over 2000 pixels) with small or overlapping particles, enabling SAHI mode (Slicing Aided Hyper Inference) is recommended. Optimal parameters include segment sizes of 200-400 pixels and 10-20% overlap - these settings provide a balance between detection accuracy and performance. Reducing segment size increases analysis detail but increases processing time, while adjusting the overlap percentage helps improve particle detection in segment junction areas, especially with non-uniform object distribution. These parameters are particularly important when working with complex images requiring high segmentation accuracy.",
        solutionSegmentText: "In this section, you can configure the resolution: increasing this parameter improves analysis accuracy but leads to longer processing times.",
        numberDetectionsText: "Limit the number of particles: decrease if the system is slow, increase for rare particles in large areas. Start with 1000, then adjust as needed.",
        binsFeretText: "In this section, you can configure the number of histogram bins for particle distribution analysis - the optimal value is 10-20 bins, as it provides clear and well-distinguishable peaks.",
        visualizationSettings: "In this section you can set the parameters for visualizing the outline and fill of segmented particles. Also available here is the option to display Feret diameters, which show the orientation of particles directly on the segmentation results, and the option to display a pixel scale.",
        modelParamsText: "Great! Now configure the model parameters.",
        buttons: {
          next: 'Next',
          prev: 'Back',
          done: 'Close'
        }
      },
      'zh-TW': {
        notificationText: '前往<strong>分析</strong>選項卡。 ',
        notificationText2: '上傳圖片即可開始。 ',
        welcomeText: "您好！我們將為您展示如何使用ParticleAnalyzer。",
        scaleSelectorText: "在此選擇工作單位：像素、微米或奈米。",
        paintUploaderText: "上傳您的SEM圖像，然後使用'畫筆'工具標記兩個點以定義比例尺邊界。如需修正，可使用'橡皮擦'進行調整，並使用'縮放'功能進行更精確的定位。",
        normalUploaderText: "請在此上傳您的SEM圖像。",
        scaleInputText: "在此輸入圖像上標示的比例尺長度。",
        examplesText: "在本區塊中，您可以選擇提供的範例圖像之一 - 選擇後樣本將自動載入進行分析。這讓您能快速開始使用典型數據並評估模型設置。",
        processButtonText: "當一切準備就緒，點擊此按鈕開始分析。",
        outputImageText: "分割結果的可視化將顯示在此窗口中。其他數據（表格、圖表和文件）將在下方提供。",
        cancelButtonText: "中斷當前分析 → 如需停止處理請點擊此按鈕。",
        clearButtonText: "清除所有字段 → 移除當前數據並準備表單進行新分析。",
        tabsText: "為提高分割質量，建議根據圖像特徵進行個別參數調整。前往<b>設置</b>部分繼續演示，並為您的案例優化分析流程。",
        modelSettingText: "本區塊配置粒子檢測模型參數。提供三種架構：YOLOv11、YOLOv12和Cascade_x152 - 每種架構根據分析粒子的特性和成像條件可能展現不同效果。檢測靈敏度通過精度參數調整：降低值可檢測更多粒子，包括微小和不明顯的粒子，而提高值有助於最小化誤報。重疊閾值(IoU)決定檢測期間可接受的粒子重疊程度：0.1-0.3的值對密集集群最為理想，而0.5-0.7範圍更適合防止重疊物體錯誤分離。為達最佳效果，建議根據特定圖像特徵進行實驗性參數調整。",
        sahiSettingText: "分析大型圖像（超過2000像素）且含有微小或重疊粒子時，建議啟用SAHI模式（切片輔助超推論）。最佳參數包括200-400像素的切片大小和10-20%的重疊 - 這些設置在檢測精度和性能之間提供平衡。減小切片尺寸可增加分析細節但會增加處理時間，而調整重疊百分比有助於改善切片連接區域的粒子檢測，特別是在非均勻物體分布情況下。這些參數對於需要高分割精度的複雜圖像處理尤為重要。",
        solutionSegmentText: "在本區塊中，您可以配置解析度：提高此參數可改善分析精度，但會導致更長的處理時間。",
        numberDetectionsText: "限制粒子數量：系統運行緩慢時減少，大面積稀有粒子時增加。先從1000開始，然後根據需要調整。",
        binsFeretText: "在本區塊中，您可以配置用於粒子分布分析的直方圖區間數 - 最佳值為10-20個區間，因其能提供清晰且易於區分的峰值。",
        visualizationSettings: "在本部分中，您可以設定用於視覺化分割粒子輪廓和填充的參數。此外，您還可以選擇顯示費雷特直徑（Feret diameters），該直徑可直接在分割結果中顯示粒子的方向，以及顯示像素比例的選項。",
        modelParamsText: "很好！現在配置模型參數。",
        buttons: {
          next: '下一步',
          prev: '上一步',
          done: '關閉'
        }
      },
      'zh-CN': {
        notificationText: '前往<strong>分析</strong>选项卡。',
        notificationText2: '上传图片即可开始。',
        welcomeText: "您好！我们将为您展示如何使用ParticleAnalyzer。",
        scaleSelectorText: "在此选择工作单位：像素、微米或纳米。",
        paintUploaderText: "上传您的SEM图像，然后使用'画笔'工具标记两个点以定义比例尺边界。如需修正，可使用'橡皮擦'进行调整，并使用'缩放'功能进行更精确的定位。",
        normalUploaderText: "请在此上传您的SEM图像。",
        scaleInputText: "在此输入图像上标示的比例尺长度。",
        examplesText: "在本区域中，您可以选择提供的示例图像之一 - 选择后样本将自动加载进行分析。这能让您快速开始使用典型数据并评估模型设置。",
        processButtonText: "当一切准备就绪，点击此按钮开始分析。",
        outputImageText: "分割结果的可视化将显示在此窗口中。其他数据（表格、图表和文件）将在下方提供。",
        cancelButtonText: "中断当前分析 → 如需停止处理请点击此按钮。",
        clearButtonText: "清除所有字段 → 移除当前数据并准备表单进行新分析。",
        tabsText: "为提高分割质量，建议根据图像特征进行个别参数调整。前往<b>设置</b>部分继续演示，并为您的案例优化分析流程。",
        modelSettingText: "本区域配置粒子检测模型参数。提供三种架构：YOLOv11、YOLOv12和Cascade_x152 - 每种架构根据分析粒子的特性和成像条件可能展现不同效果。检测灵敏度通过精度参数调整：降低值可检测更多粒子，包括微小和不明显的粒子，而提高值有助于最小化误报。重叠阈值(IoU)决定检测期间可接受的粒子重叠程度：0.1-0.3的值对密集集群最为理想，而0.5-0.7范围更适合防止重叠物体错误分离。为达最佳效果，建议根据特定图像特征进行实验性参数调整。",
        sahiSettingText: "分析大型图像（超过2000像素）且含有微小或重叠粒子时，建议启用SAHI模式（切片辅助超推理）。最佳参数包括200-400像素的切片大小和10-20%的重叠 - 这些设置在检测精度和性能之间提供平衡。减小切片尺寸可增加分析细节但会增加处理时间，而调整重叠百分比有助于改善切片连接区域的粒子检测，特别是在非均匀物体分布情况下。这些参数对于需要高分割精度的复杂图像处理尤为重要。",
        solutionSegmentText: "在本区域中，您可以配置分辨率：提高此参数可改善分析精度，但会导致更长的处理时间。",
        numberDetectionsText: "限制粒子数量：系统运行缓慢时减少，大面积稀有粒子时增加。先从1000开始，然后根据需要调整。",
        binsFeretText: "在本区域中，您可以配置用于粒子分布分析的直方图区间数 - 最佳值为10-20个区间，因其能提供清晰且易于区分的峰值。",
        visualizationSettings: "在本部分中，您可以设置用于可视化分割粒子轮廓和填充的参数。此外，您还可以选择显示费雷特直径（Feret diameters），该直径可直接在分割结果中显示粒子的方向，以及显示像素比例的选项。",
        modelParamsText: "很好！现在配置模型参数。",
        buttons: {
          next: '下一步',
          prev: '上一步',
          done: '关闭'
        }
      }
    };

    // Fallback to English if language not supported
    const t = translations[lang] || translations['en'];

    const isElementVisible = (selector) => {
      const el = document.querySelector(selector);
      return el && el.offsetWidth > 0 && el.offsetHeight > 0;
    };

    let isKeyboardBlocked = false;
    let originalKeyDownHandler = null;

    function blockAllKeys(e) {
      if (isKeyboardBlocked) {
        console.log('Key blocked:', e.key);
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
      }
    }

    function setKeyboardBlocking(block) {
      isKeyboardBlocked = block;
      
      if (block) {
        console.log('Keyboard blocking enabled');
        // Добавляем обработчики для всех клавиатурных событий
        document.addEventListener('keydown', blockAllKeys, true);
        document.addEventListener('keypress', blockAllKeys, true);
        document.addEventListener('keyup', blockAllKeys, true);
        
        const introInstance = introJs();
        if (introInstance && introInstance._onKeyDown) {
          originalKeyDownHandler = introInstance._onKeyDown;
          introInstance._onKeyDown = function(e) {
            console.log('IntroJS key blocked:', e.key);
            e.preventDefault();
            e.stopPropagation();
            return false;
          };
        }
      } else {
        console.log('Keyboard blocking disabled');

        document.removeEventListener('keydown', blockAllKeys, true);
        document.removeEventListener('keypress', blockAllKeys, true);
        document.removeEventListener('keyup', blockAllKeys, true);
        
        if (originalKeyDownHandler) {
          const introInstance = introJs();
          if (introInstance) {
            introInstance._onKeyDown = originalKeyDownHandler;
          }
          originalKeyDownHandler = null;
        }
      }
    }

    const checkVisibility = () => {
      const updateNotification = () => {
        const normalVisible = isElementVisible('#in-image');
        const scaleSelectorVisible = isElementVisible('#scale-selector');

        let notificationHTML = '';
        let showNotification = false;

        if (!normalVisible && !scaleSelectorVisible) {
          // Нет #in-image и нет #scale-selector
          showNotification = true;
          notificationHTML = t.notificationText; // содержит HTML
        } else if (!normalVisible && scaleSelectorVisible) {
          // Есть #scale-selector, но нет #in-image
          showNotification = true;
          notificationHTML = t.notificationText2; // содержит HTML
        }

        let notification = document.getElementById('tour-notification');

        if (showNotification) {
          if (!notification) {
            // Создаем уведомление
            notification = document.createElement('div');
            notification.id = 'tour-notification';
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.left = '50%';
            notification.style.transform = 'translateX(-50%)';
            notification.style.background = '#f8f9fa';
            notification.style.padding = '15px 35px 15px 25px';
            notification.style.borderRadius = '4px';
            notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            notification.style.zIndex = '1000';
            notification.style.border = '1px solid #dee2e6';
            notification.style.fontSize = '14px';
            notification.style.display = 'flex';
            notification.style.alignItems = 'center';
            notification.style.gap = '15px';

            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '5px';
            closeBtn.style.right = '5px';
            closeBtn.style.background = 'none';
            closeBtn.style.border = 'none';
            closeBtn.style.fontSize = '16px';
            closeBtn.style.cursor = 'pointer';
            closeBtn.style.padding = '0 5px';
            closeBtn.style.color = '#6c757d';

            closeBtn.onclick = function() {
              document.body.removeChild(notification);
            };

            notification.appendChild(closeBtn);
            document.body.appendChild(notification);
          }

          // Обновляем текст динамически с поддержкой HTML
          let content = notification.querySelector('.notification-text');
          if (!content) {
            content = document.createElement('p');
            content.className = 'notification-text';
            content.style.margin = '0';
            notification.appendChild(content);
          }
          content.innerHTML = notificationHTML;

        } else {
          // Скрываем уведомление и запускаем тур
          if (notification) {
            document.body.removeChild(notification);
          }
          initTour();
          clearInterval(checkInterval);
        }
      };

      const checkInterval = setInterval(updateNotification, 500);
    };

    const initTour = () => {
      // Базовые шаги тура (всегда показываются)
      const steps = [
        { 
          intro: t.welcomeText,
          position: 'bottom'
        },
        {
          element: '#scale-selector',
          intro: t.scaleSelectorText,
          disableInteraction: false,
          position: 'left'
        },
        {
          element: '#in-image',
          intro: t.normalUploaderText,
          disableInteraction: true,
          position: 'left',
        }
      ];

      // Добавляем scale-input если виден scale_input_row
      if (isElementVisible('#scale-input-row')) {
        steps.push({
          element: '#scale-input',
          intro: t.scaleInputText,
          disableInteraction: true,
          position: 'right'
        });
      }

      const commonSteps = [
        // Остальные шаги, которые всегда есть
        {
          element: '#example-row',
          intro: t.examplesText,
          disableInteraction: true,
          position: 'bottom'
        },
        {
          element: '#process-button',
          intro: t.processButtonText,
          disableInteraction: true,
          position: 'left'
        },
        {
          element: '#in-image',
          intro: t.outputImageText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#clear-btn',
          intro: t.cancelButtonText,
          disableInteraction: true,
          position: 'bottom'
        },
        {
          element: '#clear-btn',
          intro: t.clearButtonText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#setting-button',
          intro: t.tabsText,
          position: 'top',
          disableInteraction: false
        },
        {
          element: '#model-setting',
          intro: t.modelSettingText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#sahi-setting',
          intro: t.sahiSettingText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#solution-setting',
          intro: t.solutionSegmentText,
          disableInteraction: true,
          position: 'left'
        },
        {
          element: '#number-detections',
          intro: t.numberDetectionsText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#bins-feret-diametr',
          intro: t.binsFeretText,
          disableInteraction: true,
          position: 'right'
        },
        {
          element: '#visualization-settings',
          intro: t.visualizationSettings,
          disableInteraction: true,
          position: 'top'
        },  
      ];

      const allSteps = steps.concat(commonSteps);

      // Функция фильтрации шагов - проверяем только scale-input, остальные всегда показываем
      const filterSteps = () => {
        return allSteps.filter((step) => {
          // Для scale-input проверяем видимость
          if (step.element === '#scale-input') {
            return isElementVisible('#scale-input-row');
          }
          // Все остальные шаги показываем всегда
          return true;
        });
      };

      const intro = introJs().setOptions({ 
        steps: filterSteps(),
        nextLabel: t.buttons.next,
        prevLabel: t.buttons.prev,
        doneLabel: t.buttons.done,
        showProgress: true,
        showBullets: false,
        tooltipClass: 'custom-introjs-tooltip',
        highlightClass: 'custom-introjs-highlight',
        exitOnOverlayClick: false,
        keyboardNavigation: false
      });

      setTimeout(() => {
        setKeyboardBlocking(true);
      }, 100);

      intro.onbeforechange(function(targetElement) {
        const triggerElements = ['#in-image', '#scale-selector'];
        if (targetElement && triggerElements.includes('#' + targetElement.id)) {
          intro._options.steps = filterSteps();
          
          // Находим индексы шагов scale-input и example-row
          const scaleInputStepIndex = intro._introItems.findIndex(item => 
            item.element && item.element.id === 'scale-input'
          );
          
          const exampleRowStepIndex = intro._introItems.findIndex(item => 
            item.element && item.element.id === 'example-row'
          );
          
          // Динамически добавляем или удаляем scale-input
          if (isElementVisible('#scale-input-row')) {
            // scale_input_row виден - добавляем scale-input шаг
            if (scaleInputStepIndex === -1) {
              const scaleInputStep = {
                element: document.querySelector('#scale-input'),
                title: '',
                intro: t.scaleInputText,
                disableInteraction: true,
                position: 'right'
              };
              // Вставляем scale-input перед example-row
              intro._introItems.splice(exampleRowStepIndex, 0, scaleInputStep);
            }
          } else {
            // scale_input_row не виден - удаляем scale-input шаг
            if (scaleInputStepIndex !== -1) {
              intro._introItems.splice(scaleInputStepIndex, 1);
            }
          }
          
          intro.refresh();
        }

        if (targetElement && targetElement.id === 'setting-button') {
          const nextButton = document.querySelector('.introjs-nextbutton');
          if (nextButton) {
            nextButton.style.display = 'none';

            const checkSettingsTab = setInterval(() => {
              if (isElementVisible('#model-setting')) {
                clearInterval(checkSettingsTab);
                const nextButton = document.querySelector('.introjs-nextbutton');
                if (nextButton) {
                  nextButton.style.display = 'inline-block';
                  nextButton.style.animation = 'fadeIn 0.3s';
                }
              }
            }, 100);
          }
        }
        
        return true;
      });

      const style = document.createElement('style');
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .introjs-button {
          transition: opacity 0.3s;
        }
      `;
      document.head.appendChild(style);

      intro.onexit(function() {
        document.querySelectorAll('.custom-introjs-highlight').forEach(el => {
          el.classList.remove('custom-introjs-highlight');
        });
        
        const nextButton = document.querySelector('.introjs-nextbutton');
        if (nextButton) {
          nextButton.style.display = 'inline-block';
          nextButton.style.animation = '';
        }
        
        setKeyboardBlocking(false);
      });

      intro.oncomplete(function() {
        setKeyboardBlocking(false);
      });

      intro.start();
    };

    checkVisibility();
  }
</script>
"""
