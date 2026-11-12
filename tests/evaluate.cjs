// Evaluate library calls through the JS engine's normal module loader.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const engine = require(path.resolve(process.env.FLATPPL_JS_DIR || path.join(root, '../flatppl-js'), 'packages/engine/index.ts'));
const request = JSON.parse(fs.readFileSync(0, 'utf8'));
const expressions = Array.isArray(request) ? request : null;
const modulePaths = ['main.flatppl', ...fs.readdirSync(path.join(root, 'src'))
  .filter(name => name.endsWith('.flatppl')).map(name => 'src/' + name)];
const sources = Object.fromEntries(modulePaths
  .map(name => [path.join(root, name), fs.readFileSync(path.join(root, name), 'utf8')]));
const source = expressions ? 'flatppl_compat = "0.1"\na = load_module("../main.flatppl")\n'
  + expressions.map((expression, i) => `probe${i} = ${expression}`).join('\n') : request.source;
const model = engine.processSource(source, { path: path.join(__dirname, 'query.flatppl'), bundle: { sources } });
const errors = model.diagnostics.filter(d => d.severity === 'error');
if (errors.length) throw new Error(JSON.stringify(errors));
const result = engine.orchestrator.buildDerivations(model.linkedBindings, { moduleRegistry: model.linkedModuleRegistry });
const names = expressions ? expressions.map((_, i) => `probe${i}`) : request.bindings;
const values = names.map(name => {
  if (!result.fixedValues.has(name)) throw new Error(`${name} did not evaluate`);
  return result.fixedValues.get(name);
});
process.stdout.write(JSON.stringify(values));
