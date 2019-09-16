# AnnotateChange

## Implementation Notes

* Missing values are skipped, so that gaps occur in the graph. X-values are 
  however counted continuously, to ensure that this gap has nonzero width. 
  Thus, when a change point is selected by an annotator after such a gap, its 
  location can be found by retrieving the observation at the index *while 
  including missing values*. This is in contrast to the approach where missing 
  values are removed before the index is used to retrieve the data point.

* Task assignment flow: tasks assignment is handled upon login, completion of 
  the demo, and completion of an annotation.

  General rules:

  - [x] Users don't get a task assigned if they still have an unfinished task
  - [x] Users don't get a task assigned if there are no more datasets to 
    annotate
  - [x] Users don't get a task assigned if they have reached their maximum.
  - [x] Users never get assigned the same dataset more than once
  - [x] Tasks are assigned on the fly, at the moment that a user requests a 
    dataset to annotate.

  Handled at login:

  - [x] When a user logs in, a task that was previously assigned that is not 
    finished should be removed to avoid duplication, unless this task was 
    assigned by the admin.

  It may be easier to remove assigning a *specific* dataset and instead give 
  the user the option to "annotate again". If they click that, they get 
  assigned a task on the fly. This will remove a lot of the difficulties.
