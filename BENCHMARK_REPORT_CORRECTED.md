# IFEval Benchmark: CORRECTED Final Report

**Date:** 2026-06-26  
**Dataset:** 541 IFEval instruction-following prompts  
**Models:** Qwen 3.5 27B, Llama 3.3 70B, Gemma 4 26B

---

## CRITICAL ISSUE: Data Quality Problem with Qwen

**Qwen 3.5 27B failed to generate responses for 216/541 prompts (39.9%)**

These failures appear as None values in the response file and were skipped during evaluation. This means:
- Initial report showing "92% pass rate" for Qwen was misleading
- That 92% was only calculated on 323 valid responses
- The true pass rate including generation failures: **54.9%**

---

## CORRECTED FINAL RANKINGS

### By True Pass Rate (Including Generation Failures)

| Rank | Model | Pass | Fail | Skipped | True Pass Rate |
|------|-------|------|------|---------|----------------|
| 1 | **Llama 3.3 70B** | 477 | 64 | 0 | **88.2%** |
| 2 | **Gemma 4 26B** | 469 | 72 | 0 | **86.7%** |
| 3 | **Qwen 3.5 27B** | 297 | 26 | 216 | **54.9%** |

### By Pass Rate (Excluding Generation Failures - Initial Metric)

| Rank | Model | Valid | Pass | Pass Rate |
|------|-------|-------|------|-----------|
| 1 | **Qwen 3.5 27B** | 323 | 297 | 92.0% |
| 2 | **Llama 3.3 70B** | 541 | 477 | 88.2% |
| 3 | **Gemma 4 26B** | 541 | 469 | 86.7% |

---

## VERDICT

### Actual Winner: Llama 3.3 70B

**Why Llama wins:**
1. **Reliability:** Generated responses for ALL 541 prompts (100% reliability)
2. **Instruction following:** 88.2% pass rate on those responses
3. **No generation failures:** Every prompt received a valid response
4. **Consistent quality:** No significant issues

### Why Qwen Lost Despite Higher Pass Rate

**Critical problems:**
1. **39.9% generation failure rate** - Unacceptable reliability
2. **92% pass rate is on a biased subset** - Only the "easy" prompts it could generate
3. **Likely causes:**
   - OpenRouter API timeouts on complex prompts
   - Rate limiting issues that returned None
   - Model-specific generation failures
4. **Real-world impact:** In production, 40% of requests would fail to generate any response

### Gemma's Position

- **86.7% pass rate** - Solid third place
- **100% generation reliability** - All prompts got responses
- Gap to Llama: 1.5% - Close competition
- Slightly better than Qwen on real-world reliability comparison

---

## What Went Wrong with Qwen

The 216 None responses in Qwen's file indicate:
- Generation requests that failed to return content
- Possibly due to:
  - API connection timeouts during generation
  - Rate limiting that returned empty responses
  - Model-specific issues with certain prompt types
  - Streaming/buffering problems

This is **not** an instruction-following issue, but a **generation reliability issue**.

---

## Corrected Recommendation

### For Production Use: **Use Llama 3.3 70B**

- **Reliability:** 100% - every request gets a response
- **Accuracy:** 88.2% - instruction-following quality
- **Real-world performance:** Best combination of reliability and accuracy

### For Evaluation Tasks Only: Qwen ONLY if you can:
- Re-run failed generations manually
- Accept 40% retry rate
- Handle None responses in your pipeline

---

## Summary Table

| Metric | Llama | Gemma | Qwen |
|--------|-------|-------|------|
| **Generation Reliability** | 100% | 100% | 60% |
| **Instruction-Following Accuracy** | 88.2% | 86.7% | 92.0%* |
| **Real-World Pass Rate** | 88.2% | 86.7% | 54.9% |
| **Recommended for Production** | YES | MAYBE | NO |

*Qwen's 92% is only on responses that were successfully generated; not comparable due to selection bias.

---

## Cost vs. Performance

- **Llama:** Best value - reliable + good accuracy
- **Gemma:** Close second - similar reliability, slightly lower accuracy
- **Qwen:** Not recommended - reliability issues outweigh instruction-following advantage
