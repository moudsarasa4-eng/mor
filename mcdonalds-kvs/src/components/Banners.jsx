export function WaveBanner({ show }) {
	if (!show) return null;
	return (
		<div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-red-600 text-white font-extrabold text-2xl px-6 py-2 rounded-full shadow-xl animate-pulse">
			⚠ OLEADA DE PEDIDOS ⚠
		</div>
	);
}

export function SessionReminder({ show, onDismiss }) {
	if (!show) return null;
	return (
		<div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-yellow-400 text-black rounded-lg shadow-xl p-3 w-[28rem] text-sm">
			<p className="font-bold mb-1">Llevás 15 minutos seguidos.</p>
			<p className="mb-2">
				La repetición espaciada (sesiones cortas y frecuentes) memoriza mejor que una sesión larga. Considerá cortar acá y volver más tarde.
			</p>
			<button onClick={onDismiss} className="bg-black text-white px-3 py-1 rounded font-bold">
				Seguir igual
			</button>
		</div>
	);
}
