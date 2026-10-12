# New image model requirement

User requirement: All newly generated images for this project must use GPT Image 2.5, including after migration to another computer.

- Applies to new generation and new image-edit/repair calls from this instruction onward. Preserve existing images; no wholesale regeneration is requested.
- Use a route that explicitly selects a verified GPT Image 2.5 model. Do not label an unspecified built-in image tool as 2.5 or silently fall back to GPT Image 2.
- If no verifiable 2.5 route is available, pause new generation, report the limitation, and continue local inventory, assembly, review, and upload of existing assets where possible.
- This model preference does not authorize paid API usage, API spending, new subscriptions, or credential changes. The user's existing no-paid-API instruction remains in force until explicitly changed.
- Record the requested exact image model, route, and returned model metadata when available; distinguish requested model from independently confirmed actual model.
- This concerns the image generator, not the Sol model used to coordinate work.
- Carry this file with the project to every new computer and read it before resuming image generation. A separate computer/chat must have this project instruction available to apply it.

Installation and route verification were requested for after current map work; the new model requirement nevertheless forbids further unverified/2.0 generation now. Do not bypass it to finish the queue.
