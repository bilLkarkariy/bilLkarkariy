import React from 'react';
import {Composition} from 'remotion';
import './fonts';
import {V01, V01_DURATION} from './V01';

export const Root: React.FC = () => (
  <Composition id="V01" component={V01} durationInFrames={V01_DURATION} fps={30} width={1920} height={1080} />
);
