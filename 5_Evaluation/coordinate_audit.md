
# Structure Evaluation Coordinate Audit

## Common Ground Truth
- Image: sample.jpg
- EXIF Orientation: 6
- Evaluation image size: 3000 x 4000
- Exhaustive GT: 95 cells
- Upper table: 32 cells
- Lower table: 63 cells
- GT bbox bounds check: PASS

## OpenCV Predictions
- Original source files:
  - cells.json
  - cells_primitive.json
- Recorded image: sample_aligned.png
- Recorded rotation: -1.061 degrees
- Current TestReult.py rotation: 0.0 degrees
- Historical image Git hash: MATCH
- Historical JSON metadata: CONFIRMED
- Original alignment generation history: UNVERIFIED

## Coordinate Conversion
- cells_original.json: inverse-rotation candidate
- cells_primitive_original.json: inverse-rotation candidate
- Overlay inspection: COMPLETED
- Coordinate-system verification: PENDING

## Evaluation Status
- 95 GT cells: CONFIRMED
- IoU thresholds: 0.3, 0.5, 0.7
- metrics_audit_draft.json: GENERATED
- OpenCV performance numbers: PROVISIONAL
- Final Structure Recovery comparison: NOT FINALIZED

## Interpretation
The OpenCV prediction files contain a recorded
rotation of -1.061 degrees, whereas the current
pipeline reports 0.0 degrees on the available image.

The original prediction generation process has
not been fully reconstructed.

Therefore, coordinate-converted OpenCV results
must not yet be treated as finalized performance.

## OpenCV Reproduction Audit

- Input image: sample.jpg
- Input size: 3000 x 4000
- Current pipeline rotation: 0.0 degrees
- Historical JSON rotation: -1.061 degrees
- Detected row boundaries: 0
- Detected column boundaries: 0
- Reproduction status: EXECUTION_FAILED
- Failure stage: Grid extraction
- Root cause: UNCONFIRMED
- Existing cells.json: Preserved
- Existing cells_primitive.json: Preserved
- Final coordinate verification: PENDING

### Interpretation
The current OpenCV pipeline failed to reproduce
the historical structure prediction output.

This is a pipeline reproduction failure,
not a measured structure recovery performance failure.

Historical OpenCV results remain provisional
until their coordinate transformation is verified.

## Inverse Rotation Code Review

- Reviewed script: `make_original.py`
- EXIF orientation handling: CONFIRMED
- Rotation center: Image center
- Transformation: Inverse of `cv2.getRotationMatrix2D`
- Bounding-box conversion: Transform four corners, then calculate enclosing axis-aligned bbox
- Mathematical transformation: CONDITIONALLY VALID
- Historical alignment procedure: UNVERIFIED
- Original `sample_aligned.png`: NOT AVAILABLE
- OpenCV coordinate-system verification: INCOMPLETE

### Audit Conclusion

The inverse-rotation procedure is mathematically consistent with the assumption that the historical OpenCV predictions were generated from an image rotated by -1.061 degrees about its center. However, the original alignment procedure could not be independently verified, and the current pipeline did not reproduce the historical predictions.

Consequently, the converted OpenCV prediction files are treated as coordinate-alignment candidates rather than fully verified evaluation inputs. The corresponding quantitative results remain provisional and are not used to establish a definitive model ranking.