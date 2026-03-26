---
title: Stat Filter Testing (v13)
impact: HIGH
impactDescription: Testing pattern for statistical filtering features
tags: test, filter, stat, v13
---

## Stat Filter Testing Pattern

### When to Use

- Testing statistical data filtering
- Testing time range filters
- Testing multi-condition combinations
- Testing aggregation logic (deduplication, accumulation)

---

## Test Categories

| Category | Purpose | Coverage Target |
|----------|---------|------------------|
| Single Filter | Validate individual filter conditions | 100% |
| Boundary | Test edge cases (same day, cross-year, empty) | 100% |
| Combination | Test multi-condition filters | 80%+ |
| Aggregation | Test deduplication and accumulation | 80%+ |

---

## Key Test Patterns

### 1. Exact Value Verification

Always verify exact numeric values, not just structure:

```php
// Wrong: Only check structure
$this->assertArrayHasKey('count', $data);

// Correct: Verify exact value
$this->assertEquals(3, $data['count'], 'Should have 3 records');
```

### 2. Boundary Cases

- Same day range (start = end)
- Cross-year range
- Empty/null values
- Out-of-range values

### 3. Aggregation Logic

- Deduplication: Same entity counted once
- Accumulation: Multiple values summed correctly

---

## Coverage Checklist

- [ ] Single filter conditions work
- [ ] Boundary cases handled
- [ ] Multi-condition combinations work
- [ ] Deduplication logic correct
- [ ] Accumulation logic correct
- [ ] Empty results return 0 (not null)

---

## Related Rules

- [Test TDD First](test-tdd-first.md)
- [Test Transaction](test-transaction.md)
