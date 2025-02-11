#class_name NetworkManager 

extends Node
		
		
func authenticate_with_server():
	pass
	
func store_credentials():
	pass
	
func load_credentials():
	pass

func make_request(link: String):
	# Create a new request node
	var http_request := HTTPRequest.new()
	add_child(http_request)

	# invoke the reqest
	var error = http_request.request(
		link,
		["Content-Type: application/json"],
		HTTPClient.METHOD_GET)

	if error == OK:
		# wait for response
		var response = await http_request.request_completed
		http_request.queue_free()

		var result = response[0]
		var response_code = response[1]
		var _headers = response[2] # <-- not used
		var body: PackedByteArray = response[3]

		return body.get_string_from_utf8()
