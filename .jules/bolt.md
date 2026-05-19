## 2024-05-18 - DocumentFragment for DOM insertions
**Learning:** Appending DOM nodes individually inside loops using `appendChild` directly to a live DOM element causes excessive layout thrashing and reflows/repaints, making the UI rendering performance very slow, especially with large numbers of elements.
**Action:** Always batch append operations using `document.createDocumentFragment()` before appending the fragment to the live DOM in a single operation. This updates the DOM only once, resulting in measurable rendering speedups.

## 2024-05-18 - Avoiding Date Parsing in Sort Loops
**Learning:** Parsing string dates into `Date` objects inside of `Array.prototype.sort()` callbacks is a massive frontend performance bottleneck because the `O(N log N)` comparison algorithm will cause multiple instantiations and garbage collections per item.
**Action:** Extract parts of formatted date strings (e.g. DD-MM-YYYY) into raw sortable numeric integers (e.g. YYYYMMDD via `parseInt(dateStr.substring(6, 10) + dateStr.substring(3, 5) + dateStr.substring(0, 2))`) for `O(1)` numeric comparison without memory allocation.

## 2024-05-18 - Pre-computing Search Strings
**Learning:** Calling `toLowerCase()` on multiple fields per item during a real-time keystroke filter causes thousands of string allocations and massive garbage collection pressure, leading to UI stuttering.
**Action:** Pre-compute a combined lowercase search string for each item once when data is loaded, reducing the per-keystroke cost from O(N * fields) to a single `O(1)` substring check per item.

- When evaluating the performance impact of offloading a synchronous call to `asyncio.to_thread()`, use a concurrently running `asyncio.create_task` loop to act as a counter that registers ticks. If the event loop is blocked by synchronous code, the counter will remain low (or 0). By using `asyncio.to_thread()`, the counter demonstrates that the event loop remained responsive while the thread executed the blocking task.
- Be extremely careful not to accidentally mock global `asyncio` methods (like `asyncio.sleep`) during benchmarks, as doing so will prevent concurrent tasks from yielding and executing, invalidating the benchmark.

## 2024-05-18 - Pre-computing Regex and Eliminating Substring Checks
**Learning:** Re-compiling regex dynamically on every function call for every scraped job causes unnecessary overhead. Furthermore, performing substring checks on the regex pattern string itself (e.g., `'last' in pattern.lower()`) inside the nested `for match in matches` loop is highly inefficient.
**Action:** For optimal backend parsing performance in Python, pre-compile regular expressions at the module level using `re.compile()`. When iterating over multiple regex patterns, avoid dynamic substring checks on the pattern string (e.g., `'text' in pattern`) within loops; instead, associate patterns with predefined tags using tuples (e.g., `(re.compile(...), 'tag_name')`) to eliminate redundant logic execution.
