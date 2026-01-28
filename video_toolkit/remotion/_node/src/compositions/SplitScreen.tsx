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
import type { SplitScreenProps } from "../lib/types";
import { rgbToCSS } from "../lib/utils";

export const SplitScreen: React.FC<SplitScreenProps> = ({
  leftImagePath,
  rightImagePath,
  leftLabel,
  rightLabel,
  dividerWidth = 4,
  dividerColor,
  labelColor,
  labelFontSize,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const bgColor = rgbToCSS(backgroundColor, "rgb(255, 255, 255)");
  const divColor = rgbToCSS(dividerColor, "rgb(30, 30, 40)");
  const lblColor = rgbToCSS(labelColor, "rgb(30, 30, 40)");
  const lblSize = labelFontSize ?? 24;

  const leftSrc = leftImagePath.startsWith("http")
    ? leftImagePath
    : staticFile(leftImagePath);
  const rightSrc = rightImagePath.startsWith("http")
    ? rightImagePath
    : staticFile(rightImagePath);

  // Slide-in animation
  const animFrames = Math.round(fps * 0.6);
  const leftX = interpolate(frame, [0, animFrames], [-width / 2, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const rightX = interpolate(frame, [0, animFrames], [width / 2, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const dividerOpacity = interpolate(
    frame,
    [animFrames * 0.5, animFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const panelWidth = (width - dividerWidth) / 2;
  const labelPadding = 16;

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor }}>
      {/* Left panel */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: panelWidth,
          height,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `translateX(${leftX}px)`,
        }}
      >
        <Img
          src={leftSrc}
          style={{
            maxWidth: "95%",
            maxHeight: "85%",
            objectFit: "contain",
          }}
        />
        {leftLabel && (
          <div
            style={{
              position: "absolute",
              bottom: labelPadding,
              left: 0,
              right: 0,
              textAlign: "center",
              color: lblColor,
              fontSize: lblSize,
              fontFamily: "Arial",
              fontWeight: 600,
            }}
          >
            {leftLabel}
          </div>
        )}
      </div>

      {/* Divider */}
      <div
        style={{
          position: "absolute",
          left: panelWidth,
          top: 0,
          width: dividerWidth,
          height,
          backgroundColor: divColor,
          opacity: dividerOpacity,
        }}
      />

      {/* Right panel */}
      <div
        style={{
          position: "absolute",
          left: panelWidth + dividerWidth,
          top: 0,
          width: panelWidth,
          height,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `translateX(${rightX}px)`,
        }}
      >
        <Img
          src={rightSrc}
          style={{
            maxWidth: "95%",
            maxHeight: "85%",
            objectFit: "contain",
          }}
        />
        {rightLabel && (
          <div
            style={{
              position: "absolute",
              bottom: labelPadding,
              left: 0,
              right: 0,
              textAlign: "center",
              color: lblColor,
              fontSize: lblSize,
              fontFamily: "Arial",
              fontWeight: 600,
            }}
          >
            {rightLabel}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
