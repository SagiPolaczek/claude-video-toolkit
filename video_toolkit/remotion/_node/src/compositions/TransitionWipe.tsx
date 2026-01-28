import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
  staticFile,
} from "remotion";
import type { TransitionWipeProps } from "../lib/types";

export const TransitionWipe: React.FC<TransitionWipeProps> = ({
  fromImagePath,
  toImagePath,
  direction = "right",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fromSrc = fromImagePath.startsWith("http")
    ? fromImagePath
    : staticFile(fromImagePath);
  const toSrc = toImagePath.startsWith("http")
    ? toImagePath
    : staticFile(toImagePath);

  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const getClipPath = () => {
    switch (direction) {
      case "right":
        return `inset(0 ${100 - progress}% 0 0)`;
      case "left":
        return `inset(0 0 0 ${100 - progress}%)`;
      case "down":
        return `inset(0 0 ${100 - progress}% 0)`;
      case "up":
        return `inset(${100 - progress}% 0 0 0)`;
    }
  };

  return (
    <AbsoluteFill>
      <AbsoluteFill>
        <Img src={fromSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ clipPath: getClipPath() }}>
        <Img src={toSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
