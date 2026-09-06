const config = {
	maxOrderlength: 5, // tope de items distintos por pedido, aunque subas mucho de nivel
	minOrderlength: 1,
	singleItemMaxAmount: 4,
	singleItemMinAmount: 1,
	Itemlist: [
		"Dbl Carne Dble",
		"Big Mac",
		"1/4 De Libra",
		"1/4 De Libra c/Queso",
		"Dbl 1/4 De Libra c/Queso",
		"Hamburguesa",
		"Hamburguesa c/Queso",
		"McFiesta",
		"Fiesta Jr",
		"Trip Carne Trip Queso",
		"McNifica",
		"Grand Tasty Dbl",
		"Grand Tasty Trip",
		"Dbl McBacon",
		"Trip McBacon",
		"G Tasty Turbo Bacon Dbl",
		"G Tasty Turbo Bacon Trip",
		"Bacon Crispy",
		"Bacon Cheddar McMelt",
		"Grand Tostado",
		"Hamburguesa CF",
		"Fiesta Jr CF",
		"McNuggets x4",
		"McNuggets x6",
		"McNuggets x10",
		"McNuggets x20",
		"Apple Pie",
		"Tostado Lomo y Queso",
		"Mc Queso",
		// Sandwiches de pollo (confirmado en mcdonalds.com.ar/menu/sandwiches-de-pollo)
		"McPollo",
		"McCrispy Classic",
		"McCrispy Deluxe",
		"McCrispy Ranch",
		// Ensaladas (confirmado en mcdonalds.com.ar/menu/ensaladas)
		"Ensalada Caesar c/Pollo Grille",
		"Ensalada Caesar c/Pollo Crispy",
		// McCafé (confirmado en mcdonalds.com.ar/menu/mccafe)
		"Sandwich Lomo Queso y Huevo",
		"Sandwich Bacon Queso y Huevo",
	],
	OrderTypes: ["DT", "Bag", "Tray", "Delivery"],
	OrderStorage: ["Paid", "Stored"],
};

// Progresión realista: recién empezando, los pedidos vienen cortos (como te
// dan a vos al principio del entrenamiento real) y se alargan de a poco a
// medida que subís de nivel, hasta llegar al tope de config.maxOrderlength.
// "level" sube 1 por cada pedido SERVIDO (no por minuto), así que estos pasos
// están pensados en pedidos servidos, no en tiempo: con 3 tardaba apenas 10
// pedidos en llegar al tope, es decir un rato del Turno Intensivo. Con 8,
// llegar al pedido más largo lleva una sesión entera de práctica sostenida.
const START_ORDER_LENGTH = 2;
const LEVELS_PER_EXTRA_ITEM = 8;

// Misma lógica para la cantidad por ítem: arranca en 1 (un solo "Big Mac",
// no "3 Big Mac") y va sumando de a poco hasta el tope de
// config.singleItemMaxAmount, en vez de ser random desde el pedido número uno.
const START_QTY_CEILING = 2;
const LEVELS_PER_EXTRA_QTY = 6;

function qtyCeilingForLevel(level) {
	return Math.min(
		START_QTY_CEILING + Math.floor((level - 1) / LEVELS_PER_EXTRA_QTY),
		config.singleItemMaxAmount
	);
}

function generateNumber() {
	return Math.floor(Math.random() * (16 - 5) + 5);
}

const INGREDIENTES = ["Cebolla","Pepinillo","Ketchup","Mostaza","Queso","Lechuga","Tomate","Mayonesa","Bacon"];
const SIN_MODIFICADOR = new Set(["McNuggets x4", "McNuggets x6", "McNuggets x10", "McNuggets x20", "Apple Pie"]);

function maybeModifier(itemName) {
	if (SIN_MODIFICADOR.has(itemName)) return null;
	if (Math.random() > 0.35) return null;
	const isSin = Math.random() > 0.5;
	const ing = INGREDIENTES[Math.floor(Math.random() * INGREDIENTES.length)];
	return { prefix: isSin ? "SIN" : "SOLO", ing };
}

function generateOrder(level = 1, itemPool = config.Itemlist) {
	const duplicateChecker = [];
	const maxForLevel = Math.min(
		START_ORDER_LENGTH + Math.floor((level - 1) / LEVELS_PER_EXTRA_ITEM),
		config.maxOrderlength
	);
	const dynamicMax = Math.min(maxForLevel + 1, itemPool.length);
	const orderAmount = Math.floor(
		Math.random() * (dynamicMax - config.minOrderlength) +
			config.minOrderlength
	);
	const orderArray = [];
	for (let i = 0; i < orderAmount; i++) {
		let ItemRandomizer = Math.floor(Math.random() * itemPool.length);
		//Prevent duplicate items
		while (duplicateChecker.includes(ItemRandomizer)) {
			ItemRandomizer = Math.floor(Math.random() * itemPool.length);
		}
		duplicateChecker.push(ItemRandomizer);

		const singleItemAmount = Math.floor(
			Math.random() *
				(qtyCeilingForLevel(level) - config.singleItemMinAmount) +
				config.singleItemMinAmount
		);
		orderArray.push({
			name: itemPool[ItemRandomizer],
			amount: singleItemAmount,
			modifier: maybeModifier(itemPool[ItemRandomizer]),
		});
	}
	const randomCode = `R${generateNumber()}-${generateNumber()}`;
	const randomTime = Math.floor(Math.random() * (360 - 60) + 60);
	return {
		id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
		timeGenerated: Math.floor(Date.now() / 1000),
		randomCode,
		randomTime,
		orderArray,
		orderType:
			config.OrderTypes[Math.floor(Math.random() * config.OrderTypes.length)],
		orderStorage:
			config.OrderStorage[
				Math.floor(Math.random() * config.OrderStorage.length)
			],
	};
}
export default generateOrder;
