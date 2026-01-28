import React from "react";
import { Composition, registerRoot } from "remotion";
import { AnimatedTitle } from "./compositions/AnimatedTitle";
import { ImageReveal } from "./compositions/ImageReveal";
import { SplitScreen } from "./compositions/SplitScreen";
import { KenBurns } from "./compositions/KenBurns";
import { ImageCarousel } from "./compositions/ImageCarousel";
import { TransitionFade } from "./compositions/TransitionFade";
import { TransitionSlide } from "./compositions/TransitionSlide";
import { TransitionWipe } from "./compositions/TransitionWipe";

// Default dimensions (overridden at render time via inputProps)
const DEFAULT_WIDTH = 1920;
const DEFAULT_HEIGHT = 1080;
const DEFAULT_FPS = 30;
const DEFAULT_DURATION = 150; // 5 seconds

const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnimatedTitle"
        component={AnimatedTitle}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          title: "Title",
          animation: "fade_up" as const,
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="ImageReveal"
        component={ImageReveal}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          imagePath: "",
          effect: "fade" as const,
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="SplitScreen"
        component={SplitScreen}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          leftImagePath: "",
          rightImagePath: "",
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="KenBurns"
        component={KenBurns}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          imagePath: "",
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="ImageCarousel"
        component={ImageCarousel}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          imagePaths: [],
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="TransitionFade"
        component={TransitionFade}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          fromImagePath: "",
          toImagePath: "",
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="TransitionSlide"
        component={TransitionSlide}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          fromImagePath: "",
          toImagePath: "",
          direction: "left" as const,
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
      <Composition
        id="TransitionWipe"
        component={TransitionWipe}
        durationInFrames={DEFAULT_DURATION}
        fps={DEFAULT_FPS}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        defaultProps={{
          fromImagePath: "",
          toImagePath: "",
          direction: "right" as const,
          width: DEFAULT_WIDTH,
          height: DEFAULT_HEIGHT,
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
