#!/usr/bin/env node
/**
 * Remotion render bridge - called by Python via subprocess.
 *
 * Usage:
 *   echo '{}' | node render.mjs bundle
 *   echo '{}' | node render.mjs render
 *
 * JSON args are read from stdin. All output is JSON on stdout.
 */

import { bundle } from "@remotion/bundler";
import { renderMedia, getCompositions } from "@remotion/renderer";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const action = process.argv[2];
if (!action) {
  console.error("Usage: node render.mjs <bundle|render>");
  process.exit(1);
}

// Read JSON args from stdin
const chunks = [];
for await (const chunk of process.stdin) {
  chunks.push(chunk);
}
const args = JSON.parse(Buffer.concat(chunks).toString());

async function main() {
  switch (action) {
    case "bundle": {
      const entryPoint = args.entryPoint || path.join(__dirname, "src/index.tsx");
      const serveUrl = await bundle({
        entryPoint,
        outDir: args.outDir || undefined,
        webpackOverride: (config) => config,
      });
      console.log(JSON.stringify({ serveUrl }));
      break;
    }

    case "render": {
      const {
        serveUrl,
        compositionId,
        outputPath,
        inputProps = {},
        durationInFrames,
        fps,
        width,
        height,
        concurrency,
        chromiumExecutable,
        logLevel = "warn",
      } = args;

      if (!serveUrl || !compositionId || !outputPath) {
        throw new Error("serveUrl, compositionId, and outputPath are required");
      }

      const compositions = await getCompositions(serveUrl, {
        inputProps,
        logLevel,
      });

      const composition = compositions.find((c) => c.id === compositionId);
      if (!composition) {
        const available = compositions.map((c) => c.id).join(", ");
        throw new Error(
          `Composition "${compositionId}" not found. Available: ${available}`
        );
      }

      await renderMedia({
        composition: {
          ...composition,
          ...(durationInFrames && { durationInFrames }),
          ...(fps && { fps }),
          ...(width && { width }),
          ...(height && { height }),
        },
        serveUrl,
        codec: "h264",
        outputLocation: outputPath,
        inputProps,
        ...(concurrency && { concurrency }),
        ...(chromiumExecutable && { chromiumExecutable }),
        logLevel,
      });

      console.log(JSON.stringify({ success: true, outputPath }));
      break;
    }

    default:
      throw new Error(`Unknown action: ${action}. Use bundle or render.`);
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
