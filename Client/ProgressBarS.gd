extends ProgressBar


@onready var slider: HSlider = $"../HSlider"

# Called when the node enters the scene tree for the first time.
func _ready():
	slider.value_changed.connect(self.change)

func change(changed_value):
	self.set_value(changed_value)
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
