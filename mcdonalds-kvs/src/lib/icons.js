// Codificación dual (Método 4 de METODO-MEMORIA.md): asociar cada ítem
// a una imagen mental simple ayuda a fijarlo mejor que el texto solo.
const REGLAS = [
	[/ensalada/i, "🥗"],
	[/nugget/i, "🍗"],
	[/pollo|crispy/i, "🍗"],
	[/pie/i, "🥧"],
	[/tostado|lomo|huevo/i, "🥪"],
	[/bacon/i, "🥓"],
	[/queso/i, "🧀"],
];

export function iconFor(itemName) {
	const regla = REGLAS.find(([re]) => re.test(itemName));
	return regla ? regla[1] : "🍔";
}
