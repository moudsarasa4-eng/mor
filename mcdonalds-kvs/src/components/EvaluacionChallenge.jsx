import { useState, useEffect, useRef } from "react";
import { PAN_CATEGORIAS, PANES, getPan } from "../lib/panes";
import CELIACOS_PREGUNTAS from "../lib/celiacos";

// Modo Evaluación: examen formal y acotado (no un drill infinito como
// Cronómetro) — se toma, se termina, y da una nota, como una evaluación
// real de puesto (PCP). Mezcla el parámetro de Iniciador "memorizar +
// poner el pan en 5s o menos" con preguntas verificadas del procedimiento
// de atención a clientes celíacos (GE Opciones para Celíacos, Oct 2021).
const EXAM_ITEM_ROUNDS = 7;
const EXAM_CELIAC_ROUNDS = 3;
const PEEK_MS = 2000;
const TARGET_MS = 5000;
const HISTORY_KEY = "mcdonalds-kvs:evaluaciones";
const MAX_HISTORY = 20;

const ITEMS_CON_PAN = Object.keys(PANES);

function shuffle(arr) {
	const a = [...arr];
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

function loadHistory() {
	try {
		const raw = localStorage.getItem(HISTORY_KEY);
		return raw ? JSON.parse(raw) : [];
	} catch {
		return [];
	}
}

function buildRounds() {
	const items = shuffle(ITEMS_CON_PAN)
		.slice(0, EXAM_ITEM_ROUNDS)
		.map((name) => ({ type: "item", name, amount: 1 + Math.floor(Math.random() * 3), ...getPan(name) }));
	const celiac = shuffle(CELIACOS_PREGUNTAS)
		.slice(0, EXAM_CELIAC_ROUNDS)
		.map((q) => ({ type: "celiac", ...q, opciones: shuffle(q.opciones) }));
	return shuffle([...items, ...celiac]);
}

function EvaluacionChallenge({ open, onClose }) {
	const [rounds, setRounds] = useState([]);
	const [roundIdx, setRoundIdx] = useState(0);
	const [phase, setPhase] = useState("viendo"); // viendo | preguntando (solo aplica a rondas 'item')
	const [picked, setPicked] = useState(null);
	const [elapsedMs, setElapsedMs] = useState(null);
	const [results, setResults] = useState([]);
	const [finished, setFinished] = useState(false);
	const [history, setHistory] = useState(loadHistory);
	const startRef = useRef(0);
	const peekTimeoutRef = useRef(null);

	const empezar = () => {
		clearTimeout(peekTimeoutRef.current);
		const nuevasRondas = buildRounds();
		setRounds(nuevasRondas);
		setRoundIdx(0);
		setResults([]);
		setFinished(false);
		setPicked(null);
		setElapsedMs(null);
		const primera = nuevasRondas[0];
		if (primera.type === "item") {
			setPhase("viendo");
			startRef.current = Date.now();
			peekTimeoutRef.current = setTimeout(() => setPhase("preguntando"), PEEK_MS);
		} else {
			setPhase("preguntando");
		}
	};

	// El modal nunca se desmonta: arrancar de cero cada vez que se abre.
	useEffect(() => {
		if (open) empezar();
		return () => clearTimeout(peekTimeoutRef.current);
		// eslint-disable-next-line
	}, [open]);

	if (!open) return null;

	const rondaActual = rounds[roundIdx];

	const responder = (opcion) => {
		if (picked !== null) return;
		clearTimeout(peekTimeoutRef.current);
		let correcto, ms = null;
		if (rondaActual.type === "item") {
			ms = Date.now() - startRef.current;
			correcto = opcion === rondaActual.pan && ms <= TARGET_MS;
			setElapsedMs(ms);
		} else {
			correcto = opcion === rondaActual.correcta;
		}
		setPicked(opcion);
		setResults((prev) => [...prev, { type: rondaActual.type, correcto, ms }]);
	};

	const siguienteRonda = () => {
		const next = roundIdx + 1;
		setPicked(null);
		setElapsedMs(null);
		if (next >= rounds.length) {
			const itemResultados = results.filter((r) => r.type === "item");
			const celiacResultados = results.filter((r) => r.type === "celiac");
			const itemScore = itemResultados.filter((r) => r.correcto).length;
			const celiacScore = celiacResultados.filter((r) => r.correcto).length;
			const total = itemResultados.length + celiacResultados.length;
			const score = itemScore + celiacScore;
			const entry = {
				ts: Date.now(),
				score,
				total,
				itemScore,
				itemTotal: itemResultados.length,
				celiacScore,
				celiacTotal: celiacResultados.length,
				passed: score >= Math.ceil(total * 0.7),
			};
			setHistory((prev) => {
				const nextHistory = [entry, ...prev].slice(0, MAX_HISTORY);
				try {
					localStorage.setItem(HISTORY_KEY, JSON.stringify(nextHistory));
				} catch {
					// almacenamiento no disponible — se sigue igual
				}
				return nextHistory;
			});
			setFinished(true);
			return;
		}
		setRoundIdx(next);
		const siguiente = rounds[next];
		if (siguiente.type === "item") {
			setPhase("viendo");
			startRef.current = Date.now();
			peekTimeoutRef.current = setTimeout(() => setPhase("preguntando"), PEEK_MS);
		} else {
			setPhase("preguntando");
		}
	};

	if (finished) {
		const last = history[0];
		return (
			<div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
				<div className="bg-white rounded-lg p-6 w-[28rem] text-black">
					<h2 className="text-xl font-bold mb-3">Resultado de la evaluación</h2>
					<p className={`font-bold text-lg mb-3 ${last.passed ? "text-green-700" : "text-red-600"}`}>
						{last.passed ? "APROBADO" : "A REPASAR"} — {last.score}/{last.total}
					</p>
					<p className="mb-1">Memoria + Pan (≤5s): <b>{last.itemScore}/{last.itemTotal}</b></p>
					<p className="mb-3">Procedimiento Celíacos: <b>{last.celiacScore}/{last.celiacTotal}</b></p>
					<p className="text-xs text-gray-500 mb-4">Criterio de esta práctica (70% o más), no es un número de la guía oficial.</p>
					{history.length > 1 && (
						<>
							<hr className="my-2" />
							<p className="text-xs text-gray-500 mb-1">Evaluaciones anteriores:</p>
							<ul className="text-xs text-gray-600 mb-3">
								{history.slice(1, 5).map((h) => (
									<li key={h.ts}>
										{new Date(h.ts).toLocaleDateString()} — {h.score}/{h.total} {h.passed ? "✔" : "✘"}
									</li>
								))}
							</ul>
						</>
					)}
					<div className="flex flex-row gap-2">
						<button onClick={empezar} className="flex-1 bg-neutral-900 text-white font-bold px-3 py-2 rounded">Repetir</button>
						<button onClick={onClose} className="flex-1 bg-gray-200 text-black font-bold px-3 py-2 rounded">Cerrar</button>
					</div>
				</div>
			</div>
		);
	}

	if (!rondaActual) return null;

	return (
		<div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[28rem] text-black max-h-[90vh] overflow-y-auto">
				<div className="flex flex-row justify-between items-center mb-1">
					<h2 className="text-lg font-bold">Evaluación — pregunta {roundIdx + 1} de {rounds.length}</h2>
					<button onClick={onClose} className="text-gray-400 underline text-sm">cerrar (V)</button>
				</div>

				{rondaActual.type === "item" && (
					<>
						<p className="text-sm text-gray-600 mb-3">Memorizar + pan en 5s o menos.</p>
						{phase === "viendo" && (
							<div className="text-center py-10">
								<p className="text-2xl font-semibold">{rondaActual.amount} {rondaActual.name}</p>
							</div>
						)}
						{phase === "preguntando" && (
							<div className="flex flex-col gap-1 mb-2">
								<h3 className="font-bold text-sm mb-1">¿Qué pan era?</h3>
								{PAN_CATEGORIAS.map((pan) => {
									const showCorrect = picked && pan === rondaActual.pan;
									const showWrong = picked && picked === pan && pan !== rondaActual.pan;
									return (
										<button key={pan} disabled={Boolean(picked)} onClick={() => responder(pan)}
											className={`text-left px-3 py-2 rounded border-2 ${picked === pan ? "border-blue-500" : "border-gray-200"} ${showCorrect ? "bg-green-100 border-green-500" : ""} ${showWrong ? "bg-red-100 border-red-500" : ""}`}>
											{pan} {showCorrect && "✔"}
										</button>
									);
								})}
							</div>
						)}
						{picked && (
							<div className="mt-2">
								<p className={`font-bold mb-2 ${picked === rondaActual.pan && elapsedMs <= TARGET_MS ? "text-green-700" : "text-red-600"}`}>
									{(elapsedMs / 1000).toFixed(1)}s — {picked !== rondaActual.pan ? `Era: ${rondaActual.pan}` : elapsedMs <= TARGET_MS ? "¡Justo a tiempo!" : "Bien, pero lento"}
								</p>
								<button onClick={siguienteRonda} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">
									{roundIdx + 1 >= rounds.length ? "Ver resultado" : "Siguiente"}
								</button>
							</div>
						)}
					</>
				)}

				{rondaActual.type === "celiac" && (
					<>
						<p className="text-xs text-orange-700 font-bold mb-2">Procedimiento Celíacos (SIN TACC)</p>
						<p className="font-semibold mb-3">{rondaActual.pregunta}</p>
						<div className="flex flex-col gap-1 mb-2">
							{rondaActual.opciones.map((op) => {
								const showCorrect = picked && op === rondaActual.correcta;
								const showWrong = picked && picked === op && op !== rondaActual.correcta;
								return (
									<button key={op} disabled={Boolean(picked)} onClick={() => responder(op)}
										className={`text-left px-3 py-2 rounded border-2 text-sm ${picked === op ? "border-blue-500" : "border-gray-200"} ${showCorrect ? "bg-green-100 border-green-500" : ""} ${showWrong ? "bg-red-100 border-red-500" : ""}`}>
										{op} {showCorrect && "✔"}
									</button>
								);
							})}
						</div>
						{picked && (
							<div className="mt-2">
								<p className="text-xs text-gray-500 italic mb-3">{rondaActual.fuente}</p>
								<button onClick={siguienteRonda} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">
									{roundIdx + 1 >= rounds.length ? "Ver resultado" : "Siguiente"}
								</button>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);
}
export default EvaluacionChallenge;
