import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import type { TransitionProps } from "../lib/types";

export const TransitionFade: React.FC<TransitionProps> = ({
  fromImagePath,
  toImagePath,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fromSrc = fromImagePath.startsWith("http")
    ? fromImagePath
    : staticFile(fromImagePath);
  const toSrc = toImagePath.startsWith("http")
    ? toImagePath
    : staticFile(toImagePath);

  const opacity = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <AbsoluteFill>
        <Img src={fromSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ opacity }}>
        <Img src={toSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
