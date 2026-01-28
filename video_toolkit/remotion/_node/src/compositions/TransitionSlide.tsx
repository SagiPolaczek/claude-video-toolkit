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
import type { TransitionSlideProps } from "../lib/types";

export const TransitionSlide: React.FC<TransitionSlideProps> = ({
  fromImagePath,
  toImagePath,
  direction = "left",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();

  const fromSrc = fromImagePath.startsWith("http")
    ? fromImagePath
    : staticFile(fromImagePath);
  const toSrc = toImagePath.startsWith("http")
    ? toImagePath
    : staticFile(toImagePath);

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const getTransform = (isFrom: boolean) => {
    const offset = isFrom ? -progress : 1 - progress;
    switch (direction) {
      case "left":
        return `translateX(${offset * width}px)`;
      case "right":
        return `translateX(${-offset * width}px)`;
      case "up":
        return `translateY(${offset * height}px)`;
      case "down":
        return `translateY(${-offset * height}px)`;
    }
  };

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: getTransform(true) }}>
        <Img src={fromSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ transform: getTransform(false) }}>
        <Img src={toSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
