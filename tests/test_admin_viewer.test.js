/**
 * @jest-environment jsdom
 */

const fs = require('fs');
const path = require('path');

const scriptContent = fs.readFileSync(path.resolve(__dirname, '../admin.js'), 'utf8');

// ---------------------------------------------------------------------------
// Source-level invariants: the old fake admin surface must never come back.
// These guards make regressions obvious even without a browser.
// ---------------------------------------------------------------------------
describe('admin.js source invariants', () => {
    test('contains no GitHub API calls', () => {
        expect(scriptContent).not.toContain('api.github.com');
        expect(scriptContent).not.toContain('github.com/repos');
    });

    test('contains no credential or token handling', () => {
        expect(scriptContent).not.toContain('ghToken');
        expect(scriptContent).not.toContain('sessionStorage');
        expect(scriptContent).not.toContain('localStorage');
        expect(scriptContent).not.toContain('Authorization');
        expect(scriptContent).not.toContain('token');
    });

    test('contains no client-side password gate', () => {
        expect(scriptContent).not.toContain('ADMIN_PASSWORD_HASH');
        expect(scriptContent).not.toContain('hashPassword');
        expect(scriptContent).not.toContain('checkPassword');
        expect(scriptContent).not.toContain('adminLoggedIn');
    });

    test('contains no write path back to the repository', () => {
        expect(scriptContent).not.toContain('updateManifestOnGithub');
        expect(scriptContent).not.toContain('triggerScraper');
        expect(scriptContent).not.toContain('deleteJob');
        expect(scriptContent).not.toContain('saveJobData');
        expect(scriptContent).not.toContain('method: \'PUT\'');
        expect(scriptContent).not.toContain('method: "PUT"');
    });

    test('fetches the manifest from the same site with a relative URL', () => {
        expect(scriptContent).toMatch(/fetch\(\s*['"]jobs\/job_manifest\.json['"]/);
    });
});

// ---------------------------------------------------------------------------
// Runtime behaviour. admin.js resolves its table elements through
// getElementById at call time, but the DOMContentLoaded listener is
// registered once at load time, so the DOM must exist BEFORE the eval
// (mirrors tests/test_script.test.js).
// ---------------------------------------------------------------------------
document.body.innerHTML = `
    <span id="jobCount">0</span>
    <table>
        <thead>
            <tr><th>Title</th><th>Department</th><th>Category</th><th>Last Date</th></tr>
        </thead>
        <tbody id="jobsTableBody">
            <tr><td colspan="4">Loading job data...</td></tr>
        </tbody>
    </table>`;

eval(scriptContent);

const flushAsync = () => new Promise((resolve) => setTimeout(resolve, 0));

describe('read-only viewer rendering', () => {
    beforeEach(() => {
        jest.restoreAllMocks();
    });

    test('DOMContentLoaded triggers a relative same-origin manifest fetch', async () => {
        const fetchMock = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ total_jobs: 1, jobs: [] })
        });
        global.fetch = fetchMock;

        document.dispatchEvent(new Event('DOMContentLoaded'));
        await flushAsync();

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(fetchMock.mock.calls[0][0]).toBe('jobs/job_manifest.json');
        const opts = fetchMock.mock.calls[0][1] || {};
        expect(opts.headers && opts.headers.Accept).toBe('application/json');
        expect(opts.method).toBeUndefined();
    });

    test('renders jobs as text; a hostile title cannot inject HTML or script', async () => {
        const hostileTitle = '<img src=x onerror=alert(1)><script>alert(2)</script><b>Bold Dept</b>';
        const manifest = {
            total_jobs: 2,
            jobs: [
                {
                    id: 'evil-1',
                    title: hostileTitle,
                    department: '<iframe src="https://evil.example"></iframe>',
                    category: 'UPSC',
                    last_date: '30-11-2026'
                },
                {
                    id: 'ok-1',
                    title: 'RRB NTPC Recruitment 2026',
                    department: 'Railways',
                    important_dates: { last_date: '15-12-2026' }
                }
            ]
        };
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => manifest
        });

        document.dispatchEvent(new Event('DOMContentLoaded'));
        await flushAsync();

        const tbody = document.getElementById('jobsTableBody');
        const rows = tbody.querySelectorAll('tr');
        expect(rows.length).toBe(2);

        // Nothing executable was created from manifest data.
        expect(tbody.querySelectorAll('img, script, iframe, svg, object, embed').length).toBe(0);

        // The hostile strings are present as literal text, not markup.
        const firstTitle = rows[0].querySelector('strong');
        expect(firstTitle.textContent).toBe(hostileTitle);
        expect(rows[0].children[1].textContent).toContain('<iframe');

        // The second row falls back to important_dates.last_date.
        expect(rows[1].children[3].textContent).toBe('15-12-2026');
        expect(document.getElementById('jobCount').textContent).toBe('2');
    });

    test('shows a plain message when the manifest has no jobs', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ total_jobs: 0, jobs: [] })
        });

        document.dispatchEvent(new Event('DOMContentLoaded'));
        await flushAsync();

        const tbody = document.getElementById('jobsTableBody');
        expect(tbody.textContent).toContain('No jobs found.');
    });

    test('HTTP failure renders an error row, never a stack trace', async () => {
        global.fetch = jest.fn().mockResolvedValue({ ok: false, status: 404 });

        document.dispatchEvent(new Event('DOMContentLoaded'));
        await flushAsync();

        const tbody = document.getElementById('jobsTableBody');
        expect(tbody.textContent).toContain('Could not load job data: HTTP 404');
        expect(tbody.querySelectorAll('tr').length).toBe(1);
    });

    test('network failure renders an error row', async () => {
        global.fetch = jest.fn().mockRejectedValue(new Error('network down'));

        document.dispatchEvent(new Event('DOMContentLoaded'));
        await flushAsync();

        const tbody = document.getElementById('jobsTableBody');
        expect(tbody.textContent).toContain('Could not load job data');
    });
});
