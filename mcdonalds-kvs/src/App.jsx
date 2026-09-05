import "./App.css";
import SideOnSpan from "./components/sideon";
import OrderCard from "./components/OrderCard";
import StatsPanel from "./components/StatsPanel";
import SelfCheckToast from "./components/SelfCheckToast";
import ModeBar from "./components/ModeBar";
import { WaveBanner, SessionReminder } from "./components/Banners";
import { actions } from "./lib/store"
import { recallVisibleS, computeFocusPool, PEEK_DURATION_MS, WAVE_MIN_MS, WAVE_MAX_MS, WAVE_BANNER_MS } from "./lib/memoria";
import { useEffect, useState, useRef } from "react";
import { useSelector, useDispatch } from "react-redux"

const AUTO_SPAWN_MIN_MS = 14000;
const AUTO_SPAWN_MAX_MS = 26000;

// Estándar oficial McDonald's (GE Iniciador/Ensamblador, Ago 2022)
const STANDARD_MIN_S = 35;
const STANDARD_MAX_S = 50;
const REACTION_STANDARD_S = 5; // reacción a la alarma del monitor

// Modo Turno Intensivo
const SHIFT_DURATION_MS = 120000; // 2 minutos
const SHIFT_SPAWN_MIN_MS = 5000;
const SHIFT_SPAWN_MAX_MS = 9000;

const SESSION_REMINDER_MS = 15 * 60 * 1000; // Método 2: repetición espaciada

function fmtAge(seconds) {
	const m = Math.floor(seconds / 60);
	const s = seconds % 60;
	return `${m}:${String(s).padStart(2, "0")}`;
}

