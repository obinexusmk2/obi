// src/transform/ObixJSXTransform.js
// OBIX JSX Transform Layer
// Pipeline: JSX source → Babel AST → extract component logic → DOPAdapter canonical form
// This is the proof: OBIX can READ real React JSX and understand it

'use strict';

const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const t = require('@babel/types');
const generate = require('@babel/generator').default;
const fs = require('fs');

class ObixJSXTransform {
  constructor() {
    this.components = [];
  }

  // ─── Parse JSX file into Babel AST ─────────────────────────────────────────
  parse(filePath) {
    const source = fs.readFileSync(filePath, 'utf8');
    const ast = parser.parse(source, {
      sourceType: 'module',
      plugins: ['jsx']
    });
    console.log(`✓ Parsed JSX: ${filePath}`);
    return { ast, source };
  }

  // ─── Extract component structure from AST ───────────────────────────────────
  // Walks the AST and pulls out:
  //   - component name
  //   - props (from function params)
  //   - useState calls → state declarations
  //   - JSX return → render signature
  //   - event handlers → actions
  extract(ast, source) {
    const components = [];

    traverse(ast, {
      // Match: const ComponentName = (...) => { ... }
      // Match: function ComponentName(...) { ... }
      VariableDeclaration(path) {
        path.node.declarations.forEach(decl => {
          if (!decl.init) return;
          const isFuncExpr = t.isArrowFunctionExpression(decl.init) ||
                             t.isFunctionExpression(decl.init);
          if (!isFuncExpr) return;

          const name = decl.id.name;
          if (!name || !/^[A-Z]/.test(name)) return; // React components start uppercase

          const fn = decl.init;
          const component = {
            name,
            origin: 'functional',
            props: [],
            state: {},
            actions: {},
            jsxReturn: null,
            rawSource: generate(decl).code
          };

          // Extract props from first param (destructured object)
          if (fn.params.length > 0) {
            const param = fn.params[0];
            if (t.isObjectPattern(param)) {
              param.properties.forEach(prop => {
                if (t.isObjectProperty(prop)) {
                  component.props.push(prop.key.name);
                }
              });
            }
          }

          // Walk function body for useState and handlers
          if (fn.body && t.isBlockStatement(fn.body)) {
            fn.body.body.forEach(stmt => {
              // Detect: const [x, setX] = useState(initialValue)
              if (
                t.isVariableDeclaration(stmt) &&
                stmt.declarations.length > 0
              ) {
                stmt.declarations.forEach(d => {
                  if (
                    t.isArrayPattern(d.id) &&
                    t.isCallExpression(d.init) &&
                    t.isIdentifier(d.init.callee, { name: 'useState' })
                  ) {
                    const stateKey = d.id.elements[0]?.name;
                    const initArg = d.init.arguments[0];
                    let initVal = null;
                    if (t.isBooleanLiteral(initArg)) initVal = initArg.value;
                    else if (t.isStringLiteral(initArg)) initVal = initArg.value;
                    else if (t.isNumericLiteral(initArg)) initVal = initArg.value;
                    else if (t.isNullLiteral(initArg)) initVal = null;
                    if (stateKey) component.state[stateKey] = initVal;
                  }

                  // Detect: const handleX = () => { ... }
                  if (
                    t.isIdentifier(d.id) &&
                    /^handle[A-Z]/.test(d.id.name) &&
                    (t.isArrowFunctionExpression(d.init) || t.isFunctionExpression(d.init))
                  ) {
                    component.actions[d.id.name] = generate(d.init).code;
                  }
                });
              }

              // Detect: return (<JSX...>)
              if (t.isReturnStatement(stmt) && stmt.argument) {
                const returnCode = generate(stmt.argument).code;
                component.jsxReturn = returnCode;
              }
            });
          }

          components.push(component);
          console.log(`  ✓ Extracted component: ${name}`);
          console.log(`    props:   [${component.props.join(', ')}]`);
          console.log(`    state:   ${JSON.stringify(component.state)}`);
          console.log(`    actions: [${Object.keys(component.actions).join(', ')}]`);
          console.log(`    jsx:     ${component.jsxReturn ? 'present' : 'none'}`);
        });
      }
    });

    return components;
  }

  // ─── Convert extracted component to DOP canonical logic object ──────────────
  // This is the bridge: JSX component → DOPAdapter input format
  toDOPLogic(component) {
    return {
      name: component.name,
      state: { ...component.state },
      actions: Object.keys(component.actions).reduce((acc, key) => {
        // Actions are represented as strings (source-faithful)
        // In a full implementation these would be eval'd or code-gen'd
        acc[key] = `[extracted from JSX: ${key}]`;
        return acc;
      }, {}),
      // render: produces an HTML string representation of the JSX structure
      render: (ctx) => {
        // Simplified render: emit component signature as HTML comment + shell
        const stateStr = JSON.stringify(ctx.state);
        return `<div class="obix-component obix-component--${component.name.toLowerCase()}" data-state='${stateStr}'>[${component.name}]</div>`;
      },
      // Preserve the full JSX source for reference
      _jsxSource: component.jsxReturn,
      _props: component.props,
      _origin: 'jsx-extracted'
    };
  }

  // ─── Full transform pipeline ─────────────────────────────────────────────────
  transform(filePath) {
    console.log(`\n━━━ OBIX JSX Transform: ${filePath} ━━━`);
    const { ast, source } = this.parse(filePath);
    const components = this.extract(ast, source);
    const dopLogics = components.map(c => this.toDOPLogic(c));
    console.log(`\n✓ Transform complete: ${dopLogics.length} component(s) extracted`);
    return dopLogics;
  }
}

module.exports = ObixJSXTransform;
