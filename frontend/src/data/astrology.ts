// Static content for the "Carta Astral" comparison between Joaco and Selena.
// Positions are fixed and were provided/approved by them — this is not a
// calculator, so nothing here is derived or computed at runtime.
//
// Kept isolated from presentation (main.tsx / astro.tsx) so the page component
// stays focused on layout/markup and this dataset can be reviewed or edited on
// its own. Mirrored (duplicated, not shared) at mobile/src/data/astrology.ts —
// two small independent Expo/Vite projects, so a real shared package would add
// build complexity for a dataset this small.

export type PersonTone = 'joaco' | 'selena';

export interface AstroPerson {
  name: string;
  tone: PersonTone;
}

export const astroPeople: Record<PersonTone, AstroPerson> = {
  joaco: { name: 'Joaco', tone: 'joaco' },
  selena: { name: 'Selena', tone: 'selena' },
};

export interface AstroSign {
  sign: string;
  symbol: string;
}

export type AstroPlacementKey =
  | 'sun'
  | 'moon'
  | 'ascendant'
  | 'mercury'
  | 'venus'
  | 'mars'
  | 'jupiter'
  | 'saturn'
  | 'uranus'
  | 'neptune'
  | 'pluto';

export interface AstroPlacement {
  key: AstroPlacementKey;
  icon: string;
  label: string;
  subtitle: string;
  /** Significado general del planeta; se muestra en el accordion antes de los rasgos. */
  meaning?: string;
  /** Los 5 planetas exteriores usan contenido más compacto para no restar foco a los 6 principales. */
  compact?: boolean;
  joaco: AstroSign;
  selena: AstroSign;
  traits: {
    joaco?: string[];
    selena?: string[];
    /** Cuando Joaco y Selena comparten signo (Neptuno, Plutón), se listan rasgos en común en vez de dos columnas. */
    shared?: string[];
  };
  dynamic: string;
}

