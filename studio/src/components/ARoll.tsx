import {useText} from '../i18n';
import React from 'react';
import {AbsoluteFill, getInputProps, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F} from '../theme';

/**
 * Emplacement face caméra, en attendant les rushes : une photo de Billel (public/aroll/, jamais dans git).
 * Plans larges (taille, poitrine ; en ourdou « کمر تک », « سینے تک ») : setup.jpg, le bureau en entier ; plans serrés : placeholder.jpg.
 * --props '{"clean":true}' : sans le carton « à remplacer » ni la réplique (vidéo livrée, Shorts).
 * Au montage final, remplacer par <OffthreadVideo src={...} startFrom={...} />.
 */
const CLEAN = Boolean(getInputProps().clean);
/** --props '{"faceless":true}' : seul le premier face caméra reste (src/montage/faceless.tsx). */
export const FACELESS = Boolean(getInputProps().faceless);
export const ARoll: React.FC<{shot: string; line: string}> = ({shot, line}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.045]);
  return (
    <AbsoluteFill style={{background: C.night, overflow: 'hidden'}}>
      <Img
        src={staticFile(/TAILLE|POITRINE|WAIST|CHEST|کمر تک|سینے تک/.test(shot) ? 'aroll/setup.jpg' : 'aroll/placeholder.jpg')}
        style={{
          position: 'absolute',
          width: 1920,
          height: 1080,
          top: 0,
          left: 0,
          objectFit: 'cover',
          objectPosition: '50% 30%',
          transform: `scale(${zoom})`,
          transformOrigin: '50% 52%',
          filter: 'saturate(0.82) contrast(1.04) brightness(1.05) sepia(0.06)',
        }}
      />
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.38) 100%)',
        }}
      />
      {CLEAN ? null : (
        <>
          <div
            style={{
              position: 'absolute',
              left: 56,
              top: 48,
              display: 'flex',
              gap: 14,
              alignItems: 'center',
            }}
          >
            <span
              style={{
                fontFamily: F.mono,
                fontWeight: 500,
                fontSize: 20,
                letterSpacing: '0.14em',
                color: '#111',
                background: '#F2D64B',
                padding: '6px 12px',
              }}
            >{tx("A-ROLL · À REMPLACER")}</span>
            <span
              style={{
                fontFamily: F.mono,
                fontSize: 20,
                letterSpacing: '0.1em',
                color: 'rgba(255,255,255,0.85)',
              }}
            >
              {shot}
            </span>
          </div>
          <div
            style={{
              position: 'absolute',
              left: 56,
              right: 56,
              bottom: 52,
              fontFamily: F.serif,
              fontStyle: 'italic',
              fontSize: 34,
              color: 'rgba(255,255,255,0.9)',
              textShadow: '0 1px 12px rgba(0,0,0,0.6)',
            }}
          >
            {line}
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
