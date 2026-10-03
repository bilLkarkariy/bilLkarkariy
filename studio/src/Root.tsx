import React from 'react';
import {Composition} from 'remotion';
import './fonts';
import {Short, SHORT_END, SHORTS} from './Short';
import {V01, V01_DURATION} from './V01';

export const Root: React.FC = () => (
  <>
    <Composition id="V01" component={V01} durationInFrames={V01_DURATION} fps={30} width={1920} height={1080} />
    {SHORTS.map((s) => (
      <Composition
        key={s.id}
        id={s.id}
        component={Short}
        durationInFrames={s.to - s.from + SHORT_END}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{from: s.from, to: s.to, title: s.title}}
      />
    ))}
  </>
);
