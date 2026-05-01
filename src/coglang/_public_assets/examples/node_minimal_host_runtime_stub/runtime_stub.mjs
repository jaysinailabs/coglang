const SUPPORTED_HEADS = new Set(["True", "False", "Equal"]);

function splitTopLevelArgs(source) {
  const args = [];
  let current = "";
  let inString = false;
  let escapeNext = false;
  let depth = 0;

  for (const char of source) {
    if (escapeNext) {
      current += char;
      escapeNext = false;
      continue;
    }
    if (char === "\\") {
      current += char;
      escapeNext = true;
      continue;
    }
    if (char === "\"") {
      current += char;
      inString = !inString;
      continue;
    }
    if (!inString && char === "[") {
      depth += 1;
    }
    if (!inString && char === "]") {
      depth -= 1;
    }
    if (!inString && depth === 0 && char === ",") {
      args.push(current.trim());
      current = "";
      continue;
    }
    current += char;
  }

  if (current.trim() !== "") {
    args.push(current.trim());
  }
  return args;
}

function parseLiteral(source) {
  const trimmed = source.trim();
  if (trimmed === "True") {
    return { ok: true, value: true };
  }
  if (trimmed === "False") {
    return { ok: true, value: false };
  }
  if (/^-?\d+$/.test(trimmed)) {
    return { ok: true, value: Number.parseInt(trimmed, 10) };
  }
  if (
    trimmed.length >= 2
    && trimmed.startsWith("\"")
    && trimmed.endsWith("\"")
  ) {
    try {
      return { ok: true, value: JSON.parse(trimmed) };
    } catch {
      return {
        ok: false,
        error_kind: "ParseError",
        errors: [`invalid string literal: ${trimmed}`],
      };
    }
  }
  return {
    ok: false,
    error_kind: "UnsupportedExpression",
    errors: [`unsupported literal: ${trimmed}`],
  };
}

function parseExpression(source) {
  const trimmed = String(source).trim();
  if (trimmed === "True" || trimmed === "False") {
    return { ok: true, head: trimmed, args: [] };
  }

  const match = /^([A-Za-z][A-Za-z0-9_]*)\[(.*)\]$/.exec(trimmed);
  if (!match) {
    return {
      ok: false,
      error_kind: "ParseError",
      errors: [`unsupported expression syntax: ${trimmed}`],
    };
  }

  const [, head, argSource] = match;
  if (!SUPPORTED_HEADS.has(head)) {
    return {
      ok: false,
      error_kind: "UnsupportedExpression",
      errors: [`unsupported head: ${head}`],
    };
  }
  return { ok: true, head, args: splitTopLevelArgs(argSource) };
}

export function validate(source) {
  const parsed = parseExpression(source);
  if (!parsed.ok) {
    return parsed;
  }
  if (parsed.head === "Equal" && parsed.args.length !== 2) {
    return {
      ok: false,
      error_kind: "ArityError",
      errors: [`Equal expects 2 arguments, got ${parsed.args.length}`],
    };
  }
  if (parsed.head !== "Equal" && parsed.args.length !== 0) {
    return {
      ok: false,
      error_kind: "ArityError",
      errors: [`${parsed.head} expects 0 arguments, got ${parsed.args.length}`],
    };
  }
  return {
    ok: true,
    errors: [],
    expression: String(source).trim(),
    supported_heads: [...SUPPORTED_HEADS].sort(),
  };
}

export function execute(source) {
  const validation = validate(source);
  if (!validation.ok) {
    return {
      ok: false,
      value_kind: "ErrorValue",
      error_kind: validation.error_kind,
      errors: validation.errors,
      expression: String(source).trim(),
    };
  }

  const parsed = parseExpression(source);
  if (parsed.head === "True") {
    return { ok: true, value_kind: "Boolean", value: true };
  }
  if (parsed.head === "False") {
    return { ok: true, value_kind: "Boolean", value: false };
  }

  const left = parseLiteral(parsed.args[0]);
  const right = parseLiteral(parsed.args[1]);
  if (!left.ok || !right.ok) {
    return {
      ok: false,
      value_kind: "ErrorValue",
      error_kind: "UnsupportedExpression",
      errors: [...(left.errors ?? []), ...(right.errors ?? [])],
      expression: String(source).trim(),
    };
  }
  return {
    ok: true,
    value_kind: "Boolean",
    value: left.value === right.value,
  };
}
