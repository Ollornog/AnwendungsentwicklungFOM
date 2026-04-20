// Sichere(r) Formel-Auswertung fuer die Live-Preview im Browser.
//
// Gleiche Variablen- und Funktions-Whitelist wie der Backend-Evaluator
// (siehe backend/app/strategies/runtime.py und evaluator.py). Regex-Gate
// auf erlaubte Zeichen + Blacklist auf verdaechtige Tokens. Danach
// Function()-Konstruktor mit positional args – der Ausdruck sieht nur
// die durchgereichten Werte.
// Quellen von Ausdruecken sind entweder der Shop-Betreiber selbst oder
// der Backend-LLM-Endpoint, der die Formeln vorher gegencheckt.
(function () {
  // ',' ist noetig fuer min(a, b, c).
  const ALLOWED_CHARS = /^[0-9A-Za-z_+\-*/%.()\s<>!=&|,]*$/;
  const FORBIDDEN_TOKENS = ['__', 'import', 'lambda', '?', ':', ';'];
  const ALLOWED_VARS = [
    'cost_price',
    'competitor_price',
    'monthly_demand',
    'start_stock',
    'stock',
    'hour',
    'day',
    'weekday',
    'demand',
    'pi',
  ];

  // Gleiche Funktionsnamen wie im Backend. JS-Implementation ueber Math.*,
  // round(x, n) optional mit Nachkommastellen – Math.round kann das nicht nativ.
  const FUNCS = {
    sqrt: Math.sqrt,
    pow: Math.pow,
    abs: Math.abs,
    min: Math.min,
    max: Math.max,
    round: (x, n) => {
      const d = Number.isFinite(n) ? Math.pow(10, n) : 1;
      return Math.round(Number(x) * d) / d;
    },
    floor: Math.floor,
    ceil: Math.ceil,
    mod: (x, n) => Number(x) % Number(n),
    sin: Math.sin,
    cos: Math.cos,
  };
  const FUNC_NAMES = Object.keys(FUNCS);
  const FUNC_VALUES = Object.values(FUNCS);

  function evaluateFormula(expression, variables) {
    if (typeof expression !== 'string' || !expression.trim()) {
      throw new Error('Formel ist leer');
    }
    if (!ALLOWED_CHARS.test(expression)) {
      throw new Error('Formel enthält ungültige Zeichen');
    }
    const low = expression.toLowerCase();
    for (const t of FORBIDDEN_TOKENS) {
      if (low.includes(t)) throw new Error(`Formel enthält verbotenes Token: ${t}`);
    }
    // Zuweisungen verbieten: Mehrzeichen-Vergleiche rausstreichen; bleibt '=' uebrig -> nein.
    const stripped = expression.replace(/==|!=|<=|>=/g, '');
    if (stripped.includes('=')) throw new Error('Zuweisungen sind in der Formel nicht erlaubt');

    const values = ALLOWED_VARS.map((name) => {
      const v = variables && variables[name];
      if (v === undefined || v === null || v === '') {
        // `pi` hat einen sinnvollen Default, falls die aufrufende Seite
        // ihn nicht explizit mitgibt.
        return name === 'pi' ? Math.PI : 0;
      }
      const n = Number(v);
      return Number.isFinite(n) ? n : 0;
    });
    // Python-Stil `and` / `or` / `not` in JS-Syntax uebersetzen, damit eine
    // von der KI vorgeschlagene Formel (der Backend-Evaluator kennt ast.BoolOp
    // und erlaubt diese Schluesselwoerter) auch in der Live-Preview laeuft.
    // `\b` stellt sicher, dass Variablen-/Funktionsnamen wie `round` oder
    // `standard` (haette ein "and" als Teilstring) unberuehrt bleiben.
    const jsExpr = expression
      .replace(/\band\b/g, '&&')
      .replace(/\bor\b/g, '||')
      .replace(/\bnot\b/g, '!');
    // Reihenfolge: Funktionen zuerst, dann Variablen (entspricht der Parameter-
    // reihenfolge im new Function-Aufruf).
    const fn = new Function(
      ...FUNC_NAMES,
      ...ALLOWED_VARS,
      `"use strict"; return (${jsExpr});`,
    );
    return fn(...FUNC_VALUES, ...values);
  }

  window.evaluateFormula = evaluateFormula;
  window.ALLOWED_FORMULA_VARS = ALLOWED_VARS;
  window.ALLOWED_FORMULA_FUNCS = FUNC_NAMES;
})();
