import { useSelector } from "react-redux";
import { topDifficultItems } from "../lib/memoria";

function StatsPanel({ onReset }) {
	const confusion = useSelector((state) => state.confusion);
	const top = topDifficultItems(confusion, 5);
	const totalPeeks = Object.values(confusion).reduce((a, s) => a + s.peeks, 0);
	const totalServed = Object.values(confusion).reduce((a, s) => a + s.served, 0);

	return (
		<div className="fixed bottom-2 left-2 z-40 bg-neutral-900/90 text-white text-xs rounded p-3 w-64 border border-neutral-700">
			<div className="flex flex-row justify-between items-center mb-1">
				<h2 className="font-bold text-sm">Tus ítems más difíciles</h2>
				<button onClick={onReset} className="text-neutral-400 hover:text-white underline">
					reiniciar
				</button>
			</div>
			{top.length === 0 && <p className="text-neutral-400">Todavía sin datos — jugá con Modo Memoria u Modo Enfoque prendido.</p>}
			<ol className="list-decimal list-inside space-y-0.5">
				{top.map((it) => (
					<li key={it.name}>
						{it.name}{" "}
						<span className="text-neutral-400">
							({it.peeks} espiadas, {it.selfMiss} autofallos, {it.served} servidos)
						</span>
					</li>
				))}
			</ol>
			<p className="mt-2 text-neutral-400">Espiadas totales: {totalPeeks} · Servidos en test: {totalServed}</p>
		</div>
	);
}
export default StatsPanel;
