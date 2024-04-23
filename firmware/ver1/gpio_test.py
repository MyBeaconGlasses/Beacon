from gpiozero import Button

button = Button(2)
while True:
	print(button.is_pressed)

