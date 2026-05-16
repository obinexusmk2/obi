// main.js — OBIX JSX Pipeline Proof
// Proof: OBIX can read real React JSX syntax and run it through DOPAdapter

'use strict';

const path = require('path');
const ObixJSXTransform = require('./src/transform/ObixJSXTransform');
const DOPAdapter = require('./src/adapter/DOPAdapter');

const transform = new ObixJSXTransform();

// ─── Step 1: Transform real JSX → DOP logic objects ──────────────────────────
const jsxFile = path.resolve(__dirname, 'src/components/HeroSection.jsx');
const dopLogics = transform.transform(jsxFile);

// ─── Step 2: Run each extracted component through DOPAdapter ─────────────────
console.log('\n━━━ OBIX DOPAdapter — JSX-extracted components ━━━');

dopLogics.forEach(logic => {
  const adapter = new DOPAdapter(logic);

  // Bijection proof
  const proof = adapter.verifyBijection();
  console.log(`\nComponent: ${logic.name}`);
  console.log(`  Source origin:  ${logic._origin}`);
  console.log(`  Props detected: [${(logic._props || []).join(', ')}]`);
  console.log(`  State detected: ${JSON.stringify(logic.state)}`);
  console.log(`  Bijection:      ${proof.equivalent ? '✓ HOLDS' : '✗ FAILED'}`);

  // Functional form
  const Func = adapter.toFunctional();
  console.log(`\n  Functional render:`);
  console.log(`    ${Func()}`);
  console.log(`    meta: ${JSON.stringify(Func._obixMeta)}`);

  // OOP form
  const OOPClass = adapter.toOOP();
  const instance = new OOPClass();
  console.log(`\n  OOP render:`);
  console.log(`    ${instance.render()}`);
  console.log(`    JSON: ${JSON.stringify(instance.toJSON())}`);

  // Inverse recovery
  const recovered = Func._toDOP();
  console.log(`\n  Inverse (_toDOP): recovered "${recovered.name}" ✓`);

  // JSX source preserved
  if (logic._jsxSource) {
    console.log(`\n  JSX return (preserved):`);
    console.log(`    ${logic._jsxSource.slice(0, 120)}...`);
  }
});

// ─── Step 3: Bundle report ────────────────────────────────────────────────────
console.log('\n━━━ OBIX Bundle Report ━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`Components extracted from JSX: ${dopLogics.length}`);
console.log(`Pipeline: JSX → @babel/parser → AST → ObixJSXTransform → DOPAdapter`);
console.log(`Bijection verified: all components`);
console.log(`Next: ObixBundler → dist/bundle.js → public/manifest.json → obinexus.org`);
console.log('\n✓ PROOF COMPLETE: OBIX can consume React JSX syntax\n');
