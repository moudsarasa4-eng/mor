// Banco de preguntas verificadas contra la Guía de Entrenamiento oficial
// "Opciones para Celíacos — Área de Producción" (Octubre 2021). Cada
// pregunta cita textualmente de dónde sale para poder auditarla contra la
// guía real si algo cambió desde entonces.
//
// La lista de ingredientes SIN TACC (y en particular qué está
// "suspendido") es la parte más propensa a quedar vieja con el tiempo —
// se marca explícitamente en la pregunta que corresponde.
const CELIACOS_PREGUNTAS = [
	{
		pregunta: "¿Quién puede preparar un menú con ingredientes SIN TACC?",
		opciones: ["Exclusivamente un Gerente", "Cualquier miembro del crew", "El crew de parrilla", "El Iniciador de turno"],
		correcta: "Exclusivamente un Gerente",
		fuente: "\"Los menús con ingredientes SIN TACC deben ser preparados EXCLUSIVAMENTE por un Gerente en la mesa de preparación de alimentos, en el momento que el cliente lo solicita.\"",
	},
	{
		pregunta: "Un cliente pide un menú SIN TACC. Después de registrar el pedido, ¿qué hay que seleccionar?",
		opciones: ["\"Agregar Extra\" y después \"Trade Up Pan Celíaco\"", "\"SIN Cebolla\"", "\"Modificar producto\"", "Nada, se registra como cualquier otro pedido"],
		correcta: "\"Agregar Extra\" y después \"Trade Up Pan Celíaco\"",
		fuente: "\"Registrar el pedido con la tecla correspondiente... seleccionar la tecla 'Agregar Extra' y a continuación, 'Trade Up Pan Celíaco'.\"",
	},
	{
		pregunta: "¿Se puede usar la lechuga, la cebolla o el tomate de la mesa de condimentación para un pedido SIN TACC?",
		opciones: ["No, nunca", "Sí, si están frescos", "Sí, solo la lechuga"],
		correcta: "No, nunca",
		fuente: "\"NO SE DEBEN UTILIZAR LOS INGREDIENTES DE LA MESA DE CONDIMENTACIÓN\" / \"NO SE PUEDE UTILIZAR LA LECHUGA, LA CEBOLLA NI LOS TOMATES DE LA MESA DE CONDIMENTACIÓN.\"",
	},
	{
		pregunta: "¿Dónde se debe cocinar la carne de un pedido SIN TACC?",
		opciones: [
			"Solo en una parrilla sin contacto previo con tostados, marcada con sticker rojo",
			"En cualquier parrilla disponible en ese momento",
			"En la misma parrilla que los tostados, pero después de limpiarla",
		],
		correcta: "Solo en una parrilla sin contacto previo con tostados, marcada con sticker rojo",
		fuente: "\"Se deberá identificar una placa de la parrilla exclusivamente para cocinar los tostados con un sticker rojo... La carne se debe cocinar únicamente en las parrillas que no hayan tenido contacto con tostados antes y se debe utilizar el segundo juego de utensilios.\"",
	},
	{
		pregunta: "¿Cuánto tarda en descongelarse el pan celíaco a temperatura ambiente?",
		opciones: ["2 horas", "30 minutos", "24 horas", "72 horas"],
		correcta: "2 horas",
		fuente: "\"Tiempo de descongelado: 2 horas a temperatura ambiente.\"",
	},
	{
		pregunta: "Una vez descongelado a temperatura ambiente, ¿en cuánto tiempo vence el pan celíaco?",
		opciones: ["72 horas", "2 horas", "3 meses", "1 semana"],
		correcta: "72 horas",
		fuente: "\"Vencimiento secundario: 72hs. a temperatura ambiente (colocar el sticker en el dorso de la bolsa).\"",
	},
	{
		pregunta: "¿Se le puede cobrar al cliente un adicional por el agua en un menú SIN TACC?",
		opciones: ["No", "Sí, es un producto aparte"],
		correcta: "No",
		fuente: "\"No cobrar un adicional por agua.\"",
	},
	{
		pregunta: "Según la guía de Octubre 2021, ¿cuál de estos ingredientes SIN TACC figuraba SUSPENDIDO? (esto puede haber cambiado desde entonces)",
		opciones: ["Queso Cheddar amarillo", "Carne 10:1", "Lechuga", "Papas fritas sin salar"],
		correcta: "Queso Cheddar amarillo",
		fuente: "Listado de ingredientes SIN TACC, con \"Queso Cheddar amarillo\" marcado \"SUSPENDIDO\" en esa guía puntual — confirmá el estado actual antes de asumir que sigue igual.",
	},
];

export default CELIACOS_PREGUNTAS;
