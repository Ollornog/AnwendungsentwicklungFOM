// Tolerantes Parsen von Geldbetraegen aus Texteingaben.
//
// Hintergrund: `<input type="number">` laesst den Browser den Wert nach
// dessen Locale interpretieren. Auf deutschen Systemen wird "1.000" als
// Tausender gelesen und als 1 weitergereicht – der Nutzer meinte aber
// 1000. Deshalb verwenden die Preis-Felder `type="text"` und parsen den
// Roh-String hier selbst.
//
// Regel (vom Team festgelegt):
//   - Punkte UND Kommas gelten grundsaetzlich als Tausendertrenner und
//     werden entfernt.
//   - Ausnahme: stehen rechts vom *letzten* Trenner genau zwei Ziffern,
//     wird dieser Trenner als Dezimaltrenner gewertet (Cent-Betrag).
//
// Beispiele:
//   "1.000"      -> 1000      (Punkt, 3 Stellen rechts -> Tausender)
//   "1.000,50"   -> 1000.5    (Komma + 2 Stellen -> Dezimal, Punkt raus)
//   "1,000.50"   -> 1000.5    (Punkt + 2 Stellen -> Dezimal, Komma raus)
//   "9,99"       -> 9.99      (Komma + 2 Stellen -> Dezimal)
//   "10.50"      -> 10.5      (Punkt + 2 Stellen -> Dezimal)
//   "1.234.567"  -> 1234567
//   ""           -> null
(function () {
  // Liefert eine Number oder null (leere/unparsbare Eingabe).
  function parsePrice(raw) {
    if (raw === null || raw === undefined) return null;
    // Echte Zahlen (z. B. aus der API beim Bearbeiten) sind exakt – nur
    // getippte Strings brauchen die Trenner-Heuristik.
    if (typeof raw === 'number') {
      return Number.isFinite(raw) ? raw : null;
    }
    let s = String(raw).trim();
    if (s === '') return null;

    // Vorzeichen merken, dann nur Ziffern und Trenner behalten.
    const negative = s.startsWith('-');
    s = s.replace(/[^\d.,]/g, '');
    if (s === '') return null;

    const lastSep = Math.max(s.lastIndexOf('.'), s.lastIndexOf(','));
    let result;
    if (lastSep === -1) {
      result = Number(s);
    } else {
      const fraction = s.slice(lastSep + 1);
      if (/^\d{2}$/.test(fraction)) {
        // Letzter Trenner ist Dezimaltrenner: restliche Trenner entfernen.
        const integerPart = s.slice(0, lastSep).replace(/[.,]/g, '');
        result = Number((integerPart || '0') + '.' + fraction);
      } else {
        // Alle Trenner sind Tausendertrenner.
        result = Number(s.replace(/[.,]/g, ''));
      }
    }

    if (!Number.isFinite(result)) return null;
    return negative ? -result : result;
  }

  // Ganzzahlige Mengen (Lager, Nachfrage): Trenner sind hier immer
  // Tausendertrenner. Liefert eine Number (Ganzzahl) oder null.
  function parseQuantity(raw) {
    const value = parsePrice(raw);
    if (value === null) return null;
    return Math.round(value);
  }

  window.parsePrice = parsePrice;
  window.parseQuantity = parseQuantity;
})();
