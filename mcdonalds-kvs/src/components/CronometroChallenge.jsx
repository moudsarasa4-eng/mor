import { useState, useEffect, useRef } from "react";
import { PAN_CATEGORIAS, PANES, getPan } from "../lib/panes";

// Drill aislado de un solo ítem: lo mostrás un instante, se tapa, y elegís
// el pan de memoria. Mide el tiempo real desde que aparece hasta que
// elegís, contra tu propio objetivo de 5s — no es un tiempo sacado de la
// guía oficial, es la meta que pediste para practicar memorizar + ubicar
// el pan rápido. Un pedido completo de varios ítems no entra en 5s de
// forma realista, así que el drill queda a propósito en un ítem por ronda
// (misma lógica de práctica aislada que Modo Estación/estilo "curso de
// edición": una repetición corta y muy repetible en vez de una simulación larga).
const PEEK_MS = 2000;
const TARGET_MS = 5000;
const STATS_KEY = "mcdonalds-kvs:cronometro";

const ITEMS_CON_PAN = Object.keys(PANES);

function shuffle(arr) {
	const a = [...arr];
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

function loadStats() {
	try {
		const raw = localStorage.getItem(STATS_KEY);
		return raw ? JSON.parse(raw) : { attempts: 0, hits: 0, bestMs: null, totalMs: 0 };
	} catch {
		return { attempts: 0, hits: 0, bestMs: null, totalMs: 0 };
	}
}

function randomItem() {
	const name = ITEMS_CON_PAN[Math.floor(Math.random() * ITEMS_CON_PAN.length)];
	const amount = 1 + Math.floor(Math.random() * 3);
	return { name, amount, ...getPan(name) };
}

function CronometroChallenge({ open, onClose }) {
	const [item, setItem] = useState(null);
	const [phase, setPhase] = useState("viendo"); // viendo | preguntando
	const [opciones, setOpciones] = useState([]);
	const [elapsedMs, setElapsedMs] = useState(null);
	const [resultado, setResultado] = useState(null);
	const [stats, setStats] = useState(loadStats);
	const startRef = useRef(0);
	const peekTimeoutRef = useRef(null);

	const nuevaRonda = () => {
		clearTimeout(peekTimeoutRef.current);
		const next = randomItem();
		setItem(next);
		setOpciones(shuffle(PAN_CATEGORIAS));
		setPhase("viendo");
		setElapsedMs(null);
		setResultado(null);
		startRef.current = Date.now();
		peekTimeoutRef.current = setTimeout(() => setPhase("preguntando"), PEEK_MS);
	};

	// El modal nunca se desmonta (open pasa a false y listo), así que hay
	// que resetear a mano cada vez que se vuelve a abrir.
	useEffect(() => {
		if (open) nuevaRonda();
		return () => clearTimeout(peekTimeoutRef.current);
		// eslint-disable-next-line
	}, [open]);

	if (!open) return null;

	const elegirPan = (pan) => {
		if (resultado) return;
		clearTimeout(peekTimeoutRef.current);
		const ms = Date.now() - startRef.current;
		const acerto = pan === item.pan;
		const exito = acerto && ms <= TARGET_MS;
		setElapsedMs(ms);
		setResultado({ acerto, exito });
		setStats((prev) => {
			const next = {
				attempts: prev.attempts + 1,
				hits: prev.hits + (exito ? 1 : 0),
				bestMs: exito ? Math.min(prev.bestMs ?? ms, ms) : prev.bestMs,
				totalMs: prev.totalMs + ms,
			};
			try {
				localStorage.setItem(STATS_KEY, JSON.stringify(next));
			} catch {
				// almacenamiento no disponible — se sigue igual
			}
			return next;
		});
	};

	const avgMs = stats.attempts > 0 ? Math.round(stats.totalMs / stats.attempts) : null;

	return (
		<div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[26rem] text-black">
				<div className="flex flex-row justify-between items-center mb-1">
					<h2 className="text-xl font-bold">Cronómetro: memorizar + pan</h2>
					<button onClick={onClose} className="text-gray-400 underline text-sm">
						cerrar (C)
					</button>
				</div>
				<p className="text-sm text-gray-600 mb-4">Tu objetivo: memorizar y elegir el pan en 5s o menos.</p>

				{phase === "viendo" && item && (
					<div className="text-center py-10">
						<p className="text-2xl font-semibold">
							{item.amount} {item.name}
						</p>
					</div>
				)}

				{phase === "preguntando" && (
					<div className="flex flex-col gap-1 mb-2">
						<h3 className="font-bold text-sm mb-1">¿Qué pan era?</h3>
						{opciones.map((pan) => {
							const showCorrect = resultado && pan === item.pan;
							const showWrong = resultado && !resultado.acerto && pan !== item.pan;
							return (
								<button
									key={pan}
									disabled={Boolean(resultado)}
									onClick={() => elegirPan(pan)}
									className={`text-left px-3 py-2 rounded border-2 ${
										showCorrect ? "bg-green-100 border-green-500" : "border-gray-200"
									} ${showWrong ? "opacity-40" : ""}`}
								>
									{pan} {showCorrect && "✔"}
								</button>
							);
						})}
					</div>
				)}

				{resultado && (
					<div className="mt-2">
						<p className={`font-bold text-lg mb-1 ${resultado.exito ? "text-green-700" : "text-red-600"}`}>
							{(elapsedMs / 1000).toFixed(1)}s —{" "}
							{resultado.acerto ? (resultado.exito ? "¡Justo a tiempo!" : "Bien, pero lento") : "Pan incorrecto"}
						</p>
						<button onClick={nuevaRonda} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded mb-3">
							Siguiente
						</button>
					</div>
				)}

				<hr className="my-3" />
				<p className="text-xs text-gray-500">
					Intentos: {stats.attempts} · Logrados en ≤5s: {stats.hits}
					{avgMs !== null && <> · Promedio: {(avgMs / 1000).toFixed(1)}s</>}
					{stats.bestMs !== null && <> · Mejor: {(stats.bestMs / 1000).toFixed(1)}s</>}
				</p>
			</div>
		</div>
	);
}
export default CronometroChallenge;
