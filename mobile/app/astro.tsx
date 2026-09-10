import React, { useState } from 'react';
import { Linking, LayoutAnimation, Platform, Pressable, ScrollView, StyleSheet, Text, UIManager, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, colors } from '../src/ui';
import {
  astroBirthData,
  astroConnections,
  astroDisclaimer,
  astroFullChart,
  astroPeople,
  astroPlacements,
  dynamicNarrative,
  dynamicSummary,
  AstroPlacement,
} from '../src/data/astrology';

// LayoutAnimation is a core React Native JS API (no native module/build step
// required); enabling it on Android is a runtime call, not a native change,
// so this stays safe for an OTA update.
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export default function Astro() {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Carta Astral</Text>
      <Text style={styles.subtitle}>Cómo se combinan las cartas de Joaco y Selena, signo por signo.</Text>

      <View style={[styles.card, local.birthCard]}>
        <Text style={local.birthTitle}>Datos utilizados</Text>
        {(Object.keys(astroPeople) as (keyof typeof astroPeople)[]).map(tone => (
          <Text key={tone} style={local.birthItem}>
            <Text style={{ fontWeight: '800', color: tone === 'joaco' ? colors.yellow : colors.blue }}>
              {astroPeople[tone].name}
            </Text>{' '}
            · {astroBirthData[tone].date} · {astroBirthData[tone].time} · {astroBirthData[tone].place}
          </Text>
        ))}
      </View>

      <AstroTable />

      {astroPlacements.map(placement => (
        <AstroAccordionItem key={placement.key} placement={placement} />
      ))}

      <Text style={local.sectionTitle}>Lo que más nos conecta</Text>
      {astroConnections.map(connection => (
        <View key={connection.title} style={[styles.card, local.connectionCard]}>
          <Text style={local.connectionTitle}>{connection.title}</Text>
          <Text style={styles.muted}>{connection.description}</Text>
        </View>
      ))}

      <Text style={local.sectionTitle}>Nuestra dinámica</Text>
      <View style={local.summaryGrid}>
        {dynamicSummary.map(item => (
          <View key={item.label} style={[styles.card, local.summaryItem]}>
            <Text style={local.summaryLabel}>{item.label}</Text>
            <Text style={local.summaryValue}>{item.value}</Text>
          </View>
        ))}
      </View>
      <View style={local.narrative}>
        {dynamicNarrative.paragraphs.map(paragraph => (
          <Text key={paragraph} style={local.paragraph}>
            {paragraph}
          </Text>
        ))}
        <Text style={local.paragraph}>{dynamicNarrative.keyPointsIntro}</Text>
        {dynamicNarrative.keyPoints.map(point => (
          <Text key={point} style={local.bullet}>
            •  {point}
          </Text>
        ))}
      </View>

      <Text style={local.disclaimer}>{astroDisclaimer}</Text>

      <View style={[styles.card, local.fullChartCard]}>
        <Text style={local.fullChartTitle}>{astroFullChart.title}</Text>
        <Text style={local.fullChartDesc}>{astroFullChart.description}</Text>
        <Pressable
          onPress={() => Linking.openURL(astroFullChart.url)}
          accessibilityRole="button"
          style={local.fullChartButton}
        >
          <Text style={local.fullChartButtonLabel}>{astroFullChart.buttonLabel}</Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

function AstroTable() {
  return (
    <View style={[styles.card, local.tableCard]}>
      <View style={local.tableHeaderRow}>
        <Text style={[local.tableHeaderCell, { flex: 1.2 }]}>Elemento</Text>
        <Text style={[local.tableHeaderCell, local.tableHeaderJoaco]}>Joaco</Text>
        <Text style={[local.tableHeaderCell, local.tableHeaderSelena]}>Selena</Text>
      </View>
      {astroPlacements.map(placement => (
        <View key={placement.key} style={local.tableRow}>
          <Text style={[local.tableLabelCell, { flex: 1.2 }]}>
            {placement.icon} {placement.label}
          </Text>
          <Text style={[local.tableValueCell, { color: colors.yellow }]}>
            {placement.joaco.symbol} {placement.joaco.sign}
          </Text>
          <Text style={[local.tableValueCell, { color: colors.blue }]}>
            {placement.selena.symbol} {placement.selena.sign}
          </Text>
        </View>
      ))}
    </View>
  );
}

function AstroAccordionItem({ placement }: { placement: AstroPlacement }) {
  const [open, setOpen] = useState(false);
  function toggle() {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setOpen(current => !current);
  }
  return (
    <Pressable
      onPress={toggle}
      accessibilityRole="button"
      accessibilityState={{ expanded: open }}
      accessibilityLabel={`${placement.label}, ${placement.subtitle}`}
      style={[styles.card, local.accordionCard, placement.compact && local.accordionCardCompact]}
    >
      <View style={local.accordionHeader}>
        <Text style={[local.accordionHeading, placement.compact && local.accordionHeadingCompact]}>
          {placement.icon} {placement.label} — {placement.subtitle}
        </Text>
        <Ionicons name={open ? 'chevron-up' : 'chevron-down'} size={18} color={colors.blue} />
      </View>
      <View style={local.accordionValues}>
        <Text style={[local.accordionValue, { color: colors.yellow }]}>
          {placement.joaco.symbol} {placement.joaco.sign}
        </Text>
        <Text style={[local.accordionValue, { color: colors.blue }]}>
          {placement.selena.symbol} {placement.selena.sign}
        </Text>
      </View>
      {!open && <Text style={local.accordionToggleLabel}>Ver interpretación</Text>}
      {open && (
        <View style={local.accordionBody}>
          {placement.meaning && <Text style={local.accordionMeaning}>{placement.meaning}</Text>}
          {placement.traits.shared ? (
            <View style={local.accordionTraitCol}>
              <Text style={local.accordionTraitTitle}>Rasgos compartidos</Text>
              {placement.traits.shared.map(trait => (
                <Text key={trait} style={local.traitItem}>
                  •  {trait}
                </Text>
              ))}
            </View>
          ) : (
            <View style={local.accordionTraitsRow}>
              <View style={local.accordionTraitCol}>
                <Text style={[local.accordionTraitTitle, { color: colors.yellow }]}>Joaco</Text>
                {(placement.traits.joaco ?? []).map(trait => (
                  <Text key={trait} style={local.traitItem}>
                    •  {trait}
                  </Text>
                ))}
              </View>
              <View style={local.accordionTraitCol}>
                <Text style={[local.accordionTraitTitle, { color: colors.blue }]}>Selena</Text>
                {(placement.traits.selena ?? []).map(trait => (
                  <Text key={trait} style={local.traitItem}>
                    •  {trait}
                  </Text>
                ))}
              </View>
            </View>
          )}
          <Text style={local.accordionDynamic}>
            <Text style={local.accordionDynamicLabel}>Dinámica: </Text>
            {placement.dynamic}
          </Text>
        </View>
      )}
    </Pressable>
  );
}

const local = StyleSheet.create({
  sectionTitle: { color: colors.ink, fontSize: 19, fontWeight: '800', marginTop: 10, marginBottom: 12 },
  tableCard: { padding: 0, overflow: 'hidden' },
  tableHeaderRow: { flexDirection: 'row', backgroundColor: colors.cream, paddingVertical: 10, paddingHorizontal: 14 },
  tableHeaderCell: { flex: 1, fontSize: 11, fontWeight: '800', color: colors.ink, textTransform: 'uppercase', letterSpacing: 0.4 },
  tableHeaderJoaco: { color: colors.yellow },
  tableHeaderSelena: { color: colors.blue },
  tableRow: { flexDirection: 'row', paddingVertical: 10, paddingHorizontal: 14, borderTopWidth: 1, borderTopColor: colors.border },
  tableLabelCell: { flex: 1, fontSize: 13, fontWeight: '700', color: colors.ink },
  tableValueCell: { flex: 1, fontSize: 13, fontWeight: '700' },
  accordionCard: { paddingBottom: 14 },
  accordionHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  accordionHeading: { flex: 1, color: colors.ink, fontSize: 15, fontWeight: '800' },
  accordionValues: { flexDirection: 'row', gap: 16, marginTop: 8 },
  accordionValue: { fontWeight: '700', fontSize: 13 },
  accordionToggleLabel: { marginTop: 8, color: colors.blue, fontWeight: '700', fontSize: 12, textDecorationLine: 'underline' },
  accordionBody: { marginTop: 14, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 14 },
  accordionTraitsRow: { flexDirection: 'row', gap: 18 },
  accordionTraitCol: { flex: 1 },
  accordionTraitTitle: { fontWeight: '800', marginBottom: 6, fontSize: 13 },
  traitItem: { color: colors.muted, fontSize: 12.5, lineHeight: 18 },
  accordionDynamic: { color: colors.muted, fontSize: 13, lineHeight: 19, marginTop: 12 },
  accordionDynamicLabel: { color: colors.ink, fontWeight: '800' },
  connectionCard: { borderLeftWidth: 4, borderLeftColor: colors.yellow },
  connectionTitle: { color: colors.ink, fontWeight: '800', fontSize: 13, marginBottom: 4 },
  summaryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 6 },
  summaryItem: { flexBasis: '47%', flexGrow: 1 },
  summaryLabel: { fontSize: 11, fontWeight: '800', color: colors.muted, textTransform: 'uppercase', letterSpacing: 0.3, marginBottom: 4 },
  summaryValue: { color: colors.ink, fontWeight: '800', fontSize: 14 },
  narrative: { marginTop: 6, marginBottom: 8 },
  paragraph: { color: colors.muted, fontSize: 14, lineHeight: 21, marginBottom: 10 },
  bullet: { color: colors.muted, fontSize: 14, lineHeight: 21, marginLeft: 4, marginBottom: 4 },
  disclaimer: { color: '#9b9187', fontSize: 11, lineHeight: 16, marginTop: 8 },
  birthCard: { backgroundColor: colors.cream, paddingVertical: 10, paddingHorizontal: 14, marginBottom: 4 },
  birthTitle: { fontSize: 11, fontWeight: '800', color: colors.muted, textTransform: 'uppercase', letterSpacing: 0.3, marginBottom: 4 },
  birthItem: { color: colors.ink, fontSize: 13, marginTop: 2 },
  accordionCardCompact: { paddingBottom: 12 },
  accordionHeadingCompact: { fontSize: 14 },
  accordionMeaning: { color: colors.muted, fontSize: 13, lineHeight: 19, marginBottom: 4 },
  fullChartCard: { alignItems: 'flex-start', gap: 4 },
  fullChartTitle: { color: colors.ink, fontSize: 16, fontWeight: '800' },
  fullChartDesc: { color: colors.muted, fontSize: 13, lineHeight: 19, marginBottom: 8 },
  fullChartButton: { backgroundColor: colors.ink, paddingVertical: 10, paddingHorizontal: 18, borderRadius: 8 },
  fullChartButtonLabel: { color: '#fff', fontWeight: '700', fontSize: 14 },
});
