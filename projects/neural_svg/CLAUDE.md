# NeuralSVG Video

## Source
https://sagipolaczek.github.io/NeuralSVG/

## Project Info
- **Title:** NeuralSVG: An Implicit Representation for Text-to-Vector Generation
- **Authors:** Sagi Polaczek, Yuval Alaluf, Elad Richardson, Yael Vinker, Daniel Cohen-Or
- **Affiliations:** Tel Aviv University, MIT CSAIL
- **Venue:** ICCV 2025
- **Paper:** https://arxiv.org/abs/2501.03992
- **Code:** https://github.com/SagiPolaczek/NeuralSVG

## Assets

| File | Description | Status |
|------|-------------|--------|
| teaser.png | Hero image showing method overview | OK |
| method.png | Architecture diagram | OK |
| generation_1.png | Text-to-vector examples row 1 | OK |
| generation_2.png | Text-to-vector examples row 2 | OK |
| generation_3.png | Text-to-vector examples row 3 | OK |
| generation_4.png | Text-to-vector examples row 4 | OK |
| dropout_rooster.png | Dropout regularization example (rooster) | OK |
| dropout_astronaut.png | Dropout regularization example (astronaut) | OK |
| control_color_spaceship.png | Color palette control (spaceship) | OK |
| control_color_ming.png | Color palette control (vase) | OK |
| aspect_sportscar.png | Aspect ratio control (sports car) | OK |
| aspect_penguin.png | Aspect ratio control (penguin) | OK |
| aspect_hat.png | Aspect ratio control (hat) | OK |
| sketch_ballerina.png | Sketch generation (ballerina) | OK |
| sketch_margarita.png | Sketch generation (margarita) | OK |

## Video Plan

| # | Segment | Duration | Section | Description |
|---|---------|----------|---------|-------------|
| 1 | title | 4s | - | Title card with paper name and venue |
| 2 | teaser | 5s | Introduction | Show teaser - hook the viewer |
| 3 | method | 8s | Method | Explain the neural implicit approach |
| 4 | generation | 6s | Results | Show text-to-vector generation examples |
| 5 | dropout | 6s | Results | Demonstrate layered structure via dropout |
| 6 | color_control | 6s | Control | Show color palette conditioning |
| 7 | aspect_ratio | 6s | Control | Show aspect ratio flexibility |
| 8 | sketches | 5s | Control | Show sketch generation mode |
| 9 | conclusion | 4s | - | Closing with links |

**Total:** ~50 seconds

## Narration Script

1. **Title:** "NeuralSVG: An Implicit Representation for Text-to-Vector Generation. Presented at ICCV 2025."

2. **Teaser:** "NeuralSVG generates high-quality vector graphics from text descriptions, producing clean, layered SVG structures ready for design applications."

3. **Method:** "We encode the entire scene into a small MLP network, inspired by NeRF. The network is optimized using Score Distillation Sampling, and dropout regularization encourages an ordered, layered structure."

4. **Generation:** "Given a text prompt, NeuralSVG produces detailed vector graphics. Here we see examples ranging from animals to objects, each rendered as a clean SVG."

5. **Dropout:** "Our dropout-based regularization creates naturally layered outputs. As we decrease dropout probability, the SVG structure emerges progressively from coarse to fine details."

6. **Color Control:** "A single learned representation enables runtime control over color palettes. The same generation can be conditioned on different color schemes without retraining."

7. **Aspect Ratio:** "NeuralSVG supports dynamic aspect ratio adjustment at inference time, adapting the output to various canvas shapes while maintaining visual quality."

8. **Sketches:** "The method can also generate black and white sketches, useful for line art and illustration workflows."

9. **Conclusion:** "Thank you for watching. Visit the project page for code, paper, and more examples."

## Notes
- Focus on the key technical contributions: implicit representation and dropout regularization
- Highlight the inference-time control capabilities (color, aspect ratio, sketch)
- Keep narration concise and technical but accessible
