import PARES_CONFUNDIBLES from "./confusables";

// Modo Reconocimiento Visual: entrena memoria visual ESPECÍFICA del ticket
// real del KVS, no memoria visual genérica (dot-grids, n-back). La
// evidencia dice que la pericia visual es específica del dominio en el
// que se entrena — Chase & Simon (1973) con ajedrecistas, y la literatura
// de pericia perceptual en radiología muestran que un experto no es mejor
// memorizando cualquier imagen, sino la de SU dominio. Por eso este modo
// usa el mismo componente visual (OrderCard) que ves en la pantalla real,
// en vez de un juego abstracto.
//
// Dos mecánicas, las dos con paradigmas bien establecidos en la
// literatura de memoria:
// - "reconocimiento": memoria de reconocimiento clásica (¿esto estaba o
//   no estaba?), con distractores confundibles (Método 5 de
//   METODO-MEMORIA.md) en vez de opciones obviamente distintas.
// - "cambio": detección de cambios (paradigma de Luck & Vogel), con
//   ensayos "sin cambio" para que no se pueda adivinar que siempre hay algo.
//
// Tope de 3-4 ítems visibles a la vez: es el límite de capacidad de
// memoria de trabajo visual bien replicado en la literatura (Luck &
// Vogel), no un número arbitrario.
export const VISUAL_START_LEN = 2;
export const VISUAL_MAX_LEN = 4;
export const VISUAL_LEVELS_PER_EXTRA_ITEM = 3;

export const FLASH_START_MS = 2200;
export const FLASH_FLOOR_MS = 900;
export const FLASH_STEP_MS = 80;
export const BLANK_MS = 300;

export function visualLenForLevel(level) {
	return Math.min(
		VISUAL_START_LEN + Math.floor((level - 1) / VISUAL_LEVELS_PER_EXTRA_ITEM),
		VISUAL_MAX_LEN
	);
}

export function flashMs(level) {
	return Math.max(FLASH_FLOOR_MS, FLASH_START_MS - level * FLASH_STEP_MS);
}

const CONFUSION_KEY = "mcdonalds-kvs:visual-confusion";
const STATS_KEY = "mcdonalds-kvs:visual-stats";

export function loadVisualConfusion() {
	try {
		const raw = localStorage.getItem(CONFUSION_KEY);
		return raw ? JSON.parse(raw) : {};
	} catch {
		return {};
	}
}

export function saveVisualConfusion(confusion) {
	try {
		localStorage.setItem(CONFUSION_KEY, JSON.stringify(confusion));
	} catch {
		// almacenamiento no disponible — se sigue igual
	}
}

export function bumpVisual(confusion, names, wasWrong) {
	const next = { ...confusion };
	for (const name of names) {
		const prev = next[name] || { exposures: 0, misses: 0 };
		next[name] = { exposures: prev.exposures + 1, misses: prev.misses + (wasWrong ? 1 : 0) };
	}
	return next;
}

function troubleScore(stat) {
	return stat.exposures > 0 ? stat.misses / stat.exposures : 0;
}

// Método 5 (interferencia/discriminación) aplicado a este modo: pesa la
// elección de ítems hacia los que más fallás, con su propia tabla — la
// pericia visual se entrena y se mide acá mismo, no hace falta mezclarla
// con lo que te cuesta de memoria pura en Modo Enfoque.
export function weightedItemPool(confusion, fullPool) {
	const difficult = Object.entries(confusion)
		.filter(([, s]) => s.exposures > 0 && troubleScore(s) > 0)
		.sort((a, b) => troubleScore(b[1]) - troubleScore(a[1]))
		.slice(0, 8)
		.map(([name]) => name)
		.filter((name) => fullPool.includes(name));
	if (difficult.length === 0) return fullPool;
	return [...difficult, ...difficult, ...fullPool];
}

export function loadVisualStats() {
	try {
		const raw = localStorage.getItem(STATS_KEY);
		return raw ? JSON.parse(raw) : { attempts: 0, hits: 0 };
	} catch {
		return { attempts: 0, hits: 0 };
	}
}

export function saveVisualStats(stats) {
	try {
		localStorage.setItem(STATS_KEY, JSON.stringify(stats));
	} catch {
		// almacenamiento no disponible — se sigue igual
	}
}

function generateNumber() {
	return Math.floor(Math.random() * (16 - 5) + 5);
}

// Ticket sintético para este modo: mismo formato que generateOrder, pero
// con su propia progresión (tope 4, no 5) y sin modificadores SIN/SOLO —
// la variable que se está entrenando es "qué productos y cuántos", no
// el detalle del condimento.
export function buildVisualTicket(level, pool) {
	const len = visualLenForLevel(level);
	const chosen = [];
	const used = new Set();
	while (chosen.length < len && used.size < pool.length) {
		const name = pool[Math.floor(Math.random() * pool.length)];
		if (used.has(name)) continue;
		used.add(name);
		chosen.push({ name, amount: 1 + Math.floor(Math.random() * 2), modifier: null });
	}
	return {
		id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
		timeGenerated: Math.floor(Date.now() / 1000),
		randomCode: `R${generateNumber()}-${generateNumber()}`,
		randomTime: Math.floor(Math.random() * (360 - 60) + 60),
		orderArray: chosen,
		orderType: ["DT", "Bag", "Tray", "Delivery"][Math.floor(Math.random() * 4)],
		orderStorage: ["Paid", "Stored"][Math.floor(Math.random() * 2)],
	};
}

// Arma el probe de reconocimiento: 50/50 entre un ítem que sí estaba en
// el ticket y un distractor confundible que no estaba (Método 5).
export function buildRecognitionProbe(ticket, pool) {
	const presentes = ticket.orderArray.map((it) => it.name);
	const isPresent = Math.random() < 0.5;
	if (isPresent) {
		const name = presentes[Math.floor(Math.random() * presentes.length)];
		return { name, isPresent: true };
	}
	const confundibles = PARES_CONFUNDIBLES.filter((n) => !presentes.includes(n));
	const candidatos = confundibles.length > 0 ? confundibles : pool.filter((n) => !presentes.includes(n));
	const name = candidatos[Math.floor(Math.random() * candidatos.length)];
	return { name, isPresent: false };
}

// Detección de cambios (Luck & Vogel): 50% ensayo "sin cambio" (para que
// no se pueda adivinar que siempre pasa algo), 50% un cambio puntual —
// cantidad de un ítem, o directamente qué ítem es.
export function applyRandomChange(ticket, pool) {
	const clone = { ...ticket, orderArray: ticket.orderArray.map((it) => ({ ...it })) };
	if (Math.random() < 0.5) {
		return { ticket: clone, changed: false, description: null };
	}
	const idx = Math.floor(Math.random() * clone.orderArray.length);
	const original = clone.orderArray[idx];
	if (Math.random() < 0.5) {
		let newAmount = original.amount;
		while (newAmount === original.amount) newAmount = 1 + Math.floor(Math.random() * 3);
		clone.orderArray[idx] = { ...original, amount: newAmount };
		return { ticket: clone, changed: true, description: `${original.name}: ${original.amount} → ${newAmount}` };
	}
	const usados = new Set(clone.orderArray.map((it) => it.name));
	let newName = original.name;
	let intentos = 0;
	while ((newName === original.name || usados.has(newName)) && intentos < 20) {
		newName = pool[Math.floor(Math.random() * pool.length)];
		intentos++;
	}
	clone.orderArray[idx] = { ...original, name: newName };
	return { ticket: clone, changed: true, description: `${original.name} → ${newName}` };
}
