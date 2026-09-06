import { useState, useEffect } from "react";
import { PAN_CATEGORIAS } from "../lib/panes";

function shuffle(arr) {
	const a = [...arr];
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

// Modo Panes: uno por uno, "¿qué pan va acá?" — sin condimentos ni gramos,
// solo el tipo de pan, con cobertura de todo el menú. Ver panes.js.
function PanesChallenge({ item, restantes, onAnswer }) {
	const [pickedPan, setPickedPan] = useState(null);
	const [opciones, setOpciones] = useState([]);

	useEffect(() => {
		setPickedPan(null);
		setOpciones(shuffle(PAN_CATEGORIAS));
	}, [item]);

	if (!item) return null;

	const elegir = (pan) => {
		if (pickedPan) return;
		setPickedPan(pan);
	};

	const continuar = () => {
		onAnswer(pickedPan === item.pan);
	};

	return (
		<div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[26rem] text-black">
				<h2 className="text-xl font-bold mb-1">¿Qué pan va acá?</h2>
				<p className="text-lg font-semibold mb-1">{item.name}</p>
				{!item.verificado && (
					<p className="text-xs text-yellow-700 mb-3">
						Asignado por lógica de línea de producto, no confirmado en la guía oficial.
					</p>
				)}
				{item.verificado && <p className="text-xs text-gray-500 mb-3">Confirmado (guía oficial o producto real).</p>}

				<div className="flex flex-col gap-1 mb-4">
					{opciones.map((pan) => {
						const isCorrect = pickedPan && pan === item.pan;
						const isWrongPick = pickedPan && pan === pickedPan && pan !== item.pan;
						return (
							<button
								key={pan}
								disabled={Boolean(pickedPan)}
								onClick={() => elegir(pan)}
								className={`text-left px-3 py-2 rounded border-2 ${
									pickedPan === pan ? "border-blue-500" : "border-gray-200"
								} ${isCorrect ? "bg-green-100 border-green-500" : ""} ${isWrongPick ? "bg-red-100 border-red-500" : ""}`}
							>
								{pan} {isCorrect && "✔"} {isWrongPick && "✘"}
							</button>
						);
					})}
				</div>

				{pickedPan && (
					<>
						{pickedPan !== item.pan && (
							<p className="text-red-600 font-bold mb-2">Era: {item.pan}</p>
						)}
						<button onClick={continuar} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">
							{restantes > 0 ? `Siguiente (${restantes} más)` : "Servir"}
						</button>
					</>
				)}
			</div>
		</div>
	);
}
export default PanesChallenge;
