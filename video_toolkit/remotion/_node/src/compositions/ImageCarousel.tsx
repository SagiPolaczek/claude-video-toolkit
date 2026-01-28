import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  Easing,
} from "remotion";
import type { ImageCarouselProps } from "../lib/types";
import { rgbToCSS } from "../lib/utils";

export const ImageCarousel: React.FC<ImageCarouselProps> = ({
  imagePaths,
  framesPerImage,
  transition = "fade",
  transitionFrames,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const bgColor = rgbToCSS(backgroundColor, "rgb(255, 255, 255)");

  const totalImages = imagePaths.length;
  if (totalImages === 0) {
    return <AbsoluteFill style={{ backgroundColor: bgColor }} />;
  }

  const srcs = imagePaths.map((p) =>
    p.startsWith("http") ? p : staticFile(p)
  );

  // Calculate timing: distribute duration evenly across images
  const perImage = framesPerImage ?? Math.floor(durationInFrames / totalImages);
  const transDur = transitionFrames ?? Math.round(fps * 0.4);

  // Determine current image index and local progress
  const rawIndex = frame / perImage;
  const currentIndex = Math.min(Math.floor(rawIndex), totalImages - 1);
  const nextIndex = Math.min(currentIndex + 1, totalImages - 1);
  const localFrame = frame - currentIndex * perImage;

  // Initial reveal for the first image
  const revealFrames = Math.round(fps * 0.6);
  const firstImageOpacity =
    currentIndex === 0
      ? interpolate(frame, [0, revealFrames], [0, 1], {
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        })
      : 1;

  // Crossfade between current and next image
  const transitionStart = perImage - transDur;
  let blendOpacity = 0;

  if (
    transition !== "none" &&
    currentIndex < totalImages - 1 &&
    localFrame >= transitionStart
  ) {
    blendOpacity = interpolate(
      localFrame,
      [transitionStart, perImage],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) }
    );
  }

  // Subtle scale animation on the current image (Ken Burns-lite)
  const scaleProgress = interpolate(localFrame, [0, perImage], [0, 1], {
    extrapolateRight: "clamp",
  });
  const currentScale = 1 + scaleProgress * 0.02; // Very subtle 2% zoom

  const imageStyle: React.CSSProperties = {
    maxWidth: "90%",
    maxHeight: "85%",
    objectFit: "contain" as const,
  };

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor }}>
      {/* Current image */}
      <AbsoluteFill
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: firstImageOpacity * (1 - blendOpacity),
        }}
      >
        <Img
          src={srcs[currentIndex]}
          style={{
            ...imageStyle,
            transform: `scale(${currentScale})`,
          }}
        />
      </AbsoluteFill>

      {/* Next image (fading in) */}
      {blendOpacity > 0 && (
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: blendOpacity,
          }}
        >
          <Img src={srcs[nextIndex]} style={imageStyle} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
