import React from 'react';
import {
  astroBirthData,
  astroConnections,
  astroDisclaimer,
  astroFullChart,
  astroPeople,
  astroPlacements,
  dynamicNarrative,
  dynamicSummary,
} from './data/astrology';

export function AstroPage() {
  return (
    <div className="astro-page">
      <div className="title astro-title">
        <div>
          <p className="eyebrow">CARTA ASTRAL</p>
          <h1>Carta Astral</h1>
          <p className="astro-subtitle">Cómo se combinan las cartas de Joaco y Selena, signo por signo.</p>
        </div>
      </div>

      <div className="astro-birth-data">
        <p className="astro-birth-title">Datos utilizados</p>
        <div className="astro-birth-grid">
          {(Object.keys(astroPeople) as (keyof typeof astroPeople)[]).map(tone => (
            <p key={tone} className={`astro-birth-item ${tone}`}>
              <b>{astroPeople[tone].name}</b> · {astroBirthData[tone].date} · {astroBirthData[tone].time} ·{' '}
              {astroBirthData[tone].place}
            </p>
          ))}
        </div>
      </div>

      <table className="astro-table" aria-label="Comparación de posiciones astrológicas">
        <thead>
          <tr>
            <th scope="col">Elemento</th>
            <th scope="col">Joaco</th>
            <th scope="col">Selena</th>
          </tr>
        </thead>
        <tbody>
          {astroPlacements.map(placement => (
            <tr key={placement.key}>
              <td data-label="Elemento">
                <span className="astro-row-label">
                  <span aria-hidden="true">{placement.icon}</span> {placement.label}
                </span>
              </td>
              <td data-label="Joaco">
                <span className="astro-value joaco">
                  {placement.joaco.symbol} {placement.joaco.sign}
                </span>
              </td>
              <td data-label="Selena">
                <span className="astro-value selena">
                  {placement.selena.symbol} {placement.selena.sign}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="astro-accordion">
        {astroPlacements.map(placement => (
          <details key={placement.key} className={`astro-item${placement.compact ? ' compact' : ''}`}>
            <summary>
              <span className="astro-item-heading">
                <span aria-hidden="true">{placement.icon}</span> {placement.label} — {placement.subtitle}
              </span>
              <span className="astro-item-values">
                <span className="astro-value joaco">
                  {placement.joaco.symbol} {placement.joaco.sign}
                </span>
                <span className="astro-value selena">
                  {placement.selena.symbol} {placement.selena.sign}
                </span>
              </span>
              <span className="astro-item-toggle">
                <span className="astro-open-label">Ver interpretación</span>
                <span className="astro-close-label">Ocultar interpretación</span>
              </span>
            </summary>
            <div className="astro-item-body">
              {placement.meaning && <p className="astro-item-meaning">{placement.meaning}</p>}
              {placement.traits.shared ? (
                <div className="astro-item-traits shared">
                  <div className="astro-trait shared">
                    <b>Rasgos compartidos</b>
                    <ul>
                      {placement.traits.shared.map(trait => (
                        <li key={trait}>{trait}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="astro-item-traits">
                  <div className="astro-trait joaco">
                    <b>Joaco</b>
                    <ul>
                      {(placement.traits.joaco ?? []).map(trait => (
                        <li key={trait}>{trait}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="astro-trait selena">
                    <b>Selena</b>
                    <ul>
                      {(placement.traits.selena ?? []).map(trait => (
                        <li key={trait}>{trait}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
              <p className="astro-dynamic">
                <b>Dinámica:</b> {placement.dynamic}
              </p>
            </div>
          </details>
        ))}
      </div>

      <section className="astro-connections">
        <h2>Lo que más nos conecta</h2>
        <div className="astro-connections-grid">
          {astroConnections.map(connection => (
            <article key={connection.title} className="astro-connection-card">
              <p className="astro-connection-title">{connection.title}</p>
              <p className="astro-connection-desc">{connection.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="astro-summary">
        <h2>Nuestra dinámica</h2>
        <div className="astro-summary-grid">
          {dynamicSummary.map(item => (
            <div key={item.label} className="astro-summary-item">
              <span className="astro-summary-label">{item.label}</span>
              <span className="astro-summary-value">{item.value}</span>
            </div>
          ))}
        </div>
        <div className="astro-narrative">
          {dynamicNarrative.paragraphs.map(paragraph => (
            <p key={paragraph}>{paragraph}</p>
          ))}
          <p>{dynamicNarrative.keyPointsIntro}</p>
          <ul>
            {dynamicNarrative.keyPoints.map(point => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </div>
      </section>

      <p className="astro-disclaimer">{astroDisclaimer}</p>

      <section className="astro-full-chart">
        <h2>{astroFullChart.title}</h2>
        <p>{astroFullChart.description}</p>
        <a
          className="astro-full-chart-button"
          href={astroFullChart.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          {astroFullChart.buttonLabel}
        </a>
      </section>
    </div>
  );
}
