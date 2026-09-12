// Tutorial de uso: qué hace cada sección y con qué tecla se abre. Se
// muestra solo (una vez) la primera vez que se abre el archivo, y queda
// disponible siempre con el botón "AYUDA" o la tecla "?".
const SECCIONES = [
	{
		titulo: "Controles básicos",
		texto: "P activa/desactiva Side. Enter sirve el pedido de adelante. O agrega un pedido manual a la cola. Espacio solo hace algo con Modo Memoria activo (ver abajo).",
	},
	{
		titulo: "INICIAR TURNO INTENSIVO",
		texto: "Ráfaga de 2 minutos con pedidos mucho más seguidos, para simular una hora pico real. Al terminar te muestra un resumen contra el estándar oficial (35-50s por producto, GE Iniciador/Ensamblador).",
	},
	{
		titulo: "Modo Memoria (M)",
		texto: "Cada pedido se tapa solo después de un tiempo que se achica a medida que subís de nivel — te obliga a memorizar en vez de releer. Mantené Espacio para espiar todo lo tapado 1.5s (con 4s de enfriamiento entre espiadas).",
	},
	{
		titulo: "Modo Enfoque (F)",
		texto: "Los pedidos nuevos salen de tus propios puntos débiles — lo que más espiaste o fallaste — en vez de ser 100% al azar. Se combina con Modo Memoria.",
	},
	{
		titulo: "Modo Estación (E)",
		texto: "Antes de servir un producto con receta real confirmada en la guía oficial, tenés que armar de memoria el pan y los condimentos correctos, mezclados con opciones falsas.",
	},
	{
		titulo: "Modo Panes (B)",
		texto: "Versión más liviana que Estación: antes de servir, elegís solo el tipo de pan de cada producto (sin condimentos), y cubre todo el menú. No repregunta un producto que ya cubrió Estación en el mismo servido.",
	},
	{
		titulo: "Cronómetro: memorizar + pan (C)",
		texto: "Práctica libre e infinita, aislada de la cola de pedidos: un producto a la vez, lo ves 2 segundos, se tapa, y elegís su pan de memoria contra un objetivo de 5 segundos. Guarda tu mejor tiempo.",
	},
	{
		titulo: "Tomar Evaluación (V)",
		texto: "Examen formal de 10 preguntas, no práctica libre: 7 son el mismo desafío de Cronómetro y 3 son de procedimiento para pedidos de celíacos (SIN TACC). Termina con una nota y aprobado/no aprobado, y guarda tu historial.",
	},
	{
		titulo: "Reconocimiento Visual (R)",
		texto: "Entrena la memoria visual del ticket en sí, no el contenido: lo mirás un instante (con el mismo diseño real), se tapa, y te pregunto si un producto estaba o si algo cambió al mostrártelo de nuevo.",
	},
	{
		titulo: "Cronómetro, Evaluación y Reconocimiento Visual",
		texto: "Son pantallas aisladas que no tocan la cola de pedidos: solo puede haber una abierta a la vez, y mientras cualquiera de las tres (o esta ayuda) está abierta, el resto de las teclas no hace nada de fondo.",
	},
];

function AyudaModal({ open, onClose }) {
	if (!open) return null;
	return (
		<div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
			<div className="bg-white rounded-lg p-6 w-[34rem] text-black max-h-[90vh] overflow-y-auto">
				<div className="flex flex-row justify-between items-center mb-3">
					<h2 className="text-xl font-bold">Cómo se usa cada sección</h2>
					<button onClick={onClose} className="text-gray-400 underline text-sm">cerrar (?)</button>
				</div>
				<div className="flex flex-col gap-3">
					{SECCIONES.map((s) => (
						<div key={s.titulo}>
							<h3 className="font-bold text-sm">{s.titulo}</h3>
							<p className="text-sm text-gray-700">{s.texto}</p>
						</div>
					))}
				</div>
				<button onClick={onClose} className="w-full bg-neutral-900 text-white font-bold px-3 py-2 rounded mt-4">
					Entendido
				</button>
			</div>
		</div>
	);
}
export default AyudaModal;
