extends Node2D

# The URL we will connect to.
@export var websocket_url = "ws://127.0.0.1:8080/?token=player_2131"

# Our WebSocketClient instance.
var socket = WebSocketPeer.new()
var rng = RandomNumberGenerator.new()
@export var console: RichTextLabel
@export var BalanceLabel: Label
@export var EnergyLabel: Label
@export var PurchaseButton: Button

var balance: int = 0
var energy: int = 0
var max_energy: int = 0
var UI_DIRTY: bool = false

func _ready():
	
	PurchaseButton.pressed.connect(self.purchase_made)
	await establish_connection()
		
func establish_connection():
	# websocket_url = websocket_url.format({"ID": rng.randi_range(10, 100000)})
	# Initiate connection to the given URL.
	var err = socket.connect_to_url(websocket_url)
	if err != OK:
		console.add_text("Unable to connect")
		set_process(false)
	else:
		# Wait for the socket to connect.
		await get_tree().create_timer(2).timeout

func NOTIFY_BALANCE_UPDATE(balance: int, energy: int):
	socket.send_text(JSON.stringify({"type": "BALANCE", "playerId": 2131, "payload": {"balance": balance, "energy": energy}}))


func purchase_made():
	
	if balance >= 10:
		balance -= 10
		UI_DIRTY = true
		NOTIFY_BALANCE_UPDATE(balance, energy)
		

func UPDATE_DYANMIC_UI():
	BalanceLabel.text = "🪙 %d" % [balance]
	EnergyLabel.text = "🔋 %d/%d" % [energy, max_energy]

func _process(_delta):
	
	if UI_DIRTY:
		UPDATE_DYANMIC_UI()
		UI_DIRTY = false
		
	if balance <= 10:
		PurchaseButton.disabled = true
	else:
		PurchaseButton.disabled = false
	
	# Call this in _process or _physics_process. Data transfer and state updates
	# will only happen when calling this function.
	socket.poll()

	# get_ready_state() tells you what state the socket is in.
	var state = socket.get_ready_state()

	# WebSocketPeer.STATE_OPEN means the socket is connected and ready
	# to send and receive data.
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var recieved_text = socket.get_packet().get_string_from_utf8()
			console.text += "Got data from server: " + recieved_text + "\n"
			var data = JSON.parse_string(recieved_text)
			if data["type"] == "BALANCE":
				UI_DIRTY = true
				balance = data["payload"].balance
				energy = data["payload"].energy
				max_energy = data["payload"].maxEnergy
			elif data["type"] == "SERVER_EVENT":
				if data["payload"].type == "balance_add":
					balance += data["payload"].amount
					UI_DIRTY = true

	# WebSocketPeer.STATE_CLOSING means the socket is closing.
	# It is important to keep polling for a clean close.
	elif state == WebSocketPeer.STATE_CLOSING:
		console.add_text("CONNECTION CLOSED")
		while socket.get_available_packet_count():
			console.text += "Got data from server: " + socket.get_packet().get_string_from_utf8() + "\n"
		pass

	# WebSocketPeer.STATE_CLOSED means the connection has fully closed.
	# It is now safe to stop polling.
	elif state == WebSocketPeer.STATE_CLOSED:
		# The code will be -1 if the disconnection was not properly notified by the remote peer.
		
		var code = socket.get_close_code()

		console.add_text("WebSocket closed with code: %d. Clean: %s. Attempting to reconnect" % [code, code != -1])
		establish_connection()
		
	if console.get_line_count() > 100:
		console.text = ""
