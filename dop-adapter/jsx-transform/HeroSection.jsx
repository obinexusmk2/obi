// src/components/HeroSection.jsx
// obinexus.org Hero component — written in standard React JSX syntax
// OBIX will consume this and emit both functional + class forms

import React, { useState } from 'react';

const HeroSection = ({ title, subtitle, ctaText, onCta }) => {
  const [active, setActive] = useState(false);

  const handleCta = () => {
    setActive(!active);
    if (onCta) onCta();
  };

  return (
    <section className="obix-hero">
      <div className="obix-hero__inner">
        <h1 className="obix-hero__title">{title}</h1>
        <p className="obix-hero__subtitle">{subtitle}</p>
        <button
          className={`obix-btn ${active ? 'obix-btn--active' : ''}`}
          onClick={handleCta}
        >
          {ctaText}
        </button>
      </div>
    </section>
  );
};

export default HeroSection;
