## 2024-05-18 - DocumentFragment for DOM insertions
**Learning:** Appending DOM nodes individually inside loops using `appendChild` directly to a live DOM element causes excessive layout thrashing and reflows/repaints, making the UI rendering performance very slow, especially with large numbers of elements.
**Action:** Always batch append operations using `document.createDocumentFragment()` before appending the fragment to the live DOM in a single operation. This updates the DOM only once, resulting in measurable rendering speedups.

## 2024-05-18 - Avoiding Date Parsing in Sort Loops
**Learning:** Parsing string dates into `Date` objects inside of `Array.prototype.sort()` callbacks is a massive frontend performance bottleneck because the `O(N log N)` comparison algorithm will cause multiple instantiations and garbage collections per item.
**Action:** Extract parts of formatted date strings (e.g. DD-MM-YYYY) into raw sortable numeric integers (e.g. YYYYMMDD via `parseInt(dateStr.substring(6, 10) + dateStr.substring(3, 5) + dateStr.substring(0, 2))`) for `O(1)` numeric comparison without memory allocation.

## 2024-05-18 - Pre-computing Search Strings
**Learning:** Calling `toLowerCase()` on multiple fields per item during a real-time keystroke filter causes thousands of string allocations and massive garbage collection pressure, leading to UI stuttering.
**Action:** Pre-compute a combined lowercase search string for each item once when data is loaded, reducing the per-keystroke cost from O(N * fields) to a single `O(1)` substring check per item.
