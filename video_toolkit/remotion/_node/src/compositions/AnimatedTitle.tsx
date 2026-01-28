import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import type { AnimatedTitleProps } from "../lib/types";
import { rgbToCSS } from "../lib/utils";

export const AnimatedTitle: React.FC<AnimatedTitleProps> = ({
  title,
  subtitle,
  animation = "fade_up",
  backgroundColor,
  titleColor,
  subtitleColor,
  titleFontSize,
  subtitleFontSize,
  titleFont = "Arial",
  subtitleFont = "Arial",
  width: _w,
  height: _h,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const bgColor = rgbToCSS(backgroundColor, "rgb(255, 255, 255)");
  const tColor = rgbToCSS(titleColor, "rgb(30, 30, 40)");
  const sColor = rgbToCSS(subtitleColor, "rgb(100, 100, 100)");

  // Fade-in and fade-out, with safe handling for short clips.
  // Remotion requires strictly monotonically increasing inputRange,
  // so when fades would overlap we use a simpler two-point interpolation.
  const rawFadeIn = Math.round(fps * 0.8);
  const rawFadeOut = Math.round(fps * 0.5);

  let opacity: number;
  if (rawFadeIn + rawFadeOut >= durationInFrames) {
    // Short clip: crossfade up then down with no hold
    const mid = Math.floor(durationInFrames / 2);
    if (mid <= 0 || mid >= durationInFrames) {
      opacity = 1;
    } else {
      opacity = interpolate(
        frame,
        [0, mid, durationInFrames],
        [0, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
    }
  } else {
    opacity = interpolate(
      frame,
      [0, rawFadeIn, durationInFrames - rawFadeOut, durationInFrames],
      [0, 1, 1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
  }

  // Animation-specific transforms for the title
  const titleStyle = getTitleAnimation(animation, frame, fps);
  const subtitleStyle = getSubtitleAnimation(animation, frame, fps);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgColor,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          color: tColor,
          fontSize: titleFontSize ?? 64,
          fontFamily: titleFont,
          fontWeight: 700,
          textAlign: "center",
          maxWidth: "80%",
          lineHeight: 1.2,
          ...titleStyle,
        }}
      >
        {title}
      </div>
      {subtitle && (
        <div
          style={{
            color: sColor,
            fontSize: subtitleFontSize ?? 36,
            fontFamily: subtitleFont,
            fontWeight: 400,
            textAlign: "center",
            maxWidth: "70%",
            marginTop: 24,
            lineHeight: 1.3,
            ...subtitleStyle,
          }}
        >
          {subtitle}
        </div>
      )}
    </AbsoluteFill>
  );
};

function getTitleAnimation(
  animation: string,
  frame: number,
  fps: number
): React.CSSProperties {
  const animFrames = Math.round(fps * 0.8);
  const progress = Math.min(frame / animFrames, 1);

  switch (animation) {
    case "fade_up": {
      const y = interpolate(frame, [0, animFrames], [40, 0], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { transform: `translateY(${y}px)` };
    }
    case "slide_left": {
      const x = interpolate(frame, [0, animFrames], [100, 0], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { transform: `translateX(${x}px)` };
    }
    case "typewriter": {
      const chars = Math.round(progress * 100);
      return {
        clipPath: `inset(0 ${100 - chars}% 0 0)`,
      };
    }
    case "scale": {
      const scale = interpolate(frame, [0, animFrames], [0.8, 1], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { transform: `scale(${scale})` };
    }
    default:
      return {};
  }
}

function getSubtitleAnimation(
  animation: string,
  frame: number,
  fps: number
): React.CSSProperties {
  // Subtitle appears slightly after title (0.3s delay)
  const delay = Math.round(fps * 0.3);
  const animFrames = Math.round(fps * 0.6);
  const adjustedFrame = Math.max(0, frame - delay);

  const opacity = interpolate(adjustedFrame, [0, animFrames], [0, 1], {
    extrapolateRight: "clamp",
  });

  switch (animation) {
    case "fade_up": {
      const y = interpolate(adjustedFrame, [0, animFrames], [20, 0], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { transform: `translateY(${y}px)`, opacity };
    }
    case "slide_left": {
      const x = interpolate(adjustedFrame, [0, animFrames], [60, 0], {
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return { transform: `translateX(${x}px)`, opacity };
    }
    case "typewriter":
    case "scale":
      return { opacity };
    default:
      return { opacity };
  }
}
