// Recetas reales de armado, extraídas de la Guía de Entrenamiento oficial
// "Iniciador/Ensamblador — Área de Producción" (Agosto 2022). Ver
// ESTACION-INICIADOR.md para el detalle completo y las fuentes.
//
// Solo se incluyen acá los ítems para los que la guía da la receta EXACTA
// (pan + condimentos + cantidades). El resto del menú (McCrispy, ensaladas
// Caesar, tostados, McCafé, etc.) no tiene un capítulo equivalente en esta
// guía — antes que inventar cantidades, Modo Estación simplemente no arma
// desafío para esos ítems y los sirve directo. Se puede sumar cobertura el
// día que aparezca una guía más nueva para esas líneas.
const RECETAS = {
	"Hamburguesa": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mostaza (1/35-1/60 oz) en el centro de la corona",
			"Ketchup (1/3 oz) en el centro de la corona",
			"3,5 g de cebolla rehidratada sobre el ketchup",
		],
	},
	"Hamburguesa c/Queso": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mostaza (1/35-1/60 oz) en el centro de la corona",
			"Ketchup (1/3 oz) en el centro de la corona",
			"3,5 g de cebolla rehidratada sobre el ketchup",
			"1 feta de queso cheddar sobre la corona condimentada",
		],
	},
	"Big Mac": {
		pan: "Pan con club (3 piezas: base, club y corona)",
		pasos: [
			"Salsa Big Mac (1/3 oz) en el centro de la base Y del club",
			"3,5 g de cebolla rehidratada sobre la salsa del club y la base",
			"14 g de lechuga sobre el club y la base",
			"2 rodajas de pepino sobre la lechuga del club",
			"1 feta de queso cheddar sobre la lechuga de la base",
		],
	},
	"1/4 De Libra c/Queso": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mostaza (1/35-1/60 oz) y ketchup (1/2 oz) simultáneos, un dispensador en cada mano",
			"7 g de cebolla fresca sobre el ketchup",
			"1 feta de queso cheddar sobre la corona condimentada",
			"1 feta de queso cheddar más sobre la base, en estrella con la primera",
		],
	},
	"Dbl 1/4 De Libra c/Queso": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mostaza (1/35-1/60 oz) y ketchup (1/2 oz) simultáneos, un dispensador en cada mano",
			"7 g de cebolla fresca sobre el ketchup",
			"1 feta de queso cheddar sobre la corona condimentada",
			"1 feta de queso cheddar más entre las dos carnes (no va en el pan)",
		],
	},
	"McNifica": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mostaza (1/35-1/60 oz) y ketchup (1/2 oz) en el centro de la corona",
			"7 g de cebolla fresca sobre el ketchup",
			"Mayonesa (1/2 oz)",
			"21 g de lechuga sobre la salsa",
			"2 rodajas de tomate superpuestas sobre la lechuga",
			"1 feta de queso sobre los tomates",
		],
	},
	"McPollo": {
		pan: "Pan regular (corona + base)",
		pasos: [
			"Mayonesa 2/3 oz (2 dispensadas de 1/3 oz) en el centro de la corona",
			"28 g de lechuga cubriendo toda la superficie del pan",
		],
	},
};

function shuffle(arr) {
	const a = [...arr];
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

export function tieneReceta(itemName) {
	return Boolean(RECETAS[itemName]);
}

// Arma un desafío de opción múltiple: mezcla los pasos reales de este ítem
// con "distractores" — pasos reales de OTROS ítems — para practicar
// discriminación (Método 5 de METODO-MEMORIA.md), no solo memoria pura.
export function buildChallenge(itemName) {
	const receta = RECETAS[itemName];
	if (!receta) return null;

	const otrosPanes = Array.from(new Set(Object.values(RECETAS).map((r) => r.pan))).filter((p) => p !== receta.pan);
	const panOpciones = shuffle([receta.pan, ...shuffle(otrosPanes).slice(0, 1)]);

	// Algunas recetas comparten pasos textuales entre sí (ej. Hamburguesa y
	// Hamburguesa c/Queso arrancan igual) — esos NO son distractores válidos,
	// filtrarlos evita mostrar el mismo paso dos veces como si uno fuera falso.
	const propios = new Set(receta.pasos);
	const otrosPasos = Object.entries(RECETAS)
		.filter(([nombre]) => nombre !== itemName)
		.flatMap(([, r]) => r.pasos)
		.filter((paso) => !propios.has(paso));
	const distractores = shuffle(Array.from(new Set(otrosPasos))).slice(0, Math.max(2, 6 - receta.pasos.length));
	const pasoOpciones = shuffle([...receta.pasos, ...distractores]);

	return {
		itemName,
		pan: receta.pan,
		panOpciones,
		pasosCorrectos: propios,
		pasoOpciones,
	};
}
