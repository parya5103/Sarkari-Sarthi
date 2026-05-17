/**
 * @jest-environment jsdom
 */

// Define window.location with an absolute base
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost/'
  }
});

const fs = require('fs');
const path = require('path');

const scriptContent = fs.readFileSync(path.resolve(__dirname, '../script.js'), 'utf8');

// Load script.js functions into the global scope
eval(scriptContent);

describe('sanitizeURL', () => {
    test('should return "#" for falsy urls', () => {
        expect(sanitizeURL('')).toBe('#');
        expect(sanitizeURL(null)).toBe('#');
        expect(sanitizeURL(undefined)).toBe('#');
    });

    test('should return correct URL for http and https with proper URL resolution', () => {
        // Because the implementation uses \`new URL(url, window.location.href).href\`,
        // simple http:// URLs will have a trailing slash appended.
        expect(sanitizeURL('http://example.com')).toBe('http://example.com/');
        expect(sanitizeURL('https://example.com')).toBe('https://example.com/');
        expect(sanitizeURL('http://example.com/path?query=1')).toBe('http://example.com/path?query=1');
    });

    test('should resolve relative paths against window.location.href safely', () => {
        // Since we mocked window.location.href to 'http://localhost/', relative paths will resolve against it.
        expect(sanitizeURL('/path/to/resource')).toBe('http://localhost/path/to/resource');
        expect(sanitizeURL('./path/to/resource')).toBe('http://localhost/path/to/resource');
        expect(sanitizeURL('../path/to/resource')).toBe('http://localhost/path/to/resource');
    });

    test('should return "#" for blocked protocols like javascript:', () => {
        expect(sanitizeURL('javascript:alert(1)')).toBe('#');
        expect(sanitizeURL('  JaVaScRiPt:alert(1)')).toBe('#');
        expect(sanitizeURL('data:text/html,<html>')).toBe('#');
        expect(sanitizeURL('vbscript:msgbox("hello")')).toBe('#');
    });

    test('should fallback to escaping for unparseable URLs that start with relative characters', () => {
        // An invalid URL format might cause `new URL` to throw. We can force a throw by overriding `URL`
        // or passing a completely broken URL. However, the browser's URL parser is very permissive.
        // Let's create a test case that forces an error.
        const originalURL = global.URL;
        global.URL = function() { throw new Error('mock error'); };

        expect(sanitizeURL('/relative-path')).toBe('/relative-path');
        expect(sanitizeURL('./relative-path')).toBe('./relative-path');

        // Restore URL
        global.URL = originalURL;
    });
});
