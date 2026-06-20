## Samples

1. A **sampler** creates a sample from *LIMS > Samples*:
   - Set the customer, sample type, and collection date.
   - Add the analyses to perform on the sample.
   - Click **Receive** when the physical sample arrives, or use **Next Stage** to advance the sample manually.

2. An **analyst** enters the result value on each analysis line and clicks ✓ (Analyze) to submit it for verification.

3. A **verifier** (different from the analyst by default) clicks ● (Verify) on each submitted analysis. Once all analyses are verified the sample advances to *Verified* automatically.

## Sample stage workflow

```
Registered → Scheduled Sampling → Sample due → Received
           → To be verified → Verified → Published
                                        → Cancelled
                                        → Invalid
```

## Analysis stage workflow

```
Registered → To Analyze → To be Verified → Verified
                                          → Rejected (terminal)
```

The **Receive** button moves the sample from *Sample due* to *Received*
and simultaneously advances all its analyses from *Registered* to *To Analyze*.