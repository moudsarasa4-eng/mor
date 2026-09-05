const config = {
	maxOrderlength: 5,
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
	const dynamicMax = Math.min(config.maxOrderlength + Math.floor(level / 2), itemPool.length);
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
				(config.singleItemMaxAmount - config.singleItemMinAmount) +
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
