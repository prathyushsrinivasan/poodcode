## Build the confusion matrix before trusting accuracy

A fraud classifier sees 10,000 transactions: 100 fraudulent and 9,900 legitimate. Always predicting “legitimate” achieves 99% accuracy while detecting no fraud. Accuracy answers “what fraction of all predictions were correct?” In a rare-event task, the majority class can dominate that answer.

Suppose a different classifier produces the following results, with fraud as the positive class:

| Actual outcome | Predicted fraud | Predicted legitimate |
| --- | --- | --- |
| Fraud | 60 true positives (TP) | 40 false negatives (FN) |
| Legitimate | 90 false positives (FP) | 9,810 true negatives (TN) |

**Precision** is `TP / (TP + FP) = 60 / 150 = 40%`: of the alerts, how many are real fraud? **Recall** is `TP / (TP + FN) = 60 / 100 = 60%`: of all actual fraud, how much did we detect? Accuracy is `(60 + 9810) / 10000 = 98.7%`. This model has lower accuracy than the useless baseline but detects 60 fraudulent transactions. The business must decide whether those detections justify the false alerts.

F1 is the harmonic mean of precision and recall: `2PR / (P + R) = 0.48` here. It gives one balance, but does not encode every business cost. A precision-recall curve shows tradeoffs across score thresholds, and PR-AUC summarizes that curve. Compare on the same evaluation population: precision depends on prevalence, so a balanced synthetic test set can give a misleading view of production alerts.

## Thresholds convert model scores into decisions

A classifier's score becomes a decision when it crosses a threshold. Lowering the threshold often catches more positives while producing more false positives. Raising it often reduces alert volume and misses more positives. The score is not automatically a well-calibrated probability; check calibration if decisions depend on probability estimates.

Assume a missed fraud costs $100 and a false alert costs $5. The matrix above implies `40 × $100 + 90 × $5 = $4,450` in this simplified cost model. Another threshold yields TP=80, FN=20, FP=300 and TN=9,600: cost becomes `20 × $100 + 300 × $5 = $3,500`. Higher recall is cheaper under these assumptions even though precision falls to `80 / 380 ≈ 21.1%`.

The second threshold also creates 380 alerts instead of 150. If reviewers can handle only 200, the cheaper arithmetic alone is insufficient. Choose on validation using error costs and operational capacity, then report independent test results at the selected threshold. Repeatedly adjusting the threshold against test outcomes turns the test set into a tuning set.

## Address imbalance inside training, preserve evaluation

Class weights make some training errors contribute more to the objective. Oversampling increases minority-class representation in training; undersampling reduces majority examples and can discard useful variation. Synthetic methods interpolate or generate examples under assumptions that may be inappropriate for some domains. More examples do not help if labels or feature availability are wrong.

Split first using the relevant entity/time boundaries, then apply resampling within training only. If oversampled copies cross into evaluation, memorization can look like generalization. Keep validation and test prevalence representative of the operational question, or clearly account for deliberate sampling. A 50/50 fraud test set cannot directly establish the precision expected at 1% prevalence.

Augmentation must preserve the label. Small image changes may help robustness, but rotating a digit can change its identity. Text augmentation that removes “not” changes sentiment; speech augmentation that corrupts a command can change meaning. Inspect the effect by modality and subgroup. Weighting, resampling, augmentation and threshold selection solve related but different problems; evaluate them separately rather than apply all at once.

## Bias is more than an imbalanced target

Class imbalance concerns label frequency. Dataset bias concerns how collection, representation, measurement and labeling differ across relevant populations. An equally sized positive/negative dataset can still omit a language, region, device or demographic group. Removing a sensitive column does not remove proxies such as location or patterns inherited from historical decisions.

Suppose group A has 90 true positives out of 100 actual positives and group B has 10 out of 20. Overall recall is `100 / 120 ≈ 83.3%`, but subgroup recalls are 90% and 50%. The aggregate hides a substantial gap. Small subgroup sample counts create uncertainty, so report denominators and collect more representative data before drawing strong conclusions.

Compare distributions and performance across relevant slices: numeric ranges, missingness, image lighting, text language, audio quality and labeling consistency. Investigate whether the source process or label definition explains a gap. Matching one fairness metric does not prove overall fairness: false-positive rates, recall and predictive values can conflict when base rates differ. Choose task-appropriate criteria with domain stakeholders and keep checking after deployment.

SageMaker Clarify appears in AWS learning materials for bias metrics and explanations. **As of the linked AWS availability guidance, it is closed to new customers; existing customers can continue using it.** Learn the underlying calculations and consult the documented alternatives rather than assume a new account can run a historical demo. For this module, every calculation uses the tables above and requires no AWS account or paid resources.

The retailer can now publish an independent, time-aware evaluation with realistic class prevalence, known subgroup coverage and a threshold selected against explicit costs. This connects the whole module: correct storage and joins preserve examples, consistent features prevent leakage, and quality and bias checks make evaluation credible.
