simple_css = """
.card {
	font-family: arial;
	font-size: 20px;
	text-align: center;
	color: black;
	background-color: white;
}

.card.night_mode {
	color: white;
	background-color: #1f1f1f;
}


.ch_pin {
	font-size: 16px;
}

.ch_trad {
}

.ch_mean {
}

.ch_sim {
	font-size: 30px;
	font-weight: bold;
}

.ch_sen {
	text-align: center;
}

.ch_sen_sim {
	font-size: 2.2rem;
	display: inline;
}

.ch_sen_trad {
	font-size: 1.8rem;
}

.ch_sen_pin {
	font-size: 1rem;
}

.ch_sen_tr {
	font-size: 1.5rem;
}
"""


colorful_css = """
.card {
	--pinyin-color: #ef6c00;
	--simplified-color: #6495ed;
	--traditional-color: #00796b;
	--meaning-color: #607d8b;
	--sen-sim-color: #fba910;
	--sen-trad-color: #00796b;
	--sen-pin-color: #263238;
	--sen-tr-color: #29b6f6;
	font-family: arial;
	font-size: 20px;
	text-align: center;
	color: black;
	background-color: white;
}

.card.night_mode {
	--pinyin-color: #27b46e;
	--simplified-color: #6495ed;
	--traditional-color: #fba910;
	--meaning-color: #29b6f6;
	--sen-sim-color: #fba910;
	--sen-trad-color: #6495ed;
	--sen-pin-color: #27b46e;
	--sen-tr-color: #6495ed;
	color: white;
	background-color: #1f1f1f;
}

.ch_pin {
	font-size: 16px;
	color: var(--pinyin-color);
}

.ch_trad {
	color: var(--traditional-color);
}

.ch_mean {
	color: var(--meaning-color);
}

.ch_sim {
	font-size: 30px;
	font-weight: bold;
	color: var(--simplified-color);
}

.ch_sen {
	text-align: center;
}

.ch_sen_sim {
	color: var(--sen-sim-color);
	font-size: 2.2rem;
	display: inline;
}

.ch_sen_trad {
	color: var(--sen-trad-color);
	font-size: 1.8rem;
}

.ch_sen_pin {
	color: var(--sen-pin-color);
	font-size: 1rem;
}

.ch_sen_tr {
	color: var(--sen-tr-color);
	font-size: 1.5rem;
}

.replay-button svg circle {
	fill: #4CAF50;
	stroke: #4CAF50;
}

.replay-button svg path {
	fill: #fff;
	stroke: #4CAF50;
	stroke-width: 4px;
}

.replay-button svg {
	width: 30px;
	height: 30px;
}
"""
