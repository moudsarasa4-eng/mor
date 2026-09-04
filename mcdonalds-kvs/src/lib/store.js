import { configureStore, createSlice } from "@reduxjs/toolkit";
import generateOrder from "./generateorder";

const CONFUSION_KEY = "mcdonalds-kvs:confusion";

function loadConfusion() {
	try {
		const raw = localStorage.getItem(CONFUSION_KEY);
		return raw ? JSON.parse(raw) : {};
	} catch {
		return {};
	}
}

function bump(confusion, names, field) {
	for (const name of names) {
		if (!confusion[name]) confusion[name] = { peeks: 0, served: 0, selfMiss: 0 };
		confusion[name][field] += 1;
	}
}

const slice = createSlice({
	name: "kvs",
	initialState: {
		sideOn: false,
		level: 1,
		orders: [
			generateOrder(1),
			generateOrder(1),
			generateOrder(1),
			generateOrder(1),
			generateOrder(1),
			generateOrder(1),
		],
		mfyTime: 120,
		// --- Entrenamiento de memoria (ver METODO-MEMORIA.md) ---
		memoriaOn: false,
		enfoqueOn: false,
		confusion: loadConfusion(),
	},
	reducers: {
		toggleSide(state, action) {
			state.sideOn = !state.sideOn;
		},
		pushOrder(state, action) {
			state.orders.push(generateOrder(state.level));
		},
		serveOrder(state, action) {
			if (state.orders.length === 0) return;
			state.orders.shift();
			state.level += 1;
		},
		setMfy(state, action) {
			state.mfyTime = action.payload;
		},
		toggleMemoria(state) {
			state.memoriaOn = !state.memoriaOn;
		},
		toggleEnfoque(state) {
			state.enfoqueOn = !state.enfoqueOn;
		},
		pushFocusOrder(state, action) {
			state.orders.push(generateOrder(state.level, action.payload));
		},
		registerPeek(state, action) {
			bump(state.confusion, action.payload, "peeks");
		},
		registerServed(state, action) {
			bump(state.confusion, action.payload, "served");
		},
		registerSelfMiss(state, action) {
			bump(state.confusion, action.payload, "selfMiss");
		},
		resetConfusion(state) {
			state.confusion = {};
		},
	},
});
export const actions = slice.actions;
const store = configureStore({
	reducer: slice.reducer,
});

store.subscribe(() => {
	try {
		localStorage.setItem(CONFUSION_KEY, JSON.stringify(store.getState().confusion));
	} catch {
		// almacenamiento no disponible (modo privado, cuota llena, etc.) — se sigue igual
	}
});

export default store;
