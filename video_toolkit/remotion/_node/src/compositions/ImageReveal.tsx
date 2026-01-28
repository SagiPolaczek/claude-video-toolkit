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
import type { ImageRevealProps } from "../lib/types";
import { rgbToCSS } from "../lib/utils";

export const ImageReveal: React.FC<ImageRevealProps> = ({
  imagePath,
  effect = "fade",
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const bgColor = rgbToCSS(backgroundColor, "rgb(255, 255, 255)");

  const revealFrames = Math.round(fps * 0.8);
  const fadeOutFrames = Math.round(fps * 0.5);

  const imgSrc = imagePath.startsWith("http")
    ? imagePath
    : staticFile(imagePath);

  const containerOpacity = interpolate(
    frame,
    [durationInFrames - fadeOutFrames, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const imageStyle = getRevealStyle(effect, frame, revealFrames);

  return (
    <AbsoluteFill
      style={{ backgroundColor: bgColor, opacity: containerOpacity }}
    >
      <AbsoluteFill
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Img
          src={imgSrc}
          style={{
            maxWidth: "90%",
            maxHeight: "85%",
            objectFit: "contain",
            ...imageStyle,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

function getRevealStyle(
  effect: string,
  frame: number,
  revealFrames: number
): React.CSSProperties {
  switch (effect) {
    case "fade": {
      const opacity = interpolate(frame, [0, revealFrames], [0, 1], {
        extrapolateRight: "clamp",
      });
      return { opacity };
    }
    case "wipe_right": {
      const progress = interpolate(frame, [0, revealFrames], [0, 100], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { clipPath: `inset(0 ${100 - progress}% 0 0)` };
    }
    case "zoom": {
      const scale = interpolate(frame, [0, revealFrames], [1.3, 1], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      const opacity = interpolate(frame, [0, revealFrames * 0.3], [0, 1], {
        extrapolateRight: "clamp",
      });
      return { transform: `scale(${scale})`, opacity };
    }
    case "blur": {
      const blur = interpolate(frame, [0, revealFrames], [20, 0], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      const opacity = interpolate(frame, [0, revealFrames * 0.5], [0, 1], {
        extrapolateRight: "clamp",
      });
      return { filter: `blur(${blur}px)`, opacity };
    }
    default:
      return {};
  }
}
