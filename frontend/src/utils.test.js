import test from 'node:test';
import assert from 'node:assert/strict';
import { age, duration, generatePassword, localDate, localInput, maxBirthDate, money } from './utils.js';

test('amounts default to Algerian dinars and display the DZD code', () => {
  assert.equal(money('1250.50').replace(/\s/g, ' '), '1 250,50 DZD');
  assert.equal(money(0, 'DZD').replace(/\s/g, ' '), '0,00 DZD');
});

test('generated passwords have 20 characters and include all four character groups', () => {
  const passwords = new Set();
  for (let index = 0; index < 32; index++) {
    const password = generatePassword();
    assert.equal(password.length, 20);
    assert.match(password, /[A-Z]/);
    assert.match(password, /[a-z]/);
    assert.match(password, /[0-9]/);
    assert.match(password, /[!@#$%&*+\-=?]/);
    assert.doesNotMatch(password, /\s/);
    passwords.add(password);
  }
  assert.equal(passwords.size, 32);
});

test('explicit invoice currencies remain respected', () => {
  assert.equal(money('25.00', 'EUR').replace(/\s/g, ' '), '25,00 EUR');
});

test('net working hours exclude breaks and handle overnight shifts', () => {
  assert.equal(duration('2026-10-01T08:00', '2026-10-01T17:00', 60), 8);
  assert.equal(duration('2026-10-01T22:00', '2026-10-02T06:00', 30), 7.5);
});
test('incomplete time entry does not display NaN or negative hours', () => {
  assert.equal(duration('', '', 0), 0);
  assert.equal(duration('2026-10-01T17:00', '2026-10-01T08:00'), 0);
});
test('input values preserve the browser local date and minute', () => {
  const value = new Date(2026, 9, 10, 0, 30);
  assert.equal(localDate(value), '2026-10-10');
  assert.equal(localInput(value.toISOString()), '2026-10-10T00:30');
});

test('age changes on the birthday using local calendar dates', () => {
  assert.equal(age('1996-10-17', new Date(2026, 9, 16)), 29);
  assert.equal(age('1996-10-17', new Date(2026, 9, 17)), 30);
  assert.equal(age('1996-10-17', new Date(2026, 9, 18)), 30);
  assert.equal(age('1996-12-01', new Date(2026, 0, 1)), 29);
  assert.equal(age('2026-10-07', new Date(2026, 9, 17)), 0);
});

test('age handles leap birthdays and ignores missing, invalid or future dates', () => {
  assert.equal(age('2000-02-29', new Date(2026, 1, 28)), 25);
  assert.equal(age('2000-02-29', new Date(2026, 2, 1)), 26);
  for (const value of [undefined, null, '', 'invalid', '2026-02-30', '2026-13-01', '2026-10-18']) {
    assert.equal(age(value, new Date(2026, 9, 17)), null);
  }
});

test('maximum birth date is 18 years ago and clamps leap days', () => {
  assert.equal(maxBirthDate(new Date(2026, 9, 17)), '2008-10-17');
  assert.equal(maxBirthDate(new Date(2024, 1, 29)), '2006-02-28');
});