function App() {
	const sideOn = useSelector((state) => state.sideOn)
	const orders = useSelector((state) => state.orders)
	const averageTime = useSelector((state) => state.mfyTime)
	const level = useSelector((state) => state.level)
	const memoriaOn = useSelector((state) => state.memoriaOn)
	const enfoqueOn = useSelector((state) => state.enfoqueOn)
	const confusion = useSelector((state) => state.confusion)

	const dispatch = useDispatch()
	const [, forceTick] = useState(0);

	// --- Turno Intensivo state ---
	const [shiftActive, setShiftActive] = useState(false);
	const [shiftEndsAt, setShiftEndsAt] = useState(null);
	const [, setServedTimes] = useState([]); // segundos por pedido servido durante el turno
	const [shiftSummary, setShiftSummary] = useState(null);
	const shiftSpawnRef = useRef(null);
	const shiftTimeoutRef = useRef(null);

	// --- Entrenamiento de memoria state (ver METODO-MEMORIA.md) ---
	const [peeking, setPeeking] = useState(false);
	const peekTimeoutRef = useRef(null);
	const [selfCheck, setSelfCheck] = useState(null);
	const selfCheckTimeoutRef = useRef(null);
	const [waveBanner, setWaveBanner] = useState(false);
	const sessionStartRef = useRef(Date.now());
	const [sessionReminder, setSessionReminder] = useState(false);
	const reminderShownRef = useRef(false);

	// refs "vivas" para que el listener de teclado (montado una sola vez)
	// siempre lea el estado más reciente y no quede pegado al de la primera renderización
	const ordersRef = useRef(orders);
	ordersRef.current = orders;
	const shiftActiveRef = useRef(shiftActive);
	shiftActiveRef.current = shiftActive;
	const memoriaOnRef = useRef(memoriaOn);
	memoriaOnRef.current = memoriaOn;
	const enfoqueOnRef = useRef(enfoqueOn);
	enfoqueOnRef.current = enfoqueOn;
	const levelRef = useRef(level);
	levelRef.current = level;
	const confusionRef = useRef(confusion);
	confusionRef.current = confusion;

	const toggleSide = () => {
		dispatch(actions.toggleSide())
	}
	const serveOrder = () => {
		const servedOrder = ordersRef.current[0]
		if (servedOrder === undefined) return;
		const timeServed = (Date.now()) / 1000 - servedOrder.timeGenerated
		dispatch(actions.setMfy(Math.floor(timeServed)))
		dispatch(actions.serveOrder())
		if (shiftActiveRef.current) {
			setServedTimes((prev) => [...prev, timeServed]);
		}
		if (memoriaOnRef.current || enfoqueOnRef.current) {
			const names = servedOrder.orderArray.map((it) => it.name);
			dispatch(actions.registerServed(names));
			setSelfCheck({ code: servedOrder.randomCode, items: servedOrder.orderArray, revealed: false });
			clearTimeout(selfCheckTimeoutRef.current);
			selfCheckTimeoutRef.current = setTimeout(() => setSelfCheck(null), 6000);
		}
	}
	const addOrder = () => {
		if (enfoqueOnRef.current) {
			dispatch(actions.pushFocusOrder(computeFocusPool(confusionRef.current)));
		} else {
			dispatch(actions.pushOrder())
		}
	}

	const startShift = () => {
		setServedTimes([]);
		setShiftSummary(null);
		setShiftActive(true);
		setShiftEndsAt(Date.now() + SHIFT_DURATION_MS);
	}

	const endShift = () => {
		setShiftActive(false);
		setShiftEndsAt(null);
		clearTimeout(shiftSpawnRef.current);
		setServedTimes((current) => {
			const n = current.length;
			const avg = n ? current.reduce((a, b) => a + b, 0) / n : 0;
			const dentroDeVentana = current.filter((t) => t >= STANDARD_MIN_S && t <= STANDARD_MAX_S).length;
			const masRapido = current.filter((t) => t < STANDARD_MIN_S).length;
			const masLento = current.filter((t) => t > STANDARD_MAX_S).length;
			setShiftSummary({
				total: n,
				avg,
				dentroDeVentana,
				masRapido,
				masLento,
			});
			return current;
		});
	}

	// Método 1 (recuperación activa): "espiar" muestra de nuevo lo tapado
	// por un instante — cada chequeo cuenta, para saber cuánto te apoyás en mirar.
	const peek = () => {
		if (!memoriaOnRef.current) return;
		const now = Date.now() / 1000;
		const visibleWindow = recallVisibleS(levelRef.current);
		const maskedNames = new Set();
		ordersRef.current.forEach((o) => {
			if (now - o.timeGenerated >= visibleWindow) {
				o.orderArray.forEach((it) => maskedNames.add(it.name));
			}
		});
		if (maskedNames.size > 0) {
			dispatch(actions.registerPeek(Array.from(maskedNames)));
		}
		setPeeking(true);
		clearTimeout(peekTimeoutRef.current);
		peekTimeoutRef.current = setTimeout(() => setPeeking(false), PEEK_DURATION_MS);
	}
	const toggleMemoria = () => dispatch(actions.toggleMemoria());
	const toggleEnfoque = () => dispatch(actions.toggleEnfoque());

	// Método 6 (efecto de generación): revelar/confirmar el autochequeo post-servido
	const revealSelfCheck = () => setSelfCheck((sc) => (sc ? { ...sc, revealed: true } : sc));
	const confirmSelfCheck = (missed) => {
		if (selfCheck && missed) {
			dispatch(actions.registerSelfMiss(selfCheck.items.map((it) => it.name)));
		}
		clearTimeout(selfCheckTimeoutRef.current);
		setSelfCheck(null);
	}
	const resetConfusionStats = () => dispatch(actions.resetConfusion());

	useEffect(() => {
		const handleKeypress = (event) => {
			if (event.key === "p") toggleSide();
			if (event.key === "Enter") serveOrder();
			if (event.key === "o") addOrder();
			if (event.key === "m") toggleMemoria();
			if (event.key === "f") toggleEnfoque();
			if (event.key === " ") { event.preventDefault(); peek(); }
		};
		window.addEventListener("keypress", handleKeypress);
		// reloj vivo para actualizar antigüedad en pantalla
		const clock = setInterval(() => forceTick((t) => t + 1), 1000);
		return () => {
			window.removeEventListener("keypress", handleKeypress);
			clearInterval(clock);
		};
		//eslint-disable-next-line
	}, [])

	// pedidos automáticos, todo el tiempo — se pausa mientras el turno intensivo está activo
	// para no duplicar la llegada de pedidos junto con el spawn rápido del turno
	useEffect(() => {
		if (shiftActive) return;
		let spawnTimeout;
		const scheduleSpawn = () => {
			const delay = AUTO_SPAWN_MIN_MS + Math.random() * (AUTO_SPAWN_MAX_MS - AUTO_SPAWN_MIN_MS);
			spawnTimeout = setTimeout(() => {
				if (enfoqueOnRef.current) {
					dispatch(actions.pushFocusOrder(computeFocusPool(confusionRef.current)));
				} else {
					dispatch(actions.pushOrder());
				}
				scheduleSpawn();
			}, delay);
		};
		scheduleSpawn();
		return () => clearTimeout(spawnTimeout);
		//eslint-disable-next-line
	}, [shiftActive])

	// spawn rápido + corte automático mientras el turno intensivo está activo
	useEffect(() => {
		if (!shiftActive) return;
		const scheduleShiftSpawn = () => {
			const delay = SHIFT_SPAWN_MIN_MS + Math.random() * (SHIFT_SPAWN_MAX_MS - SHIFT_SPAWN_MIN_MS);
			shiftSpawnRef.current = setTimeout(() => {
				if (enfoqueOnRef.current) {
					dispatch(actions.pushFocusOrder(computeFocusPool(confusionRef.current)));
				} else {
					dispatch(actions.pushOrder());
				}
				scheduleShiftSpawn();
			}, delay);
		};
		scheduleShiftSpawn();
		shiftTimeoutRef.current = setTimeout(() => {
			endShift();
		}, SHIFT_DURATION_MS);
		return () => {
			clearTimeout(shiftSpawnRef.current);
			clearTimeout(shiftTimeoutRef.current);
		};
		//eslint-disable-next-line
	}, [shiftActive])

	// Oleadas de pedidos extra ("salen muchos pedidos a la vez") mientras
	// algún modo de entrenamiento está activo, con cartel de aviso.
	useEffect(() => {
		if (!memoriaOn && !enfoqueOn) return;
		let waveTimeout;
		const scheduleWave = () => {
			const delay = WAVE_MIN_MS + Math.random() * (WAVE_MAX_MS - WAVE_MIN_MS);
			waveTimeout = setTimeout(() => {
				const n = 2 + Math.floor(Math.random() * 2);
				for (let i = 0; i < n; i++) {
					if (enfoqueOnRef.current) {
						dispatch(actions.pushFocusOrder(computeFocusPool(confusionRef.current)));
					} else {
						dispatch(actions.pushOrder());
					}
				}
				setWaveBanner(true);
				setTimeout(() => setWaveBanner(false), WAVE_BANNER_MS);
				scheduleWave();
			}, delay);
		};
		scheduleWave();
		return () => clearTimeout(waveTimeout);
		//eslint-disable-next-line
	}, [memoriaOn, enfoqueOn])

	// Método 2 (repetición espaciada): avisar cuando la sesión ya lleva rato largo
	useEffect(() => {
		const id = setInterval(() => {
			if (!reminderShownRef.current && Date.now() - sessionStartRef.current >= SESSION_REMINDER_MS) {
				reminderShownRef.current = true;
				setSessionReminder(true);
			}
		}, 30000);
		return () => clearInterval(id);
	}, []);

	const shiftRemainingS = shiftEndsAt ? Math.max(0, Math.ceil((shiftEndsAt - Date.now()) / 1000)) : 0;

	return (
		<>
			<div className="h-screen w-screen flex flex-col align-middle justify-between bg-black">
				<div className="flex flex-row items-center justify-between bg-neutral-900 px-4 py-2">
					{!shiftActive && (
						<button onClick={startShift} className="bg-yellow-400 text-black font-bold px-4 py-2 rounded">
							INICIAR TURNO INTENSIVO (2 min)
						</button>
					)}
					{shiftActive && (
						<span className="text-red-400 font-bold text-2xl">TURNO ACTIVO — {fmtAge(shiftRemainingS)}</span>
					)}
					<span className="text-white text-sm">Estándar oficial: {STANDARD_MIN_S}-{STANDARD_MAX_S}s por producto (GE Iniciador/Ensamblador)</span>
				</div>
				<ModeBar
					memoriaOn={memoriaOn}
					enfoqueOn={enfoqueOn}
					onToggleMemoria={toggleMemoria}
					onToggleEnfoque={toggleEnfoque}
					level={level}
				/>
				<div className="min-h-[80vh] flex flex-row flex-wrap content-start">
					{orders.map((orderObject, index) => {
						const ageSeconds = Math.max(0, Math.floor(Date.now() / 1000 - orderObject.timeGenerated));
						const masked = memoriaOn && !peeking && ageSeconds >= recallVisibleS(level);
						return (
							<OrderCard key={orderObject.id} order={orderObject} isFront={index === 0} masked={masked} />
						)
					})}
				</div >
				<footer className=" flex flex-row align-middle justify-between text-xl pr-2">
					<span className="text-black font-extrabold bg-gray-500 text-2xl">{new Date().toLocaleTimeString()}</span>
					<span className="text-white">Standard/MFY {SideOnSpan(sideOn)}</span>
					<span className="text-white">{averageTime} / 120</span>
				</footer>
			</div>

			{shiftSummary && (
				<div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
					<div className="bg-white rounded-lg p-8 w-[26rem] text-black">
						<h2 className="text-2xl font-bold mb-2">Resumen del turno</h2>
						<p className="mb-1">Pedidos servidos: <b>{shiftSummary.total}</b></p>
						<p className="mb-1">Tiempo promedio de bump: <b>{shiftSummary.avg.toFixed(1)}s</b></p>
						<p className="mb-1">Estándar oficial McDonald's: <b>{STANDARD_MIN_S}-{STANDARD_MAX_S}s</b> por producto</p>
						<hr className="my-3" />
						<p className="text-green-700">Dentro de la ventana estándar: <b>{shiftSummary.dentroDeVentana}</b></p>
						<p className="text-blue-700">Más rápido que el estándar: <b>{shiftSummary.masRapido}</b></p>
						<p className="text-red-700">Más lento que el estándar: <b>{shiftSummary.masLento}</b></p>
						<p className="mt-3 text-sm text-gray-600">
							Recordá: la reacción a la alarma del monitor tiene que ser en {REACTION_STANDARD_S}s o menos según la guía oficial (GE Iniciador/Ensamblador, Ago 2022).
						</p>
						<button onClick={() => setShiftSummary(null)} className="mt-4 bg-neutral-900 text-white font-bold px-4 py-2 rounded w-full">
							Cerrar
						</button>
					</div>
				</div>
			)}

			<WaveBanner show={waveBanner} />
			<SessionReminder show={sessionReminder} onDismiss={() => setSessionReminder(false)} />
			<SelfCheckToast data={selfCheck} onReveal={revealSelfCheck} onConfirm={confirmSelfCheck} />
			{(memoriaOn || enfoqueOn) && <StatsPanel onReset={resetConfusionStats} />}
		</>
	);
}

export default App;
