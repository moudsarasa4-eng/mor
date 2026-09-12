import { useState, useEffect } from "react";

// Modo Estación: antes de servir, armá el producto de memoria —
// pan correcto + condimentos correctos — como en la estación real.
// Ver ESTACION-INICIADOR.md.
function EstacionChallenge({ challenge, onResolve, onSkip }) {
	const [pan, setPan] = useState(null);
	const [pasos, setPasos] = useState(new Set());
	const [resultado, setResultado] = useState(null);

	// El componente nunca se desmonta entre desafíos (challenge solo cambia
	// de un objeto a otro, o a null) — sin este reset, el segundo desafío
	// arrancaba mostrando el resultado del anterior en vez de la pantalla limpia.
	useEffect(() => {
		setPan(null);
		setPasos(new Set());
		setResultado(null);
	}, [challenge]);

	if (!challenge) return null;

	const togglePaso = (paso) => {
		if (resultado) return;
		setPasos((prev) => {
			const next = new Set(prev);
			if (next.has(paso)) next.delete(paso);
			else next.add(paso);
			return next;
		});
	};

	const confirmar = () => {
		const panOk = pan === challenge.pan;
		const pasosOk =
			pasos.size === challenge.pasosCorrectos.size &&
			[...pasos].every((p) => challenge.pasosCorrectos.has(p));
		setResultado({ panOk, pasosOk, huboError: !panOk || !pasosOk });
	};

	const continuar = () => {
		onResolve(Boolean(resultado && resultado.huboError));
	};

	return (
		<div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[30rem] text-black max-h-[90vh] overflow-y-auto">
				<h2 className="text-xl font-bold mb-1">Armá de memoria: {challenge.itemName}</h2>
				<p className="text-sm text-gray-600 mb-4">Elegí el pan y los pasos correctos antes de servir.</p>

				<h3 className="font-bold text-sm mb-1">Pan</h3>
				<div className="flex flex-col gap-1 mb-4">
					{challenge.panOpciones.map((p) => {
						const isCorrect = resultado && p === challenge.pan;
						const isWrongPick = resultado && p === pan && p !== challenge.pan;
						return (
							<button
								key={p}
								disabled={Boolean(resultado)}
								onClick={() => setPan(p)}
								className={`text-left px-3 py-2 rounded border-2 ${
									pan === p ? "border-blue-500" : "border-gray-200"
								} ${isCorrect ? "bg-green-100 border-green-500" : ""} ${isWrongPick ? "bg-red-100 border-red-500" : ""}`}
							>
								{p} {isCorrect && "✔"} {isWrongPick && "✘"}
							</button>
						);
					})}
				</div>

				<h3 className="font-bold text-sm mb-1">Condimentos y armado (elegí todos los que correspondan)</h3>
				<div className="flex flex-col gap-1 mb-4">
					{challenge.pasoOpciones.map((paso) => {
						const picked = pasos.has(paso);
						const isCorrectStep = challenge.pasosCorrectos.has(paso);
						const showCorrect = resultado && isCorrectStep;
						const showWrong = resultado && picked && !isCorrectStep;
						const showMissed = resultado && !picked && isCorrectStep;
						return (
							<button
								key={paso}
								disabled={Boolean(resultado)}
								onClick={() => togglePaso(paso)}
								className={`text-left px-3 py-2 rounded border-2 text-sm ${
									picked ? "border-blue-500" : "border-gray-200"
								} ${showCorrect ? "bg-green-100 border-green-500" : ""} ${showWrong ? "bg-red-100 border-red-500" : ""} ${
									showMissed ? "bg-yellow-100 border-yellow-500" : ""
								}`}
							>
								{picked ? "☑" : "☐"} {paso}
								{showCorrect && !showWrong && " ✔"}
								{showWrong && " ✘"}
								{showMissed && " (te lo perdiste)"}
							</button>
						);
					})}
				</div>

				{!resultado ? (
					<div className="flex flex-row gap-2">
						<button onClick={confirmar} disabled={!pan} className="flex-1 bg-blue-500 disabled:bg-gray-300 text-white font-bold px-3 py-2 rounded">
							Confirmar armado
						</button>
						<button onClick={onSkip} className="text-gray-500 underline px-3 py-2">
							Saltar
						</button>
					</div>
				) : (
					<div>
						<p className={`font-bold mb-2 ${resultado.huboError ? "text-red-600" : "text-green-700"}`}>
							{resultado.huboError ? "Casi — repasalo antes del próximo." : "¡Perfecto, así se arma en la vida real!"}
						</p>
						<button onClick={continuar} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded">
							Servir
						</button>
					</div>
				)}
			</div>
		</div>
	);
}
export default EstacionChallenge;
