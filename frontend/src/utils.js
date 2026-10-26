export const roleLabels = { ADMIN: 'Administrateur', SUPERVISOR: 'Superviseur interne', TECHNICIAN: 'Technicien', PROJECT_MANAGER: 'Chef de projet client' };
export const statusLabels = { ACTIVE: 'En cours', COMPLETED: 'Terminé', DRAFT: 'Brouillon', SUBMITTED: 'À valider', APPROVED: 'Validé', REJECTED: 'Refusé', INVOICED: 'Facturé', UNPAID: 'Non réglée', PARTIAL: 'Paiement partiel', PAID: 'Réglée' };
export const money = (value, currency = 'DZD') => new Intl.NumberFormat('fr-FR', { style: 'currency', currency, currencyDisplay: 'code' }).format(Number(value || 0));
export const number = value => new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(Number(value || 0));
export const date = value => value ? new Date(value.length === 10 ? value + 'T12:00:00' : value).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';
export const time = value => new Date(value).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
export function generatePassword() {
  const groups = ['ABCDEFGHJKLMNPQRSTUVWXYZ', 'abcdefghijkmnopqrstuvwxyz', '23456789', '!@#$%&*+-=?'];
  const alphabet = groups.join('');
  function randomIndex(length) {
    const sample = new Uint32Array(1);
    const limit = 2 ** 32 - (2 ** 32 % length);
    do { globalThis.crypto.getRandomValues(sample); } while (sample[0] >= limit);
    return sample[0] % length;
  }
  const characters = groups.map(group => group[randomIndex(group.length)]);
  while (characters.length < 20) characters.push(alphabet[randomIndex(alphabet.length)]);
  for (let index = characters.length - 1; index > 0; index--) {
    const other = randomIndex(index + 1);
    [characters[index], characters[other]] = [characters[other], characters[index]];
  }
  return characters.join('');
}
export function localDate(value = new Date()) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
}
export function maxBirthDate(today = new Date()) {
  const year = today.getFullYear() - 18;
  const month = today.getMonth();
  const day = Math.min(today.getDate(), new Date(year, month + 1, 0).getDate());
  return localDate(new Date(year, month, day));
}
export function age(birthDate, today = new Date()) {
  if (typeof birthDate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(birthDate)) return null;
  const birth = new Date(`${birthDate}T12:00:00`);
  if (!Number.isFinite(birth.getTime()) || localDate(birth) !== birthDate || birthDate > localDate(today)) return null;
  const birthdayPending = today.getMonth() < birth.getMonth()
    || (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate());
  return today.getFullYear() - birth.getFullYear() - Number(birthdayPending);
}
export function localInput(value) {
  const d = new Date(value);
  return `${localDate(d)}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}
export function duration(start, end, pause = 0) {
  const result = (new Date(end) - new Date(start)) / 3600000 - Number(pause) / 60;
  return Number.isFinite(result) ? Math.max(0, result) : 0;
}