export const astroPlacements: AstroPlacement[] = [
  {
    key: 'sun',
    icon: '☀',
    label: 'Sol',
    subtitle: 'Identidad',
    joaco: { sign: 'Cáncer', symbol: '♋' },
    selena: { sign: 'Libra', symbol: '♎' },
    traits: {
      selena: ['Equilibrio', 'Buen trato', 'Diálogo', 'Cooperación', 'Considerar ambas partes'],
      joaco: ['Seguridad emocional', 'Cercanía', 'Lealtad', 'Contención', 'Sentir la relación como lugar seguro'],
    },
    dynamic:
      'Los dos están orientados al vínculo, pero Selena puede buscar resolver desde el equilibrio y Joaco puede necesitar primero sentirse comprendido emocionalmente.',
  },
  {
    key: 'moon',
    icon: '☾',
    label: 'Luna',
    subtitle: 'Mundo emocional',
    joaco: { sign: 'Escorpio', symbol: '♏' },
    selena: { sign: 'Géminis', symbol: '♊' },
    traits: {
      selena: ['Procesa emociones hablando, preguntando y cambiando de perspectiva', 'Puede necesitar aire, humor o distracción'],
      joaco: ['Procesa profundamente', 'Necesita entender qué pasó y qué significa', 'No siempre puede cambiar rápidamente de tema'],
    },
    dynamic:
      'Selena puede sentir que Joaco vuelve demasiado sobre un tema; Joaco puede sentir que Selena lo toma con poca profundidad. No significa que uno sienta más: sienten/procesan distinto.',
  },
  {
    key: 'ascendant',
    icon: '↑',
    label: 'Ascendente',
    subtitle: 'Cómo nos mostramos',
    joaco: { sign: 'Piscis', symbol: '♓' },
    selena: { sign: 'Tauro', symbol: '♉' },
    traits: {
      selena: ['Estabilidad', 'Calma', 'Firmeza'],
      joaco: ['Sensibilidad', 'Flexibilidad', 'Intuición'],
    },
    dynamic:
      'Tauro puede dar estructura a Piscis; Piscis puede suavizar y sensibilizar a Tauro. Puede existir afinidad por comodidad, tranquilidad, intimidad y afecto.',
  },
  {
    key: 'mercury',
    icon: '☿',
    label: 'Mercurio',
    subtitle: 'Comunicación',
    joaco: { sign: 'Cáncer', symbol: '♋' },
    selena: { sign: 'Libra', symbol: '♎' },
    traits: {
      selena: ['Busca palabras justas', 'Equilibrio', 'Negociación'],
      joaco: ['Comunica desde la experiencia personal', 'Registra mucho el impacto emocional y el tono'],
    },
    dynamic:
      'Funciona mejor si Selena valida la emoción antes de analizar y Joaco explica lo que necesita sin asumir intenciones.',
  },
  {
    key: 'venus',
    icon: '♀',
    label: 'Venus',
    subtitle: 'Cómo amamos',
    joaco: { sign: 'Géminis', symbol: '♊' },
    selena: { sign: 'Escorpio', symbol: '♏' },
    traits: {
      selena: ['Intensidad', 'Exclusividad', 'Profundidad', 'Confianza', 'Lealtad'],
      joaco: ['Comunicación', 'Humor', 'Curiosidad', 'Complicidad mental', 'Movimiento'],
    },
    dynamic:
      'Selena aporta profundidad y compromiso. Joaco aporta conversación, juego y frescura. La Venus en Géminis de Joaco conecta bien con la Luna en Géminis de Selena, favoreciendo conversación, humor, códigos propios y amistad dentro de la pareja.',
  },
  {
    key: 'mars',
    icon: '♂',
    label: 'Marte',
    subtitle: 'Acción, impulso y deseo',
    joaco: { sign: 'Leo', symbol: '♌' },
    selena: { sign: 'Virgo', symbol: '♍' },
    traits: {
      selena: ['Acción medida', 'Práctica', 'Detallista', 'Demostrar interés ayudando u organizando'],
      joaco: ['Expresividad', 'Impulso', 'Orgullo', 'Espontaneidad', 'Necesidad de reconocimiento'],
    },
    dynamic:
      'Joaco aporta fuego y espontaneidad. Selena aporta atención y precisión. Durante conflictos, las correcciones/detalles pueden tocar el orgullo de Joaco y la intensidad de Joaco puede resultarle excesiva a Selena.',
  },

  {
    key: 'jupiter',
    icon: '♃',
    label: 'Júpiter',
    subtitle: 'Crecimiento y expansión',
    meaning: 'Júpiter representa crecimiento, expansión, confianza, oportunidades y la manera en que una persona busca desarrollarse.',
    compact: true,
    joaco: { sign: 'Virgo', symbol: '♍' },
    selena: { sign: 'Leo', symbol: '♌' },
    traits: {
      joaco: ['Crece mejorando procesos', 'Atención al detalle', 'Aprender haciendo', 'Utilidad y constancia'],
      selena: ['Crecimiento mediante expresión', 'Creatividad', 'Confianza', 'Visibilidad', 'Generosidad'],
    },
    dynamic:
      'Joaco puede aportar método y precisión; Selena puede aportar confianza, entusiasmo y expresión. Pueden complementarse entre organización y espontaneidad.',
  },
  {
    key: 'saturn',
    icon: '♄',
    label: 'Saturno',
    subtitle: 'Responsabilidad y aprendizajes',
    meaning: 'Saturno representa límites, responsabilidad, estructura, disciplina y aprendizajes de largo plazo.',
    compact: true,
    joaco: { sign: 'Cáncer', symbol: '♋' },
    selena: { sign: 'Géminis', symbol: '♊' },
    traits: {
      joaco: ['Aprendizajes ligados a la seguridad emocional', 'Protección', 'Familia', 'Vulnerabilidad'],
      selena: ['Aprendizajes ligados a la comunicación', 'Claridad', 'Expresión de ideas', 'Organizar pensamientos'],
    },
    dynamic:
      'Joaco puede poner peso emocional en determinadas situaciones; Selena puede analizarlas mentalmente. La relación funciona mejor cuando emoción y comunicación se acompañan.',
  },
  {
    key: 'uranus',
    icon: '♅',
    label: 'Urano',
    subtitle: 'Cambio e independencia',
    meaning: 'Urano representa independencia, cambios inesperados, originalidad, innovación y necesidad de libertad.',
    compact: true,
    joaco: { sign: 'Piscis', symbol: '♓' },
    selena: { sign: 'Acuario', symbol: '♒' },
    traits: {
      joaco: ['Intuición', 'Imaginación', 'Sensibilidad poco convencional', 'Cambios guiados por percepciones internas'],
      selena: ['Independencia fuerte', 'Pensamiento diferente', 'Innovación', 'Necesidad de espacio'],
    },
    dynamic:
      'Los dos pueden necesitar libertad, aunque la expresan distinto: Selena la busca desde las ideas, Joaco desde la sensibilidad e intuición.',
  },
  {
    key: 'neptune',
    icon: '♆',
    label: 'Neptuno',
    subtitle: 'Sensibilidad e ideales',
    meaning: 'Neptuno representa imaginación, sensibilidad, idealismo, fantasía e intuición.',
    compact: true,
    joaco: { sign: 'Acuario', symbol: '♒' },
    selena: { sign: 'Acuario', symbol: '♒' },
    traits: {
      shared: [
        'Idealismo',
        'Imaginación',
        'Interés por posibilidades futuras',
        'Sensibilidad a ideas colectivas',
        'Capacidad para fantasear y proyectar juntos',
      ],
    },
    dynamic:
      'Al compartir Neptuno en Acuario, pueden coincidir bastante en ideales generacionales y en imaginar juntos proyectos, experiencias o futuros posibles. Al ser un planeta lento, esta coincidencia también es generacional y no debe leerse como algo exclusivamente personal.',
  },
  {
    key: 'pluto',
    icon: '♇',
    label: 'Plutón',
    subtitle: 'Transformación e intensidad',
    meaning: 'Plutón representa transformación, intensidad, poder interno y procesos profundos de cambio.',
    compact: true,
    joaco: { sign: 'Sagitario', symbol: '♐' },
    selena: { sign: 'Sagitario', symbol: '♐' },
    traits: {
      shared: [
        'Búsqueda de significado',
        'Transformación mediante experiencias',
        'Cuestionamiento de creencias',
        'Interés por descubrir perspectivas nuevas',
      ],
    },
    dynamic:
      'Comparten una posición generacional asociada a revisar creencias, explorar ideas y transformar la manera de entender el mundo. Plutón es un planeta lento, por lo que esta coincidencia es principalmente generacional.',
  },
];

