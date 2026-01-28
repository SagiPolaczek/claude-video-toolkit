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
import type { KenBurnsProps } from "../lib/types";
import { rgbToCSS } from "../lib/utils";

export const KenBurns: React.FC<KenBurnsProps> = ({
  imagePath,
  startScale = 1.0,
  endScale = 1.2,
  panX = 0,
  panY = 0,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const bgColor = rgbToCSS(backgroundColor, "rgb(255, 255, 255)");

  const imgSrc = imagePath.startsWith("http")
    ? imagePath
    : staticFile(imagePath);

  const scale = interpolate(frame, [0, durationInFrames], [startScale, endScale], {
    easing: Easing.inOut(Easing.cubic),
  });

  const translateX = interpolate(frame, [0, durationInFrames], [0, panX], {
    easing: Easing.inOut(Easing.cubic),
  });

  const translateY = interpolate(frame, [0, durationInFrames], [0, panY], {
    easing: Easing.inOut(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor, overflow: "hidden" }}>
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
            maxWidth: "100%",
            maxHeight: "100%",
            objectFit: "contain",
            transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
