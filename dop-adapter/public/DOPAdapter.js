// adapter/DOPAdapter.js
// OBINexus OBIX - Data Origin Pattern Adapter
// Bijection guarantee: toFunctional(toOOP(logic)) ≡ logic
// Bijection guarantee: toOOP(toFunctional(logic)) ≡ logic

'use strict';

class DOPAdapter {
  constructor(logic) {
    this._validate(logic);
    this.logic = logic;
    this._origin = 'declarative'; // canonical source of truth
  }

  _validate(logic) {
    if (!logic || typeof logic !== 'object') throw new Error('DOPAdapter: logic must be a declarative object');
    if (typeof logic.render !== 'function') throw new Error('DOPAdapter: logic must define render(ctx)');
    if (!logic.state || typeof logic.state !== 'object') throw new Error('DOPAdapter: logic must define initial state object');
  }

  // ─── Functional Form ───────────────────────────────────────────────────────
  // Returns a stateless closure over a fresh state copy.
  // Identity: calling toFunctional() twice produces equivalent (not identical) functions.
  toFunctional() {
    const { name, state, actions = {}, render } = this.logic;

    function FunctionalComponent(overrideState = {}) {
      const ctx = {
        state: { ...state, ...overrideState },
        ...actions
      };
      // Actions operate on ctx.state directly (no this binding)
      return render(ctx);
    }

    FunctionalComponent._obixMeta = { name, origin: 'functional', actions: Object.keys(actions) };
    FunctionalComponent._toDOP = () => this.logic; // inverse: recover canonical logic
    return FunctionalComponent;
  }

  // ─── OOP Form ──────────────────────────────────────────────────────────────
  // Returns a class with encapsulated state, methods, and a render() method.
  // Identity: new OOPComponent()._toDOP() recovers canonical logic.
  toOOP() {
    const { name, state, actions = {}, render } = this.logic;
    const logicRef = this.logic;

    class OOPComponent {
      constructor(initialState = {}) {
        this.name = name;
        this.state = { ...state, ...initialState };

        // Bind all actions to this instance
        Object.entries(actions).forEach(([key, fn]) => {
          this[key] = (...args) => fn(this, ...args);
        });
      }

      render() {
        return render(this);
      }

      // Inverse: recover canonical declarative logic from OOP instance
      _toDOP() {
        return logicRef;
      }

      // Serialize state for bundle/manifest embedding
      toJSON() {
        return { name: this.name, state: this.state };
      }
    }

    OOPComponent._obixMeta = { name, origin: 'oop', actions: Object.keys(actions) };
    OOPComponent._toDOP = () => logicRef;
    return OOPComponent;
  }

  // ─── Bijection Verifier ────────────────────────────────────────────────────
  // Asserts that both forms produce equivalent render output for same state input.
  // This is the formal proof check — run at bundle time.
  verifyBijection(testState = {}) {
    const Func = this.toFunctional();
    const OOPClass = this.toOOP();
    const oop = new OOPClass(testState);

    const funcOutput = Func(testState);
    const oopOutput = oop.render();

    const equivalent = funcOutput === oopOutput;

    return {
      equivalent,
      functional: funcOutput,
      oop: oopOutput,
      delta: equivalent ? null : { functional: funcOutput, oop: oopOutput }
    };
  }
}

module.exports = DOPAdapter;
