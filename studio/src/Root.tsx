import React from 'react';
import {Composition} from 'remotion';
import './fonts';
import {Hook, HOOK_DURATION} from './Hook';

export const Root: React.FC = () => (
  <Composition id="Hook" component={Hook} durationInFrames={HOOK_DURATION} fps={30} width={1920} height={1080} />
);
