# -*- coding: utf-8 -*-
"""Sliding window: Python reference implementations.

Every expected output, trace table and stepper frame in the topic is computed
from these, never typed by hand. tools/verify_new_dsa.py then proves each
TypeScript solution agrees with them on every test case.
"""

VOWELS = set("aeiou")
MINSTD = 2147483647


def max_sum_window(nums, k):
    s = sum(nums[:k])
    best = s
    for hi in range(k, len(nums)):
        s += nums[hi] - nums[hi - k]
        best = max(best, s)
    return best


def count_good_windows(nums, k, threshold):
    return sum(1 for lo in range(len(nums) - k + 1) if sum(nums[lo:lo + k]) >= k * threshold)


def longest_unique(s):
    best = 0
    for lo in range(len(s)):
        seen = set()
        for hi in range(lo, len(s)):
            if s[hi] in seen:
                break
            seen.add(s[hi])
            best = max(best, hi - lo + 1)
    return best


def longest_sum_at_most(nums, limit):
    best = 0
    for lo in range(len(nums)):
        for hi in range(lo, len(nums)):
            if sum(nums[lo:hi + 1]) <= limit:
                best = max(best, hi - lo + 1)
    return best


def longest_k_distinct(s, k):
    best = 0
    for lo in range(len(s)):
        for hi in range(lo, len(s)):
            if len(set(s[lo:hi + 1])) <= k:
                best = max(best, hi - lo + 1)
    return best


def min_len_sum_at_least(nums, target):
    best = 0
    for lo in range(len(nums)):
        for hi in range(lo, len(nums)):
            if sum(nums[lo:hi + 1]) >= target:
                if best == 0 or hi - lo + 1 < best:
                    best = hi - lo + 1
                break
    return best


def longest_ones_k_flips(bits, k):
    best = 0
    for lo in range(len(bits)):
        for hi in range(lo, len(bits)):
            if bits[lo:hi + 1].count(0) <= k:
                best = max(best, hi - lo + 1)
    return best


def max_char_count(s):
    return max((s.count(c) for c in set(s)), default=0)


def distinct_letters(s):
    return len(set(s))


def max_vowels(s, k):
    return max(sum(1 for c in s[lo:lo + k] if c in VOWELS) for lo in range(len(s) - k + 1))


def count_product_less(nums, k):
    count = 0
    for lo in range(len(nums)):
        p = 1
        for hi in range(lo, len(nums)):
            p *= nums[hi]
            if p < k:
                count += 1
            else:
                break
    return count


def longest_distinct_values(nums):
    best = 0
    for lo in range(len(nums)):
        seen = set()
        for hi in range(lo, len(nums)):
            if nums[hi] in seen:
                break
            seen.add(nums[hi])
            best = max(best, hi - lo + 1)
    return best


def exactly_k_distinct(nums, k):
    return sum(
        1
        for lo in range(len(nums))
        for hi in range(lo, len(nums))
        if len(set(nums[lo:hi + 1])) == k
    )


def window_maxima(nums, k):
    return [max(nums[lo:lo + k]) for lo in range(len(nums) - k + 1)]


def window_maxima_fast(nums, k):
    """The deque version, for the generated large case only (the brute force
    above would take hours there). Cross-checked against it in new_dsa.py."""
    from collections import deque
    dq, out = deque(), []
    for hi, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(hi)
        if dq[0] <= hi - k:
            dq.popleft()
        if hi >= k - 1:
            out.append(nums[dq[0]])
    return out


def minstd(count, seed):
    """The generator the large-case harness uses, bit for bit: Park-Miller
    MINSTD. Products stay below 2^47, so JavaScript numbers compute it exactly."""
    x, out = seed, []
    for _ in range(count):
        x = (x * 48271) % MINSTD
        out.append(x % 1000)
    return out


def longest_at_most_twice(s):
    best = 0
    for lo in range(len(s)):
        for hi in range(lo, len(s)):
            w = s[lo:hi + 1]
            if all(w.count(c) <= 2 for c in set(w)):
                best = max(best, hi - lo + 1)
    return best


def count_k_len_no_repeat(s, k):
    return sum(1 for lo in range(len(s) - k + 1) if len(set(s[lo:lo + k])) == k)


# ---------------------------------------------------------------------------
# Traces — simulate the TypeScript shown in the lesson, step by step
# ---------------------------------------------------------------------------

def unique_frames(s):
    """Stepper frames for longestUnique(s): one per absorb / release / measure."""
    frames, seen, lo, best = [], [], 0, 0

    def snap(hi, action, note):
        frames.append({
            "lo": lo, "hi": hi, "action": action, "note": note,
            "state": "{ " + ", ".join(seen) + " }" if seen else "{ }",
            "best": best,
        })

    snap(-1, "start", "Empty window: lo = 0, hi has not moved yet. best = 0.")
    for hi, c in enumerate(s):
        while c in seen:
            gone = s[lo]
            seen.remove(gone)
            lo += 1
            snap(hi, "release",
                 f"'{c}' is already inside, so the window would repeat it. Release s[{lo - 1}] = '{gone}' and move lo to {lo}.")
        seen.append(c)
        snap(hi, "absorb", f"Absorb s[{hi}] = '{c}'. The window [{lo}, {hi}] has no repeats.")
        if hi - lo + 1 > best:
            best = hi - lo + 1
            snap(hi, "measure", f"Measure: length {hi} − {lo} + 1 = {best}. New best.")
        else:
            snap(hi, "measure", f"Measure: length {hi - lo + 1}, not better than best = {best}.")
    snap(len(s) - 1, "done", f"hi has visited every index once; lo only ever moved forward. Answer: {best}.")
    return frames


def max_sum_rows(nums, k):
    rows = []
    s = sum(nums[:k])
    best = s
    rows.append([f"{k - 1}", "first k", "—", str(nums[:k]).replace(",", ","), str(s), str(best)])
    for hi in range(k, len(nums)):
        s += nums[hi] - nums[hi - k]
        best = max(best, s)
        rows.append([str(hi), f"+{nums[hi]}", f"−{nums[hi - k]}", str(nums[hi - k + 1:hi + 1]), str(s), str(best)])
    return rows


def unique_rows(s):
    rows, seen, lo, best = [], set(), 0, 0
    for hi, c in enumerate(s):
        released = []
        while c in seen:
            seen.discard(s[lo])
            released.append(s[lo])
            lo += 1
        seen.add(c)
        best = max(best, hi - lo + 1)
        rows.append([str(hi), f"'{c}'", ", ".join(f"'{r}'" for r in released) or "—",
                     f'"{s[lo:hi + 1]}"', str(hi - lo + 1), str(best)])
    return rows
