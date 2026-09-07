// Modo Panes: qué tipo de pan lleva cada producto, sin condimentos ni
// gramos — la versión liviana de Modo Estación, con cobertura de todo el
// menú. Ver ESTACION-INICIADOR.md para la fuente de lo verificado.
//
// verificado: true  -> confirmado contra la guía oficial o una foto de
//                       producto real (mcdonalds.com.ar / la propia guía).
// verificado: false -> asignado por lógica de línea de producto (nombre,
//                       familia), no por una fuente oficial puntual.
export const PAN_CATEGORIAS = [
	"Regular (sin semilla)",
	"Sésamo grande",
	'Big Mac (3 piezas, con "club")',
	"Grand (prensado, más grande)",
	"Pan de papa",
	"Kaiser (McCafé)",
];

export const PANES = {
	"Hamburguesa": { pan: "Regular (sin semilla)", verificado: true },
	"Hamburguesa c/Queso": { pan: "Regular (sin semilla)", verificado: true },
	"Hamburguesa CF": { pan: "Regular (sin semilla)", verificado: true },
	"Fiesta Jr": { pan: "Regular (sin semilla)", verificado: false },
	"Fiesta Jr CF": { pan: "Regular (sin semilla)", verificado: false },
	"McFiesta": { pan: "Regular (sin semilla)", verificado: false },
	"Dbl Carne Dble": { pan: "Regular (sin semilla)", verificado: false },
	"Trip Carne Trip Queso": { pan: "Regular (sin semilla)", verificado: false },

	"1/4 De Libra": { pan: "Sésamo grande", verificado: true },
	"1/4 De Libra c/Queso": { pan: "Sésamo grande", verificado: true },
	"Dbl 1/4 De Libra c/Queso": { pan: "Sésamo grande", verificado: true },
	"McNifica": { pan: "Sésamo grande", verificado: true },
	"McPollo": { pan: "Sésamo grande", verificado: false },

	"Big Mac": { pan: 'Big Mac (3 piezas, con "club")', verificado: true },

	"Grand Tasty Dbl": { pan: "Grand (prensado, más grande)", verificado: false },
	"Grand Tasty Trip": { pan: "Grand (prensado, más grande)", verificado: false },
	"Dbl McBacon": { pan: "Grand (prensado, más grande)", verificado: false },
	"Trip McBacon": { pan: "Grand (prensado, más grande)", verificado: false },
	"G Tasty Turbo Bacon Dbl": { pan: "Grand (prensado, más grande)", verificado: false },
	"G Tasty Turbo Bacon Trip": { pan: "Grand (prensado, más grande)", verificado: false },
	"Bacon Crispy": { pan: "Grand (prensado, más grande)", verificado: false },
	"Bacon Cheddar McMelt": { pan: "Grand (prensado, más grande)", verificado: false },
	"Grand Tostado": { pan: "Grand (prensado, más grande)", verificado: false },

	// Confirmado: McDonald's Argentina lanzó la línea McCrispy con pan de
	// papa como diferencial explícito de marketing (infonegocios.info, 2023).
	"McCrispy Classic": { pan: "Pan de papa", verificado: true },
	"McCrispy Deluxe": { pan: "Pan de papa", verificado: true },
	"McCrispy Ranch": { pan: "Pan de papa", verificado: true },

	"Tostado Lomo y Queso": { pan: "Kaiser (McCafé)", verificado: true },
	"Sandwich Lomo Queso y Huevo": { pan: "Kaiser (McCafé)", verificado: false },
	"Sandwich Bacon Queso y Huevo": { pan: "Kaiser (McCafé)", verificado: false },
	"Mc Queso": { pan: "Kaiser (McCafé)", verificado: false },
	// Sin pan a propósito (no mapeados): McNuggets x4/x6/x10/x20, Apple Pie,
	// Ensalada Caesar c/Pollo Grille/Crispy — Modo Panes los salta solo.
};

export function getPan(itemName) {
	return PANES[itemName] || null;
}

// Arma la cola de productos con pan a preguntar para un pedido, en el orden
// en que aparecen, sin repetir nombre y sin repreguntar uno que ya cubrió
// Modo Estación en el mismo servido.
export function buildPanesQueue(orderArray, excludeName) {
	const vistos = new Set();
	const cola = [];
	for (const item of orderArray) {
		if (item.name === excludeName || vistos.has(item.name)) continue;
		const info = getPan(item.name);
		if (info) {
			vistos.add(item.name);
			cola.push({ name: item.name, ...info });
		}
	}
	return cola;
}
