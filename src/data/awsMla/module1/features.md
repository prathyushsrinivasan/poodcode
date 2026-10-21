## A feature is an executable definition

A feature is a model input derived from available information: purchase amount, count of orders in seven days, or an encoded product category. Its definition includes units, time window, missing-value policy and version. `spend_7d` in dollars is different from `spend_7d` in cents, even if the column name is unchanged. Train and serve with the same definition and fitted parameters.

Choose a transformation engine from the work it must do. AWS Glue provides managed data integration and ETL, often using Spark. Amazon EMR provides broader control over big-data frameworks and their runtime configuration. SageMaker Processing runs preparation or evaluation code in managed jobs near an ML workflow. DataBrew offers visual data preparation; SageMaker Data Wrangler is available through Canvas for visual ML preparation. Lambda can perform short, bounded event transformations, but it is a poor place to keep durable rolling-window state across independent invocations. Flink is designed for stateful stream processing.

A prototype in a visual tool still needs a repeatable production transformation. Save its flow or exported processing definition, input schema, parameters and tests against representative records. The objective is to run the same computation repeatedly, including on future data.

## Work through numeric transformations

Different transformations solve different problems. **Min-max scaling** maps a training range to a selected range, often 0–1: `(x - min) / (max - min)`. With training minimum 10 and maximum 50, a value of 30 becomes `(30 - 10) / 40 = 0.5`. A future value of 70 becomes 1.5 unless clipping is explicitly part of the fitted transformation. Recomputing the minimum and maximum on each production batch changes the meaning of the inputs.

**Standardization** uses `(x - mean) / standard_deviation`. With training mean 40 and standard deviation 10, a value of 60 becomes 2: two training standard deviations above the mean. It does not guarantee a bell-shaped distribution. Handle zero variance explicitly rather than divide by zero. Distance-based methods and gradient optimization often benefit from comparable numeric scales; tree-based splits usually do not need scaling for the same reason.

**Log transformation** compresses a long right tail. `log1p(x)` means `ln(1 + x)`, allowing a nonnegative value of zero. Counts of 0, 9 and 99 become approximately 0, 2.30 and 4.61. This changes relative distances. It is not valid for arbitrary negative values without a different policy. **Binning** groups continuous values, such as ages into intervals. Quantile boundaries must be learned from training data; fixed business boundaries can be authored in advance. Binning trades detail for a simpler representation.

For categories, one-hot encoding creates indicators rather than pretending category IDs have an ordered numeric distance. Define behavior for unseen categories. Target encoding uses label statistics and therefore needs special leakage controls, such as out-of-fold construction inside training. Do not compute a category's average outcome using the holdout labels.

## Split first, fit second, transform consistently

Training data fits model and preprocessing parameters. Validation data selects settings. Test data provides a final independent estimate. If you compute a median, scaler or vocabulary on all three first, information from evaluation has entered training. This is **data leakage**, even if you never explicitly use the test label.

```text
raw examples
  -> split by time/entity according to the prediction task
  -> fit imputer + encoder + scaler on TRAIN only
  -> transform TRAIN, VALIDATION and TEST with those fitted objects
  -> train and choose settings using validation
  -> evaluate the selected pipeline on test
```

Suppose training incomes are 20, 30 and missing, while a future test income is 1,000. A training median of 25 is the valid imputation parameter. Including the future value changes the median and makes training depend on information it would not yet have. If you compare multiple imputers, select using validation, not repeated test-set inspection.

Random splitting is appropriate only when it matches the intended independent examples. For next-month demand, a chronological split better resembles deployment. For generalization to unseen patients, keep every record of one patient in a single split. Stratification can preserve class proportions within those constraints; it cannot override the need for independence.

## Worked example: reconstruct what was actually available

At 10:00, a customer makes a purchase. A support ticket opens at 09:00 and closes at 15:00. A fraud label arrives three days later. A training row predicting fraud at 10:00 may use the ticket's existence, but cannot use its eventual resolution or the later fraud label as a feature.

Now imagine a device event occurred at 09:55 but was not ingested until 10:10. Its event timestamp precedes checkout, yet the production system did not know about it at 10:00. An honest historical reconstruction may need both event time and availability time. A point-in-time join selects the appropriate entity record as of the prediction boundary and excludes information unavailable then. Merely joining the latest online record leaks the future.

Keep feature lineage from raw events through transformation version to fitted parameters and training manifest. At serving time reuse that artifact rather than refit it. Monitor missing rates, unseen categories and transformed ranges to detect changes. A value outside the original 0–1 range is a signal to investigate; silently refitting the scaler at inference hides the change and creates training-serving skew.

For streaming features such as five-minute spending, specify window boundaries, timezone and late-data handling in the feature definition. Otherwise batch training can calculate a complete historical window while online inference sees an incomplete one. Reusing a name does not establish computational equivalence.
