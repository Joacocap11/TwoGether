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

export type AstroPlacementKey = 'sun' | 'moon' | 'ascendant' | 'mercury' | 'venus' | 'mars';

export interface AstroPlacement {
  key: AstroPlacementKey;
  icon: string;
  label: string;
  subtitle: string;
  joaco: AstroSign;
  selena: AstroSign;
  traits: {
    joaco: string[];
    selena: string[];
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
