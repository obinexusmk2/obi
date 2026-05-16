/**
 * OBIX Bundle — OBINexus Data Origin Pattern
 * Generated: 2026-04-22T19:15:53.117Z
 * Version: 1.0.0
 * Components: Button
 * Bijection: VERIFIED
 */
(function(global) {
  'use strict';

  var OBIXRegistry = {};

  
  // ── Component: Button ──────────────────────────────────────────────
  OBIXRegistry["Button"] = {
    meta: {"name":"Button","origin":"functional","actions":["toggle","reset"]},
    state: {"clicked":false,"label":"ACTIVATE"},
    functional: function(overrideState) {
      var state = Object.assign({"clicked":false,"label":"ACTIVATE"}, overrideState || {});
      var ctx = { state: state };
      return (ctx) => {
    const status = ctx.state.clicked ? 'ON' : 'OFF';
    return `<button class="obix-btn obix-btn--${status.toLowerCase()}" data-state="${status}">${ctx.state.label} [${status}]</button>`;
  }.call(null, ctx);
    },
    oop: (function() {
      function OOPComponent(initialState) {
        this.name = "Button";
        this.state = Object.assign({"clicked":false,"label":"ACTIVATE"}, initialState || {});
        var self = this;
        this["toggle"] = function() { return ((ctx) => {
      ctx.state.clicked = !ctx.state.clicked;
      ctx.state.label = ctx.state.clicked ? 'DEACTIVATE' : 'ACTIVATE';
    })(self); };
        this["reset"] = function() { return ((ctx) => {
      ctx.state.clicked = false;
      ctx.state.label = 'ACTIVATE';
    })(self); };
      }
      OOPComponent.prototype.render = function() {
        return ((ctx) => {
    const status = ctx.state.clicked ? 'ON' : 'OFF';
    return `<button class="obix-btn obix-btn--${status.toLowerCase()}" data-state="${status}">${ctx.state.label} [${status}]</button>`;
  }).call(null, this);
      };
      return OOPComponent;
    })()
  };

  // Runtime API
  global.OBIX = {
    version: "1.0.0",
    appId: "com.obinexus.obix",
    registry: OBIXRegistry,

    // Get functional form of component
    functional: function(name, state) {
      var comp = OBIXRegistry[name];
      if (!comp) throw new Error('OBIX: Component not found: ' + name);
      return comp.functional(state);
    },

    // Get OOP instance of component
    oop: function(name, state) {
      var comp = OBIXRegistry[name];
      if (!comp) throw new Error('OBIX: Component not found: ' + name);
      return new comp.oop(state);
    },

    // Mount component to DOM element
    mount: function(name, targetSelector, state, useOOP) {
      var el = document.querySelector(targetSelector);
      if (!el) throw new Error('OBIX: Mount target not found: ' + targetSelector);
      if (useOOP) {
        var instance = this.oop(name, state);
        el.innerHTML = instance.render();
        return instance;
      } else {
        el.innerHTML = this.functional(name, state);
        return null;
      }
    }
  };

})(typeof window !== 'undefined' ? window : global);