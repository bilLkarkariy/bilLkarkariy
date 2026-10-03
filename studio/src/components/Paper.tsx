import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';

/** Fond papier. `grid` = quadrillage du carnet de labo (0 à 1). */
export const Paper: React.FC<{warm?: boolean; grid?: number}> = ({warm, grid = 0}) => (
  <AbsoluteFill>
    <Img src={staticFile(warm ? 'tex/paper_warm.png' : 'tex/paper_cool.png')} />
    {grid > 0 && (
      <AbsoluteFill style={{opacity: grid}}>
        <Img src={staticFile('tex/grid.png')} />
      </AbsoluteFill>
    )}
  </AbsoluteFill>
);

/** Grain argentique léger sur toute l'image, change toutes les 2 images. */
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.07}) => {
  const frame = useCurrentFrame();
  const i = Math.floor(frame / 2) % 8;
  return (
    <AbsoluteFill style={{mixBlendMode: 'overlay', opacity, pointerEvents: 'none'}}>
      <Img src={staticFile(`tex/grain_${i}.png`)} style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};
