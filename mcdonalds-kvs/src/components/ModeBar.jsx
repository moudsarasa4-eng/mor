import { recallVisibleS } from "../lib/memoria";

function ModeBar({
	memoriaOn,
	enfoqueOn,
	estacionOn,
	panesOn,
	onToggleMemoria,
	onToggleEnfoque,
	onToggleEstacion,
	onTogglePanes,
	level,
}) {
	const handleClick = (fn) => (event) => {
		event.currentTarget.blur();
		fn();
	};

	return (
		<div className="flex flex-row items-center justify-between bg-neutral-800 px-4 py-1 text-xs text-gray-300">
			<div className="flex flex-row gap-2">
				<button
					onClick={handleClick(onToggleMemoria)}
					className={`px-3 py-1 rounded font-bold ${memoriaOn ? "bg-blue-500 text-white" : "bg-neutral-700"}`}
				>
					Modo Memoria (M): {memoriaOn ? "ON" : "OFF"}
				</button>
				<button
					onClick={handleClick(onToggleEnfoque)}
					className={`px-3 py-1 rounded font-bold ${enfoqueOn ? "bg-purple-500 text-white" : "bg-neutral-700"}`}
				>
					Modo Enfoque (F): {enfoqueOn ? "ON" : "OFF"}
				</button>
				<button
					onClick={handleClick(onToggleEstacion)}
					className={`px-3 py-1 rounded font-bold ${estacionOn ? "bg-orange-500 text-white" : "bg-neutral-700"}`}
				>
					Modo Estación (E): {estacionOn ? "ON" : "OFF"}
				</button>
				<button
					onClick={handleClick(onTogglePanes)}
					className={`px-3 py-1 rounded font-bold ${panesOn ? "bg-amber-600 text-white" : "bg-neutral-700"}`}
				>
					Modo Panes (B): {panesOn ? "ON" : "OFF"}
				</button>
			</div>
			<div className="flex flex-row gap-3">
				{memoriaOn && <span>Se tapa a los {recallVisibleS(level).toFixed(1)}s · Espacio = chequear</span>}
				{enfoqueOn && <span>Practicando tus ítems más difíciles</span>}
				{estacionOn && <span>Armá el pan y los condimentos antes de servir</span>}
				{panesOn && <span>Elegí el pan de cada producto antes de servir</span>}
			</div>
		</div>
	);
}
export default ModeBar;
