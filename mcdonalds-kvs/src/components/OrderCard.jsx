import { Fragment } from "react";

function OrderCard({ order, isFront, masked }) {
	return (
		<div className={`${isFront ? "border-[6px] border-green-400 " : ""}flex flex-col flex-wrap align-top bg-white w-[20rem] m-2 h-min`}>
			<div className="bg-purple-900 text-white font-bold text-xl flex flex-row align-middle justify-between px-5">
				<h1>Side →</h1>
				<h1>{order.orderType}</h1>
				<h1>{order.randomCode}</h1>
			</div>
			{masked && (
				<div className="bg-yellow-500 text-black text-xs font-extrabold text-center py-0.5 tracking-wide">
					RECORDALO — mantené Espacio para chequear
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
					<Fragment key={i}>
						<span className="text-xl font-semibold px-5">
							<span>{orderList.amount}</span>  {orderList.name}
						</span>
						{orderList.modifier && (
							<div className={`text-sm font-semibold px-5 ml-6 ${orderList.modifier.prefix === "SIN" ? "text-red-600" : "text-green-700"}`}>
								{orderList.modifier.prefix} <span className="text-black">{orderList.modifier.ing}</span>
							</div>
						)}
					</Fragment>
				))
			)}
			<div className="bg-red-400 text-white font-bold text-xl px-2 flex flex-row align-middle justify-between">
				<h1>{order.orderStorage}</h1>
				<h1>{order.randomTime}</h1>
			</div>
		</div>
	);
}
export default OrderCard;
