/**
 * GoGo Central Notifications module tests (Sarkari Sarthi).
 * MOCKED: the module is evaluated against a fake window in plain Node. No
 * Firebase SDK, no service worker, no Notification API and no network are
 * involved. These tests validate the fail-closed config gate and the exact
 * request payload shapes only. They do NOT prove live FCM delivery -
 * live delivery is a manual post-deployment verification step.
 */
const fs = require('fs');
const path = require('path');

const moduleSrc = fs.readFileSync(path.resolve(__dirname, '../gogo-notifications.js'), 'utf8');
const swSrc = fs.readFileSync(path.resolve(__dirname, '../firebase-messaging-sw.js'), 'utf8');
const indexHtml = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

const fakeWindow = {};
new Function('window', moduleSrc)(fakeWindow);
const GoGoNotifications = fakeWindow.GoGoNotifications;

describe('GoGo Central notifications module (MOCKED)', () => {
  test('exposes its testable API and stays inert outside the browser', () => {
    expect(GoGoNotifications).toBeDefined();
    expect(typeof GoGoNotifications.internals.validateConfig).toBe('function');
    expect(typeof GoGoNotifications.internals.buildRegisterPayload).toBe('function');
    expect(typeof GoGoNotifications.internals.buildPreferencePayload).toBe('function');
    expect(typeof GoGoNotifications.internals.safeUrl).toBe('function');
    expect(GoGoNotifications.config.appId).toBe('sarkari-sarthi');
    expect(GoGoNotifications.config.swUrl).toBe('firebase-messaging-sw.js');
  });

  test('fail-closed: empty apiBase/vapidPublicKey disables the whole feature', () => {
    const v = GoGoNotifications.internals.validateConfig();
    expect(v.ok).toBe(false);
    expect(v.disabled).toBe(true);
    expect(v.problems.some((p) => p.includes('API base'))).toBe(true);
    expect(v.problems.some((p) => p.includes('VAPID'))).toBe(true);
    const v2 = GoGoNotifications.internals.validateConfig({
      appId: 'sarkari-sarthi',
      apiBase: 'https://gogo-central-backend.example.run.app/',
      vapidPublicKey: 'BExampleVapidPublicKey000000000000000',
    });
    expect(v2.ok).toBe(true);
    expect(v2.disabled).toBe(false);
  });

  test('register payload matches the backend contract', () => {
    const payload = GoGoNotifications.internals.buildRegisterPayload(
      { appId: 'sarkari-sarthi' },
      'fcm-web-token-abcdefgh1234567890',
      'Mozilla/5.0 (Linux; Android 15) TestAgent/1.0'
    );
    expect(payload).toEqual({
      appId: 'sarkari-sarthi',
      fcmToken: 'fcm-web-token-abcdefgh1234567890',
      platform: 'web',
      userAgent: 'Mozilla/5.0 (Linux; Android 15) TestAgent/1.0',
    });
    const fallback = GoGoNotifications.internals.buildRegisterPayload({ appId: 'x' }, 'tok-1234567890abcdef');
    expect(fallback.userAgent).toBe('unknown-web');
  });

  test('preference payload toggles every channel together with quiet hours', () => {
    const on = GoGoNotifications.internals.buildPreferencePayload(true);
    expect(on).toEqual({
      enabled: true,
      webPush: true,
      androidPush: true,
      marketingAlerts: true,
      transactionalAlerts: true,
      quietHoursStart: '22:00',
      quietHoursEnd: '06:00',
    });
    const off = GoGoNotifications.internals.buildPreferencePayload(false);
    expect(off.enabled).toBe(false);
    expect(off.webPush).toBe(false);
    expect(off.androidPush).toBe(false);
    expect(off.quietHoursStart).toBe('22:00');
    expect(off.quietHoursEnd).toBe('06:00');
  });

  test('safeUrl opens only GoGo domains; everything else falls back to the portal', () => {
    const safeUrl = GoGoNotifications.internals.safeUrl;
    expect(safeUrl('https://gogocompany.in/')).toBe('https://gogocompany.in/');
    expect(safeUrl('https://gogocompany.in/sarkari-sarthi/')).toBe('https://gogocompany.in/sarkari-sarthi/');
    expect(safeUrl('https://evil.example.org/phish')).toBe('https://gogocompany.in/');
    expect(safeUrl('javascript:alert(1)')).toBe('https://gogocompany.in/');
    expect(safeUrl('')).toBe('https://gogocompany.in/');
    expect(safeUrl(null)).toBe('https://gogocompany.in/');
  });

  test('background worker invariants: messaging handler, dedupe tag, click focus, NO fetch handler', () => {
    expect(swSrc.includes('firebase-messaging-compat.js')).toBe(true);
    expect(swSrc.includes('onBackgroundMessage')).toBe(true);
    expect(swSrc.includes('showNotification')).toBe(true);
    expect(swSrc.includes('notificationclick')).toBe(true);
    expect(swSrc.includes('gogocompany.in')).toBe(true);
    expect(swSrc.includes('tag:')).toBe(true);
    expect(swSrc.includes("addEventListener('fetch'")).toBe(false);
  });

  test('index.html mounts the notifications container and loads the module after script.js', () => {
    expect(indexHtml.includes('data-gogo-notifications')).toBe(true);
    expect(indexHtml.includes('gogo-notifications.js')).toBe(true);
    expect(indexHtml.indexOf('script.js') < indexHtml.indexOf('gogo-notifications.js')).toBe(true);
  });
});
