// Efecto de generación (Método 6): después de servir, recordar de memoria
// lo que tenía el pedido (sin mirar) fija mejor que releerlo.
function SelfCheckToast({ data, onReveal, onConfirm }) {
	if (!data) return null;
	return (
		<div className="fixed bottom-2 right-2 z-40 bg-white text-black rounded-lg shadow-xl p-4 w-72 border-4 border-blue-500">
			<p className="font-bold mb-1">Recién serviste {data.code}.</p>
			<p className="text-sm mb-2">Antes de que llegue el próximo: decí en voz alta qué tenía.</p>
			{!data.revealed ? (
				<button onClick={onReveal} className="bg-blue-500 text-white font-bold px-3 py-1 rounded w-full">
					Ya lo dije — revelar
				</button>
			) : (
				<>
					<ul className="text-sm mb-2 list-disc list-inside">
						{data.items.map((it, i) => (
							<li key={i}>
								{it.amount} {it.name}
								{it.modifier && ` (${it.modifier.prefix} ${it.modifier.ing})`}
							</li>
						))}
					</ul>
					<div className="flex flex-row gap-2">
						<button onClick={() => onConfirm(false)} className="flex-1 bg-green-600 text-white font-bold px-2 py-1 rounded">
							Lo sabía ✔
						</button>
						<button onClick={() => onConfirm(true)} className="flex-1 bg-red-600 text-white font-bold px-2 py-1 rounded">
							Me fallé ✘
						</button>
					</div>
				</>
			)}
		</div>
	);
}
export default SelfCheckToast;
