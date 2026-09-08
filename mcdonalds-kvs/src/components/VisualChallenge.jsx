import { useState, useEffect, useRef } from "react";
import OrderCard from "./OrderCard";
import { ITEM_LIST } from "../lib/generateorder";
import {
	flashMs,
	BLANK_MS,
	loadVisualConfusion,
	saveVisualConfusion,
	bumpVisual,
	weightedItemPool,
	loadVisualStats,
	saveVisualStats,
	buildVisualTicket,
	buildRecognitionProbe,
	applyRandomChange,
} from "../lib/visual";

// Modo Reconocimiento Visual (ver src/lib/visual.js para las fuentes y el
// razonamiento detrás de cada mecánica). Drill aislado como Cronómetro y
// Evaluación: no toca la cola de pedidos, tiene su propio nivel interno.
function VisualChallenge({ open, onClose }) {
	const [level, setLevel] = useState(1);
	const [phase, setPhase] = useState("flash"); // flash | blank | probe
	const [roundType, setRoundType] = useState("reconocimiento");
	const [ticket, setTicket] = useState(null);
	const [probe, setProbe] = useState(null);
	const [resultado, setResultado] = useState(null);
	const [stats, setStats] = useState(loadVisualStats);
	const [confusion, setConfusion] = useState(loadVisualConfusion);
	const timeoutRef = useRef(null);

	const nuevaRonda = (nivel) => {
		clearTimeout(timeoutRef.current);
		const pool = weightedItemPool(confusion, ITEM_LIST);
		const t = buildVisualTicket(nivel, pool);
		const tipo = Math.random() < 0.5 ? "reconocimiento" : "cambio";
		setTicket(t);
		setRoundType(tipo);
		setResultado(null);
		if (tipo === "reconocimiento") {
			setProbe(buildRecognitionProbe(t, pool));
		} else {
			setProbe(applyRandomChange(t, pool));
		}
		setPhase("flash");
		timeoutRef.current = setTimeout(() => {
			setPhase("blank");
			timeoutRef.current = setTimeout(() => setPhase("probe"), BLANK_MS);
		}, flashMs(nivel));
	};

	// El modal nunca se desmonta: arrancar de cero cada vez que se abre.
	useEffect(() => {
		if (open) {
			setLevel(1);
			nuevaRonda(1);
		}
		return () => clearTimeout(timeoutRef.current);
		// eslint-disable-next-line
	}, [open]);

	if (!open) return null;

	const responder = (respuesta) => {
		if (resultado || !ticket) return;
		const nombres = ticket.orderArray.map((it) => it.name);
		let correcto, detalle, itemsEnJuego;
		if (roundType === "reconocimiento") {
			correcto = respuesta === probe.isPresent;
			detalle = probe.isPresent ? `Sí estaba: ${probe.name}` : `No estaba: ${probe.name}`;
			itemsEnJuego = [probe.name];
		} else {
			correcto = respuesta === probe.changed;
			detalle = probe.changed ? `Cambió: ${probe.description}` : "No cambió nada";
			itemsEnJuego = nombres;
		}
		setResultado({ correcto, detalle });
		setStats((prev) => {
			const next = { attempts: prev.attempts + 1, hits: prev.hits + (correcto ? 1 : 0) };
			saveVisualStats(next);
			return next;
		});
		setConfusion((prev) => {
			const next = bumpVisual(prev, itemsEnJuego, !correcto);
			saveVisualConfusion(next);
			return next;
		});
	};

	const siguienteRonda = () => {
		const nextLevel = level + 1;
		setLevel(nextLevel);
		nuevaRonda(nextLevel);
	};

	const accuracy = stats.attempts > 0 ? Math.round((stats.hits / stats.attempts) * 100) : null;

	return (
		<div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[32rem] text-black max-h-[90vh] overflow-y-auto">
				<div className="flex flex-row justify-between items-center mb-1">
					<h2 className="text-xl font-bold">Reconocimiento Visual</h2>
					<button onClick={onClose} className="text-gray-400 underline text-sm">cerrar (R)</button>
				</div>
				<p className="text-sm text-gray-600 mb-3">
					{roundType === "reconocimiento" ? "Memorizá el ticket. Después te pregunto si un producto estaba o no." : "Memorizá el ticket. Después te muestro una versión y decís si cambió algo."}
				</p>

				{phase === "flash" && ticket && (
					<div className="flex flex-row justify-center py-2">
						<OrderCard order={ticket} isFront={true} masked={false} />
					</div>
				)}

				{phase === "blank" && <div className="py-24 text-center text-gray-400">memorizando…</div>}

				{phase === "probe" && roundType === "reconocimiento" && probe && (
					<div>
						<p className="text-lg font-semibold text-center py-6">¿Estaba "{probe.name}" en el ticket?</p>
						{!resultado ? (
							<div className="flex flex-row gap-2">
								<button onClick={() => responder(true)} className="flex-1 bg-blue-500 text-white font-bold px-3 py-2 rounded">Sí</button>
								<button onClick={() => responder(false)} className="flex-1 bg-blue-500 text-white font-bold px-3 py-2 rounded">No</button>
							</div>
						) : (
							<>
								<p className={`font-bold mb-2 ${resultado.correcto ? "text-green-700" : "text-red-600"}`}>
									{resultado.correcto ? "¡Bien!" : "Incorrecto"} — {resultado.detalle}
								</p>
								<button onClick={siguienteRonda} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">Siguiente</button>
							</>
						)}
					</div>
				)}

				{phase === "probe" && roundType === "cambio" && probe && (
					<div>
						<div className="flex flex-row justify-center py-2">
							<OrderCard order={probe.ticket} isFront={true} masked={false} />
						</div>
						<p className="text-lg font-semibold text-center py-3">¿Cambió algo respecto de lo que viste antes?</p>
						{!resultado ? (
							<div className="flex flex-row gap-2">
								<button onClick={() => responder(true)} className="flex-1 bg-blue-500 text-white font-bold px-3 py-2 rounded">Sí, cambió</button>
								<button onClick={() => responder(false)} className="flex-1 bg-blue-500 text-white font-bold px-3 py-2 rounded">No cambió</button>
							</div>
						) : (
							<>
								<p className={`font-bold mb-2 ${resultado.correcto ? "text-green-700" : "text-red-600"}`}>
									{resultado.correcto ? "¡Bien!" : "Incorrecto"} — {resultado.detalle}
								</p>
								<button onClick={siguienteRonda} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">Siguiente</button>
							</>
						)}
					</div>
				)}

				<hr className="my-3" />
				<p className="text-xs text-gray-500">
					Nivel {level} · Intentos: {stats.attempts}{accuracy !== null && <> · Precisión: {accuracy}%</>}
				</p>
			</div>
		</div>
	);
}
export default VisualChallenge;
