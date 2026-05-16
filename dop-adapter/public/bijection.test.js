// tests/bijection.test.js
// Formal bijection proof tests for OBINexus DOP Adapter

'use strict';

const DOPAdapter = require('../src/adapter/DOPAdapter');
const ButtonLogic = require('../src/components/ButtonLogic');

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✓ ${label}`);
    passed++;
  } else {
    console.error(`  ✗ ${label}`);
    failed++;
  }
}

console.log('\n━━━ OBIX DOP Adapter — Bijection Test Suite ━━━\n');

// ─── Group 1: Adapter Construction ────────────────────────────────────────────
console.log('Group 1: Adapter Construction');
const adapter = new DOPAdapter(ButtonLogic);
assert(adapter instanceof DOPAdapter, 'DOPAdapter instantiates');
assert(adapter.logic === ButtonLogic, 'Logic reference preserved');
assert(adapter._origin === 'declarative', 'Origin set to declarative');

// ─── Group 2: Functional Form ─────────────────────────────────────────────────
console.log('\nGroup 2: Functional Form');
const Func = adapter.toFunctional();
assert(typeof Func === 'function', 'toFunctional returns a function');
assert(Func._obixMeta.origin === 'functional', 'Meta origin tagged as functional');
assert(typeof Func._toDOP === 'function', 'Inverse _toDOP attached');
const funcOut = Func();
assert(typeof funcOut === 'string', 'Functional render returns string');
assert(funcOut.includes('ACTIVATE'), 'Functional default state correct');
assert(funcOut.includes('OFF'), 'Functional default OFF state');

// ─── Group 3: OOP Form ────────────────────────────────────────────────────────
console.log('\nGroup 3: OOP Form');
const OOPClass = adapter.toOOP();
assert(typeof OOPClass === 'function', 'toOOP returns a constructor');
assert(OOPClass._obixMeta.origin === 'oop', 'Meta origin tagged as oop');
const oop = new OOPClass();
assert(typeof oop.render === 'function', 'OOP instance has render()');
assert(typeof oop.toggle === 'function', 'OOP instance has toggle()');
assert(typeof oop.reset === 'function', 'OOP instance has reset()');
assert(oop.state.clicked === false, 'OOP initial state correct');
const oopOut = oop.render();
assert(typeof oopOut === 'string', 'OOP render returns string');

// ─── Group 4: Bijection Proof ─────────────────────────────────────────────────
console.log('\nGroup 4: Bijection Proof');
const proof = adapter.verifyBijection();
assert(proof.equivalent === true, 'Default state: functional ≡ OOP');
assert(proof.functional === proof.oop, 'Outputs are identical strings');
assert(proof.delta === null, 'No delta (no divergence)');

// Bijection under action
oop.toggle();
const Func2 = adapter.toFunctional();
const clickedState = { clicked: true, label: 'DEACTIVATE' };
const funcClicked = Func2(clickedState);
const oopClicked = oop.render();
assert(funcClicked === oopClicked, 'Post-toggle: functional ≡ OOP');

// ─── Group 5: Inverse Recovery ────────────────────────────────────────────────
console.log('\nGroup 5: Inverse Recovery');
const recoveredFromFunc = Func._toDOP();
const recoveredFromOOP = OOPClass._toDOP();
assert(recoveredFromFunc === ButtonLogic, 'Functional → DOP recovery correct');
assert(recoveredFromOOP === ButtonLogic, 'OOP → DOP recovery correct');
assert(recoveredFromFunc === recoveredFromOOP, 'Both inverses return same canonical logic');

// ─── Group 6: Multiple Instances ─────────────────────────────────────────────
console.log('\nGroup 6: Instance Isolation');
const btn1 = new OOPClass();
const btn2 = new OOPClass();
btn1.toggle();
assert(btn1.state.clicked === true, 'btn1 state mutated');
assert(btn2.state.clicked === false, 'btn2 state unaffected (isolated)');

// ─── Summary ──────────────────────────────────────────────────────────────────
console.log(`\n━━━ Results: ${passed} passed, ${failed} failed ━━━━━━━━━━━━━`);
process.exit(failed > 0 ? 1 : 0);
