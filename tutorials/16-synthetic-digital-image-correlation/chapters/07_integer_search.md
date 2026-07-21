# Integer search and initialization

A finite search window evaluates candidate translations on the pixel grid. This stage is robust and easy to visualize, but its resolution is limited to one pixel. Search radius must exceed the expected displacement while remaining small enough to reduce false matches and cost.

Large motion is usually handled with image pyramids, incremental correlation, feature-based initialization, or prediction from neighboring points. The baseline keeps a direct finite search so that failure mechanisms remain visible.
