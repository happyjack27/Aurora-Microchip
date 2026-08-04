Expand every RTL module specification to implementation-ready quality.

| Priority | Module                     | Reason                         |
|----------|----------------------------|--------------------------------|
| 1        | Decode & Issue Window      | Architectural heart of Aurora  |
| 2        | Register File & Scoreboard | Defines hazards and forwarding |
| 3        | Execution Lanes            | Largest instruction coverage   |
| 4        | Multiplier & Reduction     | DSP differentiator             |
| 5        | Load/Store Unit            | Memory correctness             |
| 6        | Remaining modules          | Follow dependency order        |
