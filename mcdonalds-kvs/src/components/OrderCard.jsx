import { iconFor } from "../lib/icons";

function fmtAge(seconds) {
	const m = Math.floor(seconds / 60);
	const s = seconds % 60;
	return `${m}:${String(s).padStart(2, "0")}`;
}

function OrderCard({ order, ageSeconds, colors, masked }) {
	return (
		<div className={`border-[6px] ${colors.border} flex flex-col flex-wrap align-top bg-white w-[20rem] m-2 h-min`}>
			<div className="bg-neutral-900 text-white font-bold text-lg flex flex-row align-middle justify-between px-4 py-1">
				<h1>{order.orderType}</h1>
				<h1>AGE {fmtAge(ageSeconds)}</h1>
				<h1>{order.randomCode}</h1>
			</div>
			{masked && (
				<div className="bg-yellow-500 text-black text-xs font-extrabold text-center py-0.5 tracking-wide">
					🔒 RECORDALO — mantené Espacio para chequear
				</div>
			)}
			{masked ? (
				<div className="px-5 py-2 flex flex-col gap-1.5">
					{order.orderArray.map((_, i) => (
						<div
							key={i}
							className="h-5 rounded bg-neutral-300 animate-pulse"
							style={{ width: `${55 + ((i * 13) % 35)}%` }}
						/>
					))}
				</div>
			) : (
				order.orderArray.map((orderList, i) => (
					<div key={i} className="px-5 py-0.5">
						<span className="text-xl font-bold text-black">
							<span className="inline-block w-5">{orderList.amount}</span> {iconFor(orderList.name)} {orderList.name}
						</span>
						{orderList.modifier && (
							<div className={`text-sm font-semibold ml-6 ${orderList.modifier.prefix === "SIN" ? "text-red-600" : "text-green-700"}`}>
								{orderList.modifier.prefix} <span className="text-black">{orderList.modifier.ing}</span>
							</div>
						)}
					</div>
				))
			)}
			<div className={`${colors.bar} text-black font-bold text-lg px-3 flex flex-row align-middle justify-between mt-1`}>
				<h1>{order.orderStorage}</h1>
				<h1>{order.randomTime}</h1>
			</div>
		</div>
	);
}
export default OrderCard;
