# AnnotateChange

## Implementation Notes

* Missing values are skipped, so that gaps occur in the graph. X-values are 
  however counted continuously, to ensure that this gap has nonzero width. 
  Thus, when a change point is selected by an annotator after such a gap, its 
  location can be found by retrieving the observation at the index *while 
  including missing values*. This is in contrast to the approach where missing 
  values are removed before the index is used to retrieve the data point.
