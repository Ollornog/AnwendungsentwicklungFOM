// Sichere(r) Formel-Auswertung fuer die Live-Preview im Browser.
//
// Gleiche Variablen-Whitelist wie der Backend-Evaluator (siehe
// backend/app/strategies/runtime.py). Regex-Gate auf erlaubte Zeichen +
// Blacklist auf verdaechtige Tokens. Danach Function()-Konstruktor mit
// positional args – der Ausdruck sieht damit nur die uebergebenen Werte.
// Quellen von Ausdruecken sind entweder der Shop-Betreiber selbst oder
// der eigene Backend-LLM-Endpoint, der die Formeln vorher gegencheckt.
(function () {
  const ALLOWED_CHARS = /^[0-9A-Za-z_+\-*/%.()\s<>!=&|]*$/;
  const FORBIDDEN_TOKENS = ['__', 'import', 'lambda', '?', ':', ';'];
  const ALLOWED_VARS = [
    'cost_price',
    'competitor_price',
    'monthly_demand',
    'start_stock',
    'stock',
    'usage',
    'hour',
    'day',
  ];

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
    // Zuweisungen verbieten: Mehrzeichen-Vergleiche (==, !=, <=, >=) rausfiltern,
    // was dann noch an '=' uebrig ist, waere eine Zuweisung.
    const stripped = expression.replace(/==|!=|<=|>=/g, '');
    if (stripped.includes('=')) throw new Error('Zuweisungen sind in der Formel nicht erlaubt');
    const values = ALLOWED_VARS.map((name) => {
      const v = variables && variables[name];
      if (v === undefined || v === null || v === '') return 0;
      const n = Number(v);
      return Number.isFinite(n) ? n : 0;
    });
    const fn = new Function(...ALLOWED_VARS, `"use strict"; return (${expression});`);
    return fn(...values);
  }

  window.evaluateFormula = evaluateFormula;
  window.ALLOWED_FORMULA_VARS = ALLOWED_VARS;
})();