export interface AstroConnection {
  title: string;
  description: string;
}

export const astroConnections: AstroConnection[] = [
  {
    title: 'Luna de Joaco en Escorpio + Venus de Selena en Escorpio',
    description: 'Conexión emocional e intimidad fuerte.',
  },
  {
    title: 'Venus de Joaco en Géminis + Luna de Selena en Géminis',
    description: 'Conversación, humor, amistad y códigos propios.',
  },
  {
    title: 'Sol de Joaco en Cáncer + Venus de Selena en Escorpio',
    description: 'Afinidad emocional y valoración de la sensibilidad y la lealtad.',
  },
];

export interface DynamicSummaryItem {
  label: string;
  value: string;
}

export const dynamicSummary: DynamicSummaryItem[] = [
  { label: 'Conexión emocional', value: 'Alta' },
  { label: 'Atracción e intimidad', value: 'Muy alta' },
  { label: 'Comunicación cotidiana', value: 'Alta' },
  { label: 'Manejo de conflictos', value: 'Desafiante, pero trabajable' },
  { label: 'Necesidad de seguridad', value: 'Fuerte en ambos' },
  { label: 'Potencial de crecimiento', value: 'Alto' },
];

export const dynamicNarrative = {
  paragraphs: [
    'Joaco aporta profundidad emocional, sensibilidad y protección. Selena aporta equilibrio, estabilidad y perspectiva.',
    'Existe mucha conexión mediante la intimidad, la conversación y la complicidad, pero hay que cuidar la sobreinterpretación emocional.',
    'Cuando Joaco siente distancia puede buscar más seguridad, mientras Selena puede necesitar más aire cuando siente presión.',
  ],
  keyPointsIntro: 'La clave es:',
  keyPoints: [
    'Comunicar necesidades directamente',
    'No interpretar el espacio como desamor',
    'No esperar que el otro adivine',
    'Hablar de hechos y emociones concretas',
  ],
};

export const astroDisclaimer =
  'Esta es una interpretación astrológica simbólica, no una medición científica de compatibilidad. Las posiciones utilizadas fueron calculadas de forma aproximada.';

export interface AstroBirthDetail {
  date: string;
  time: string;
  place: string;
}

// Mostrados de forma discreta ("Datos utilizados"); no se usan para calcular nada en runtime.
export const astroBirthData: Record<PersonTone, AstroBirthDetail> = {
  joaco: { date: '27/06/2004', time: '22:20', place: 'Montevideo, Uruguay' },
  selena: { date: '28/09/2002', time: '20:50', place: 'Montevideo, Uruguay' },
};

export const astroFullChart = {
  title: '¿Querés ver la carta completa?',
  description:
    'Si querés profundizar en casas, grados, aspectos y otros puntos astrológicos, podés consultar una carta natal completa.',
  buttonLabel: 'Ver carta completa',
  // Calculadora externa de carta natal (Astro-Seek) donde cada quien ingresa sus propios
  // datos manualmente. Sin query params con datos personales a propósito.
  url: 'https://horoscopes.astro-seek.com/birth-chart-horoscope-online',
};
