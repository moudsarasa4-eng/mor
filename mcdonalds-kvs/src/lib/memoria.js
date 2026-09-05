import PARES_CONFUNDIBLES from "./confusables";

// Cuánto tiempo (en segundos) se ve el pedido completo antes de taparse
// en Modo Memoria. Baja a medida que subís de nivel (Método 1: recuperación
// activa, con exigencia creciente en vez de fija).
export const RECALL_VISIBLE_BASE_S = 8;
export const RECALL_VISIBLE_FLOOR_S = 2.5;
export const RECALL_VISIBLE_STEP_S = 0.3;

export function recallVisibleS(level) {
	return Math.max(RECALL_VISIBLE_FLOOR_S, RECALL_VISIBLE_BASE_S - level * RECALL_VISIBLE_STEP_S);
}

// Cuánto dura el "chequeo" (espiar) al mantener la tecla de repaso.
export const PEEK_DURATION_MS = 1500;

// Oleadas de pedidos extra mientras hay algún modo de entrenamiento activo,
// simulando la hora pico ("salen muchos pedidos a la vez").
export const WAVE_MIN_MS = 45000;
export const WAVE_MAX_MS = 70000;
export const WAVE_BANNER_MS = 2500;

const FOCUS_POOL_MIN = 6;

function troubleScore(stat) {
	return (stat.peeks + stat.selfMiss) / (stat.served + 1);
}

function sortedTrouble(confusion) {
	return Object.entries(confusion)
		.filter(([, s]) => s.peeks + s.selfMiss > 0)
		.sort((a, b) => troubleScore(b[1]) - troubleScore(a[1]));
}

// Método 5 (interferencia y discriminación): arma un pool de práctica
// enfocado en lo que más le cuesta al jugador, completado con los pares
// clásicos que se confunden entre sí hasta tener suficientes datos propios.
export function computeFocusPool(confusion) {
	const propios = sortedTrouble(confusion).slice(0, 6).map(([name]) => name);
	const pool = Array.from(new Set([...propios, ...PARES_CONFUNDIBLES]));
	return pool.slice(0, Math.max(FOCUS_POOL_MIN, propios.length + 4));
}

export function topDifficultItems(confusion, n = 5) {
	return sortedTrouble(confusion)
		.slice(0, n)
		.map(([name, s]) => ({ name, ...s, score: troubleScore(s) }));
}
