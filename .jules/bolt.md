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

## 2024-05-18 - Pre-computing Regexes in Parser
**Learning:** Recompiling the same date and link regexes thousands of times during Python backend parsing is highly inefficient. Furthermore, checking if strings like `'last'` exist in the pattern name inside a nested loop causes massive redundant logic execution.
**Action:** Always pre-compile `re` expressions at the module level using `re.compile()`. To eliminate redundant string checks in loops, pre-associate the compiled pattern with a predefined string tag using a tuple (e.g., `(re.compile(...), 'tag_name')`).

## 2024-05-18 - Pre-allocating keyword configuration objects in backend
**Learning:** Re-declaring large string arrays and configuration dictionaries inside looping functions and parsers in Python introduces continuous background garbage collection memory overhead and slows execution, especially as parsing job datasets scale upwards. Lookups inside lists have O(N) constraints.
**Action:** Extract inline lists, sets, and static keyword mapping loops out to module-level tuple and set constants. Using frozen module-level constants circumvents GC entirely, and checking against Python `set` provides immediate O(1) keyword detection.

## 2024-05-18 - requestAnimationFrame for smooth animations
**Learning:** Using `setInterval` for DOM animations like increasing counters can lead to choppy performance and continues running even when the browser tab is inactive, wasting CPU and battery life.
**Action:** Always use `window.requestAnimationFrame()` instead of `setInterval` for animations because it automatically synchronizes with the display refresh rate (typically 60fps) and pauses when the user switches away from the tab.

## 2024-05-18 - Unobserving IntersectionObserver
**Learning:** For one-time events triggered by `IntersectionObserver` (like triggering a CSS fade-in animation once when scrolled into view), leaving the element observed means the callback will pointlessly trigger every time it leaves and enters the viewport again.
**Action:** Call `observer.unobserve(entry.target)` immediately after the initial intersection fires to detach the observer and save CPU cycles during scrolling.
