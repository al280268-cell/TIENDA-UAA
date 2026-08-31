/**
 * js/questions.js — UAA E-Commerce Game
 * Banco de 20 preguntas organizadas en 6 misiones.
 * Las opciones se mezclan aleatoriamente en cada carga.
 */

(function () {
  'use strict';

  // ─────────────────────────────────────────────
  // BANCO DE PREGUNTAS (20 preguntas)
  // Cada pregunta tiene: id, text, options[], correctId, explanation, concept
  // ─────────────────────────────────────────────

  const ALL_QUESTIONS = [

    // ── MISIÓN 1: NEGOCIOS DIGITALES ──────────────────────────────────────
    {
      id: 'q6', mission: 'M1',
      difficulty: 'media', points: 100,
      text: 'Una empresa vende productos directamente a consumidores mediante su página web. ¿Qué modelo de negocio representa mejor esta operación?',
      options: [
        { id: 'A', text: 'B2B — Business to Business' },
        { id: 'B', text: 'B2C — Business to Consumer' },
        { id: 'C', text: 'C2C — Consumer to Consumer' },
      ],
      correctId: 'B',
      explanation: 'B2C (Business to Consumer) describe cuando una empresa vende directamente al consumidor final a través de canales digitales como su propia página web.',
      concept: 'Modelo B2C'
    },
    {
      id: 'q7', mission: 'M1',
      difficulty: 'media', points: 100,
      text: 'Una empresa que fabrica uniformes vende grandes cantidades directamente a otras empresas mediante una plataforma digital. ¿Qué modelo de negocio corresponde?',
      options: [
        { id: 'A', text: 'B2C — venta directa al consumidor' },
        { id: 'B', text: 'C2C — consumidor a consumidor' },
        { id: 'C', text: 'B2B — empresa a empresa' },
      ],
      correctId: 'C',
      explanation: 'B2B (Business to Business) se aplica cuando una empresa vende productos o servicios a otras empresas, no al consumidor final.',
      concept: 'Modelo B2B'
    },
    {
      id: 'q15', mission: 'M1',
      difficulty: 'media', points: 100,
      text: 'Una persona tiene una idea para vender productos personalizados por internet, pero no sabe si existe suficiente demanda. ¿Qué debería hacer antes de invertir mucho dinero?',
      options: [
        { id: 'A', text: 'Comprar miles de productos inmediatamente para tener inventario' },
        { id: 'B', text: 'Investigar el mercado y validar la idea con clientes potenciales' },
        { id: 'C', text: 'Crear el logotipo y considerar terminado el proyecto' },
      ],
      correctId: 'B',
      explanation: 'La validación de mercado es el primer paso del emprendimiento digital. Investiga antes de invertir para confirmar que existe demanda real por tu producto.',
      concept: 'Validación de Mercado'
    },
    {
      id: 'q16', mission: 'M1',
      difficulty: 'media', points: 100,
      text: 'Una empresa vende sus productos a través de una plataforma donde también venden cientos de otros negocios (como Amazon o Mercado Libre). ¿Qué tipo de plataforma está utilizando?',
      options: [
        { id: 'A', text: 'Marketplace — plataforma multivendedor' },
        { id: 'B', text: 'ERP — sistema de planificación empresarial' },
        { id: 'C', text: 'CRM — gestión de relaciones con clientes' },
      ],
      correctId: 'A',
      explanation: 'Un Marketplace es una plataforma digital donde múltiples vendedores ofrecen sus productos. Ejemplos: Amazon, Mercado Libre, Etsy.',
      concept: 'Marketplace'
    },

    // ── MISIÓN 2: MARKETING DIGITAL ──────────────────────────────────────
    {
      id: 'q1', mission: 'M2',
      difficulty: 'media', points: 100,
      text: 'Una tienda en línea recibe mucho tráfico desde Instagram, pero muy pocas personas terminan comprando. ¿Qué debería analizar primero un profesional de Comercio Electrónico?',
      options: [
        { id: 'A', text: 'El color y estilo del logotipo de la marca' },
        { id: 'B', text: 'El comportamiento de los usuarios dentro del sitio y el proceso de conversión' },
        { id: 'C', text: 'La cantidad de seguidores de la cuenta de Instagram' },
      ],
      correctId: 'B',
      explanation: 'Tener tráfico sin conversiones indica un problema en el embudo de ventas. Hay que analizar en qué paso abandonan los usuarios usando herramientas de analítica web.',
      concept: 'Tasa de Conversión'
    },
    {
      id: 'q9', mission: 'M2',
      difficulty: 'media', points: 100,
      text: 'Una tienda quiere aparecer entre los primeros resultados cuando alguien busca en Google un producto que vende. ¿Qué estrategia debería dominar un profesional de Comercio Electrónico?',
      options: [
        { id: 'A', text: 'SEO — Optimización para Motores de Búsqueda' },
        { id: 'B', text: 'CRM — Gestión de Relaciones con el Cliente' },
        { id: 'C', text: 'ERP — Sistema de Planificación de Recursos' },
      ],
      correctId: 'A',
      explanation: 'SEO (Search Engine Optimization) consiste en optimizar el contenido y la estructura del sitio para aparecer en los primeros resultados orgánicos de Google.',
      concept: 'SEO'
    },
    {
      id: 'q10', mission: 'M2',
      difficulty: 'media', points: 100,
      text: 'Una empresa quiere registrar las compras anteriores de sus clientes para ofrecerles productos relacionados posteriormente y mejorar su experiencia. ¿Qué sistema puede ayudarle?',
      options: [
        { id: 'A', text: 'CRM — Customer Relationship Management' },
        { id: 'B', text: 'Editor de imágenes tipo Photoshop' },
        { id: 'C', text: 'Sistema operativo del servidor' },
      ],
      correctId: 'A',
      explanation: 'Un CRM gestiona toda la información de clientes: historial de compras, preferencias y comunicaciones, permitiendo personalizar la experiencia y fidelizarlos.',
      concept: 'CRM'
    },
    {
      id: 'q14', mission: 'M2',
      difficulty: 'difícil', points: 150,
      text: 'Una tienda recibe 10,000 visitantes al mes, pero solo 100 realizan una compra. Un especialista quiere mejorar este indicador. ¿Qué KPI está analizando?',
      options: [
        { id: 'A', text: 'Tasa de conversión (Conversion Rate)' },
        { id: 'B', text: 'Número total de empleados del negocio' },
        { id: 'C', text: 'Tamaño físico del almacén de inventario' },
      ],
      correctId: 'A',
      explanation: 'La tasa de conversión = (ventas / visitantes) × 100. En este caso es 1%. Un benchmark saludable en e-commerce es entre 2% y 4%.',
      concept: 'Tasa de Conversión'
    },

    // ── MISIÓN 3: TECNOLOGÍA Y DESARROLLO ────────────────────────────────
    {
      id: 'q4', mission: 'M3',
      difficulty: 'difícil', points: 150,
      text: 'Una tienda tiene miles de clientes y necesita almacenar nombres, correos, pedidos y productos comprados para consultarlos de forma eficiente. ¿Qué conocimiento es especialmente importante?',
      options: [
        { id: 'A', text: 'Bases de datos relacionales (SQL)' },
        { id: 'B', text: 'Fotografía comercial de producto' },
        { id: 'C', text: 'Diseño de empaques físicos' },
      ],
      correctId: 'A',
      explanation: 'Las bases de datos relacionales (MySQL, PostgreSQL) son fundamentales para almacenar y consultar eficientemente la información de clientes, pedidos e inventario.',
      concept: 'Bases de Datos'
    },
    {
      id: 'q5', mission: 'M3',
      difficulty: 'difícil', points: 150,
      text: 'Una empresa quiere que el carrito actualice automáticamente el precio cuando el cliente cambia la cantidad de productos, sin recargar la página. ¿Qué área se encarga principalmente de esto?',
      options: [
        { id: 'A', text: 'Programación y desarrollo web (JavaScript frontend)' },
        { id: 'B', text: 'Mercadotecnia tradicional en medios impresos' },
        { id: 'C', text: 'Logística de almacén y gestión de inventario' },
      ],
      correctId: 'A',
      explanation: 'Esta funcionalidad se implementa con JavaScript en el frontend, manipulando el DOM en tiempo real para actualizar precios, subtotales y totales sin recargar la página.',
      concept: 'Desarrollo Frontend'
    },
    {
      id: 'q18', mission: 'M3',
      difficulty: 'difícil', points: 150,
      text: 'Una tienda recibe cientos de pedidos diariamente y quiere que, al confirmar una compra, el sistema envíe automáticamente un correo al cliente y actualice el inventario. ¿Qué concepto está aplicando?',
      options: [
        { id: 'A', text: 'Automatización de procesos empresariales' },
        { id: 'B', text: 'Publicidad impresa en catálogos físicos' },
        { id: 'C', text: 'Diseño editorial y maquetación gráfica' },
      ],
      correctId: 'A',
      explanation: 'La automatización de procesos reduce errores humanos y tiempo operativo. Herramientas como Zapier, webhooks o flujos de trabajo en el backend permiten estas acciones automáticas.',
      concept: 'Automatización'
    },
    {
      id: 'q19', mission: 'M3',
      difficulty: 'extremo', points: 200,
      text: 'Una tienda quiere conectar su página web con el sistema de inventario y con una empresa de paquetería para que los datos de los pedidos se transfieran automáticamente entre sistemas. ¿Qué tecnología es clave?',
      options: [
        { id: 'A', text: 'Integración de sistemas mediante APIs (REST o SOAP)' },
        { id: 'B', text: 'Fotografía de producto con cámara profesional' },
        { id: 'C', text: 'Diseño de logotipos y branding visual' },
      ],
      correctId: 'A',
      explanation: 'Las APIs permiten que diferentes sistemas se comuniquen entre sí. Una API REST conecta la tienda con inventario, paqueterías (FedEx, DHL) y pasarelas de pago de forma segura.',
      concept: 'APIs e Integración'
    },

    // ── MISIÓN 4: LOGÍSTICA Y OPERACIONES ────────────────────────────────
    {
      id: 'q8', mission: 'M4',
      difficulty: 'difícil', points: 150,
      text: 'Un cliente realiza una compra por internet. El producto debe salir del almacén, ser preparado, empaquetado, entregado por paquetería y confirmado. ¿Qué área coordina principalmente este proceso?',
      options: [
        { id: 'A', text: 'Logística y cadena de suministro (Supply Chain)' },
        { id: 'B', text: 'Diseño UX y experiencia de usuario' },
        { id: 'C', text: 'Publicidad en redes sociales y medios digitales' },
      ],
      correctId: 'A',
      explanation: 'La logística en e-commerce incluye: almacenamiento, picking, packing, envío, rastreo y devoluciones. Es clave para satisfacer al cliente y controlar costos.',
      concept: 'Logística E-Commerce'
    },
    {
      id: 'q17', mission: 'M4',
      difficulty: 'extremo', points: 200,
      text: 'Una empresa mexicana quiere comenzar a vender productos a clientes de Estados Unidos y Europa. ¿Qué aspectos debe considerar además de crear una página web en inglés?',
      options: [
        { id: 'A', text: 'Logística internacional, métodos de pago locales, impuestos, regulaciones aduanales y diferencias culturales de consumo' },
        { id: 'B', text: 'Únicamente cambiar el idioma del botón de compra a inglés' },
        { id: 'C', text: 'Solamente aumentar el precio de los productos un 20%' },
      ],
      correctId: 'A',
      explanation: 'El comercio internacional requiere: cumplimiento aduanal, Incoterms, métodos de pago por región (Klarna en Europa, Apple Pay en EUA), regulaciones de privacidad (GDPR) y logística transfronteriza.',
      concept: 'Comercio Internacional'
    },
    {
      id: 'qX1', mission: 'M4',
      difficulty: 'difícil', points: 150,
      text: 'Una tienda en línea tiene un alto porcentaje de devoluciones. Los clientes dicen que el producto recibido no coincide con las fotos del sitio. ¿Cuál es la mejor acción para reducir este problema?',
      options: [
        { id: 'A', text: 'Eliminar la política de devoluciones del sitio' },
        { id: 'B', text: 'Mejorar las descripciones, fotos 360° y reseñas verificadas de clientes' },
        { id: 'C', text: 'Bajar los precios para compensar las devoluciones' },
      ],
      correctId: 'B',
      explanation: 'El 30% de los productos comprados online se devuelven. Mejorar la información del producto (fotos precisas, descripciones detalladas, tallas exactas) reduce las expectativas incorrectas.',
      concept: 'Logística Inversa'
    },

    // ── MISIÓN 5: DATOS Y SEGURIDAD ──────────────────────────────────────
    {
      id: 'q3', mission: 'M5',
      difficulty: 'media', points: 100,
      text: 'Una empresa quiere saber qué productos generan más ventas, cuándo compran sus clientes y qué categorías tienen mayor demanda para tomar mejores decisiones. ¿Qué área resulta más útil?',
      options: [
        { id: 'A', text: 'Analítica de datos e inteligencia de negocios' },
        { id: 'B', text: 'Diseño gráfico y fotografía de producto exclusivamente' },
        { id: 'C', text: 'Atención al cliente por teléfono' },
      ],
      correctId: 'A',
      explanation: 'La analítica de datos permite tomar decisiones basadas en evidencia: qué productos impulsar, cuándo hacer campañas, qué clientes retener y qué inventario mantener.',
      concept: 'Analítica de Datos'
    },
    {
      id: 'q11', mission: 'M5',
      difficulty: 'difícil', points: 150,
      text: 'Una tienda almacena tarjetas de crédito, datos personales y realiza pagos por internet. Un atacante intenta acceder a su base de datos. ¿Por qué es crítica la ciberseguridad en e-commerce?',
      options: [
        { id: 'A', text: 'Protege información sensible y previene fraudes, pérdidas financieras y daño a la reputación' },
        { id: 'B', text: 'Porque hace que los productos sean más baratos automáticamente' },
        { id: 'C', text: 'Porque aumenta el número de visitas al sitio web' },
      ],
      correctId: 'A',
      explanation: 'Un breach de seguridad puede costar millones y destruir la confianza. Estándares como PCI DSS son obligatorios para tiendas que procesan pagos con tarjeta.',
      concept: 'Ciberseguridad'
    },
    {
      id: 'q12', mission: 'M5',
      difficulty: 'extremo', points: 200,
      text: 'Una tienda analiza sus datos y descubre que el 78% de sus compradores tiene entre 18 y 28 años y usa exclusivamente dispositivos móviles. ¿Cuál sería la decisión estratégica más efectiva?',
      options: [
        { id: 'A', text: 'Ignorar los datos porque todos los clientes compran de la misma manera' },
        { id: 'B', text: 'Optimizar la experiencia móvil (UX responsive, velocidad, checkout simplificado) y dirigir campañas a ese segmento' },
        { id: 'C', text: 'Eliminar la app móvil y vender exclusivamente en tienda física' },
      ],
      correctId: 'B',
      explanation: 'El marketing basado en datos (Data-Driven Marketing) permite personalizar estrategias. Optimizar para mobile-first cuando el 78% de ventas viene de móviles es una decisión de alto impacto.',
      concept: 'Segmentación de Datos'
    },

    // ── MISIÓN 6: EXPERIENCIA DIGITAL ────────────────────────────────────
    {
      id: 'q2', mission: 'M6',
      difficulty: 'media', points: 100,
      text: 'Una tienda tiene buenos productos y precios competitivos, pero los clientes abandonan porque no encuentran el botón de compra. ¿Qué área del comercio electrónico está relacionada directamente con este problema?',
      options: [
        { id: 'A', text: 'UX — Experiencia de Usuario (User Experience)' },
        { id: 'B', text: 'Contabilidad fiscal y declaración de impuestos' },
        { id: 'C', text: 'Administración de inventarios y bodega' },
      ],
      correctId: 'A',
      explanation: 'UX (User Experience) diseña el recorrido del usuario para que sea intuitivo. Si el usuario no encuentra el botón de compra, la UX está fallando y se pierden ventas.',
      concept: 'UX Design'
    },
    {
      id: 'q13', mission: 'M6',
      difficulty: 'media', points: 100,
      text: 'Un diseñador está trabajando en la distribución de botones, jerarquía visual, tipografías, paleta de colores e imágenes de una tienda online para que sea más atractiva. ¿Con qué concepto se relaciona principalmente?',
      options: [
        { id: 'A', text: 'UI — Interfaz de Usuario (User Interface)' },
        { id: 'B', text: 'Logística inversa y gestión de devoluciones' },
        { id: 'C', text: 'Comercio exterior e importaciones' },
      ],
      correctId: 'A',
      explanation: 'UI (User Interface) se enfoca en el diseño visual: cómo se ve la interfaz. UX se enfoca en cómo funciona. Ambas disciplinas son esenciales en e-commerce.',
      concept: 'UI Design'
    },
    {
      id: 'q20', mission: 'M6',
      difficulty: 'extremo', points: 200,
      text: 'Una empresa busca un profesional que pueda diseñar su tienda, analizar datos de ventas, proponer estrategias digitales, entender al cliente y coordinar logística. ¿Qué perfil describe a un egresado de Comercio Electrónico?',
      options: [
        { id: 'A', text: 'Una persona especializada únicamente en publicaciones para redes sociales' },
        { id: 'B', text: 'Una persona que combina negocios, tecnología, marketing, análisis de datos y operación digital' },
        { id: 'C', text: 'Una persona dedicada exclusivamente a reparar computadoras y dar soporte técnico' },
      ],
      correctId: 'B',
      explanation: 'El perfil de Comercio Electrónico es multidisciplinario: negocios digitales, marketing, tecnología, logística y analítica. Es uno de los perfiles más demandados en la economía digital.',
      concept: 'Perfil Profesional'
    },

  ];

  // ─────────────────────────────────────────────
  // DEFINICIÓN DE LAS 6 MISIONES
  // ─────────────────────────────────────────────

  const MISSIONS_META = [
    { id: 'M1', icon: '💼', name: 'Negocios Digitales',    topic: 'Modelos de negocio y emprendimiento', difficulty: 'MEDIA',   color: '#FF6B35' },
    { id: 'M2', icon: '📱', name: 'Marketing Digital',     topic: 'SEO, conversión y fidelización',      difficulty: 'MEDIA',   color: '#FF6B35' },
    { id: 'M3', icon: '💻', name: 'Tecnología',            topic: 'Programación, APIs y bases de datos', difficulty: 'DIFÍCIL', color: '#FF1744' },
    { id: 'M4', icon: '🚚', name: 'Logística',             topic: 'Supply chain y comercio internacional', difficulty: 'DIFÍCIL', color: '#FF1744' },
    { id: 'M5', icon: '📊', name: 'Datos y Seguridad',     topic: 'Analítica, ciberseguridad y datos',   difficulty: 'DIFÍCIL', color: '#FF1744' },
    { id: 'M6', icon: '🛒', name: 'Experiencia Digital',   topic: 'UX, UI y perfil profesional',         difficulty: 'EXTREMO', color: '#C77DFF' },
  ];

  // ─────────────────────────────────────────────
  // UTILIDADES
  // ─────────────────────────────────────────────

  /** Mezcla un array (Fisher-Yates) */
  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  /**
   * Toma una pregunta y devuelve una copia con las opciones mezcladas.
   * La propiedad correctId se actualiza para apuntar al nuevo id de la opción correcta.
   */
  function shuffleOptions(question) {
    const originalCorrectText = question.options.find(o => o.id === question.correctId).text;
    const shuffled = shuffle(question.options).map((opt, i) => ({
      ...opt,
      id: String.fromCharCode(65 + i), // A, B, C, D…
    }));
    const newCorrectId = shuffled.find(o => o.text === originalCorrectText).id;
    return { ...question, options: shuffled, correctId: newCorrectId };
  }

  /**
   * Devuelve las preguntas de una misión dada, con opciones mezcladas.
   * @param {string} missionId — 'M1'..'M6'
   */
  function getQuestionsForMission(missionId) {
    return ALL_QUESTIONS
      .filter(q => q.mission === missionId)
      .map(shuffleOptions);
  }

  /**
   * Selecciona N misiones aleatorias de las 6 disponibles.
   * Cada misión incluye su metadata + preguntas mezcladas.
   * @param {number} n — cuántas misiones (por defecto 3 para partida de 5 min)
   */
  function getRandomMissions(n = 3) {
    const shuffledMeta = shuffle(MISSIONS_META).slice(0, n);
    return shuffledMeta.map(meta => ({
      ...meta,
      questions: getQuestionsForMission(meta.id),
    }));
  }

  /**
   * Devuelve TODAS las misiones con sus preguntas mezcladas.
   */
  function getAllMissions() {
    return MISSIONS_META.map(meta => ({
      ...meta,
      questions: getQuestionsForMission(meta.id),
    }));
  }

  // ─────────────────────────────────────────────
  // SISTEMA DE PUNTUACIÓN
  // ─────────────────────────────────────────────

  const SCORING = {
    CORRECT_FAST:    150,  // < 10s
    CORRECT_NORMAL:  100,  // 10-25s
    CORRECT_SLOW:     75,  // > 25s
    INCORRECT:       -50,
    TIMEOUT:        -100,
    STREAK_3:        +50,  // bonus por racha de 3
    STREAK_5:       +100,  // bonus por racha de 5
    MIN_SCORE:         0,  // no puede ser negativo
  };

  /**
   * Calcula los puntos obtenidos por una respuesta.
   * @param {boolean} correct
   * @param {boolean} timeout
   * @param {number} timeTakenMs — milisegundos tardados
   * @param {number} streakCount — racha actual de correctas
   * @param {number} currentScore — puntuación actual
   */
  function calculatePoints(correct, timeout, timeTakenMs, streakCount, currentScore) {
    let delta = 0;

    if (timeout) {
      delta = SCORING.TIMEOUT;
    } else if (!correct) {
      delta = SCORING.INCORRECT;
    } else {
      const secs = timeTakenMs / 1000;
      if (secs < 10)      delta = SCORING.CORRECT_FAST;
      else if (secs < 25) delta = SCORING.CORRECT_NORMAL;
      else                delta = SCORING.CORRECT_SLOW;

      // Bonus por racha
      if (streakCount + 1 >= 5)      delta += SCORING.STREAK_5;
      else if (streakCount + 1 >= 3) delta += SCORING.STREAK_3;
    }

    return Math.max(SCORING.MIN_SCORE, currentScore + delta) - currentScore;
  }

  // ─────────────────────────────────────────────
  // EXPORTAR
  // ─────────────────────────────────────────────

  window.QuestionBank = {
    ALL_QUESTIONS,
    MISSIONS_META,
    SCORING,
    shuffle,
    shuffleOptions,
    getQuestionsForMission,
    getRandomMissions,
    getAllMissions,
    calculatePoints,
  };

})();
