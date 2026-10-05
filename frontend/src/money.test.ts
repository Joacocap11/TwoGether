// @vitest-environment jsdom
// api.ts reads `localStorage` at module load time (access-token bootstrap), hence jsdom here.
import { describe, expect, it } from 'vitest';
import { parseMoney, moneyToApi, formatMoney } from './api';

describe('parseMoney', () => {
  it('treats a bare integer as whole pesos, not cents ("1950" -> 1950.00)', () => {
    expect(parseMoney('1950')).toBe(1950_00n);
  });
  it('accepts comma as the decimal separator', () => {
    expect(parseMoney('1950,50')).toBe(1950_50n);
  });
  it('accepts dot as the decimal separator', () => {
    expect(parseMoney('1950.50')).toBe(1950_50n);
  });
  it('parses zero', () => {
    expect(parseMoney('0')).toBe(0n);
  });
  it('pads a single decimal digit after the separator', () => {
    expect(parseMoney('0,50')).toBe(50n);
    expect(parseMoney('19,5')).toBe(1950n);
  });
  it('passes bigint input through unchanged (already-computed cents, e.g. a summed total)', () => {
    expect(parseMoney(195000n)).toBe(195000n);
  });
  it('returns null for empty/missing input', () => {
    expect(parseMoney('')).toBeNull();
    expect(parseMoney(null)).toBeNull();
    expect(parseMoney(undefined)).toBeNull();
  });
});

describe('moneyToApi', () => {
  it('serializes whole pesos with two decimals for the backend', () => {
    expect(moneyToApi('1950')).toBe('1950.00');
  });
  it('serializes an explicit decimal unchanged', () => {
    expect(moneyToApi('1950,50')).toBe('1950.50');
  });
});

describe('formatMoney', () => {
  it('formats whole pesos with es-UY grouping and two decimals', () => {
    expect(formatMoney('1950', 'UYU')).toBe('UYU 1.950,00');
  });
  it('formats USD with two decimals', () => {
    expect(formatMoney(25.5, 'USD')).toBe('USD 25,50');
  });
  it('does not double-convert an already-summed bigint total (restaurant "Total" fields)', () => {
    const totalCents = ['1950', '0', '0'].reduce((sum: bigint, v) => sum + (parseMoney(v) || 0n), 0n);
    expect(formatMoney(totalCents, 'UYU')).toBe('UYU 1.950,00');
  });
});
